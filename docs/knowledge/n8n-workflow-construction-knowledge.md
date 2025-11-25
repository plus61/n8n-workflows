# n8nワークフロー構築ナレッジベース

**作成日**: 2025-10-29
**最終更新**: 2025-11-24
**出典**: WF6 (note記事自動生成), WF7 (SNS動画生成パイプライン), WF-B (AI Agent分析パイプライン) 構築・テスト・トラブルシューティング実行から得られた知見

## 目次

1. [HTTP Request Node v4 設定ルール](#1-http-request-node-v4-設定ルール)
2. [n8n式構文のベストプラクティス](#2-n8n式構文のベストプラクティス)
3. [ノード参照とデータアクセス](#3-ノード参照とデータアクセス)
4. [ワークフロー更新戦略](#4-ワークフロー更新戦略)
5. [テストとデバッグアプローチ](#5-テストとデバッグアプローチ)
6. [Notion API統合](#6-notion-api統合)
7. [Webhook設計パターンとRailway制限](#7-webhook設計パターンとrailway制限)
8. [Execute Command ノードのベストプラクティス](#8-execute-command-ノードのベストプラクティス)
9. [チェックリスト](#9-チェックリスト)
10. [AI Agent + JSON出力パイプライン](#10-ai-agent--json出力パイプライン)
11. [Google Sheets ノード制約事項](#11-google-sheets-ノード制約事項)
12. [n8n MCP API 使用時の注意事項](#12-n8n-mcp-api-使用時の注意事項)

---

## 1. HTTP Request Node v4 設定ルール

### 🚨 Critical: specifyBody パラメータの正しい使い方

#### ルール1: n8n式構文 `={{ }}` を使う場合は必ず `specifyBody: "json"` を使用

**❌ 間違った設定** (式が評価されない):
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/endpoint",
    "sendBody": true,
    "contentType": "json",
    "specifyBody": "string",
    "body": "={{ JSON.stringify({ key: $('PreviousNode').first().json.value }) }}"
  }
}
```

**問題点**:
- `specifyBody: "string"` は `body` パラメータ内の `={{ }}` 式を**評価しない**
- 式がリテラル文字列として送信される
- 結果: API側でJSON parse errorまたはvalidation errorが発生

**✅ 正しい設定** (式が評価される):
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/endpoint",
    "sendBody": true,
    "contentType": "json",
    "specifyBody": "json",
    "jsonBody": "={{ { key: $('PreviousNode').first().json.value } }}"
  }
}
```

**正しい動作**:
- `specifyBody: "json"` + `jsonBody` パラメータで式を評価
- `={{ }}` 内のJavaScript式が実行される
- 結果: 正しいJSON objectがAPIに送信される

#### ルール2: データ型別の正しい式構文

| データ型 | 正しい構文 | 誤った構文 | 理由 |
|---------|-----------|-----------|------|
| **String** | `" + $json.stringField + "` | `" + JSON.stringify($json.stringField) + "` | JSON.stringify()は二重引用符をエスケープ |
| **Number** | `" + $json.numberField + "` | `"\"field\": \" + $json.numberField + \"\""` | JSONで数値に引用符は不要 |
| **Boolean** | `" + $json.boolField + "` | `" + $json.boolField.toString() + "` | 自動的に文字列変換される |
| **Array/Object** | `" + JSON.stringify($json.arrayField) + "` | `" + $json.arrayField + "` | 配列/オブジェクトはJSON.stringify必須 |
| **ISO Date** | `" + JSON.stringify(new Date().toISOString()) + "` | `" + new Date().toISOString() + "` | 文字列として扱う場合は引用符が必要 |
| **null** | `null` | `"null"` | nullは文字列ではなくnull値として送信 |

#### 実際のエラー事例（WF6 Node 8）

**Execution 816 失敗ログ**:
```json
// 送信されたリクエストボディ（誤り）
{
  "{\"parent\":{\"database_id\":\"29968d5c298681ad90d0c24ed710503e\"},\"properties\":{...}}": ""
}

// Notion APIエラー
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "body.{...} should be not present, instead was `\"\"`."
}
```

**修正後（Execution 823成功）**:
```json
// 正しく送信されたリクエストボディ
{
  "parent": {
    "database_id": "29968d5c298681ad90d0c24ed710503e"
  },
  "properties": {
    "Title": {
      "title": [{"text": {"content": "安全で子どもが喜ぶ！渋谷のカフェ＆レストラン完全ガイド"}}]
    }
  }
}
```

### 教訓とベストプラクティス

1. **必須パラメータチェック**: ワークフロー構築時に `specifyBody` パラメータが正しく設定されているか確認
2. **式構文の検証**: `={{ }}` を使う場合は必ず `specifyBody: "json"` + `jsonBody` の組み合わせ
3. **データフローシミュレーション**: テスト前に各ノードのパラメータを目視確認
4. **段階的テスト**: 新しいHTTP Requestノードは単体で先にテスト実行

---

## 2. n8n式構文のベストプラクティス

### 基本構文ルール

#### 式の基本形式

```javascript
// ✅ 正しい: Expression内でのJavaScript実行
={{ $('NodeName').first().json.propertyName }}

// ✅ 正しい: 複雑な変換処理
={{ $('NodeName').first().json.items.map(item => item.name).join(', ') }}

// ✅ 正しい: 条件分岐
={{ $('NodeName').first().json.status === 'active' ? 'はい' : 'いいえ' }}

// ❌ 間違い: 式の外側で引用符を使用
"={{ $('NodeName').first().json.propertyName }}"  // これはリテラル文字列として扱われる
```

### JSONボディ構築の正しい方法

#### パターン1: シンプルなオブジェクト

```javascript
// ✅ 正しい: jsonBodyでオブジェクト構築
jsonBody: "={{ {
  title: $('Prepare Data').first().json.title,
  body: $('Prepare Data').first().json.body,
  status: 'draft'
} }}"
```

#### パターン2: ネストされた構造

```javascript
// ✅ 正しい: ネストされたオブジェクト
jsonBody: "={{ {
  parent: {
    database_id: '29968d5c298681ad90d0c24ed710503e'
  },
  properties: {
    Title: {
      title: [{
        text: {
          content: $('Prepare Data').first().json.title
        }
      }]
    }
  }
} }}"
```

#### パターン3: 配列マッピング

```javascript
// ✅ 正しい: 配列を別の形式にマッピング
jsonBody: "={{ {
  categories: $('Prepare Data').first().json.categories.map(c => ({ name: c }))
} }}"

// ✅ 正しい: 配列のフィルタリングとマッピング
jsonBody: "={{ {
  activeItems: $('Source').first().json.items
    .filter(item => item.status === 'active')
    .map(item => ({
      id: item.id,
      name: item.name
    }))
} }}"
```

### 文字列連結の罠を避ける

#### ❌ 避けるべきパターン

```javascript
// ❌ 間違い: JSON.stringify()でstring値をエスケープ
"content": " + JSON.stringify($json.topic) + "
// 結果: "content": "\"子供向けカフェガイド\""  ← 不要なエスケープ

// ❌ 間違い: 手動で引用符を追加
"content": "\"" + $json.topic + "\""
// 結果: JSON構文エラーの可能性
```

#### ✅ 正しいパターン

```javascript
// ✅ 正しい: string値は直接使用
"content": " + $json.topic + "
// 結果: "content": "子供向けカフェガイド"

// ✅ 正しい: オブジェクト全体をJSON.stringify
" + JSON.stringify({ content: $json.topic }) + "
// 結果: {"content": "子供向けカフェガイド"}
```

---

## 3. ノード参照とデータアクセス

### ノード名の正確な参照

#### 🚨 Critical: ノード名は完全一致必須

**❌ 間違った参照** (Execution 817エラー):
```javascript
// ノード名: "Select Topic"
// 参照: $('Get Random Topics')  ← 存在しないノード名
{
  "error": "Referenced node doesn't exist: \"Get Random Topics\""
}
```

**✅ 正しい参照**:
```javascript
// ノード名: "Select Topic"
// 参照: $('Select Topic')  ← 正確なノード名
$('Select Topic').first().json.topicName
```

### プロパティアクセスの検証

#### ベストプラクティス: データ構造の事前確認

1. **前のノードの出力を確認**:
```javascript
// ノードの実行結果を確認
{
  "json": {
    "topicId": "xxx",
    "topicName": "英語学童選びのポイント",  // ← 正しいプロパティ名
    "score": 85
  }
}
```

2. **正しいプロパティ名を使用**:
```javascript
// ✅ 正しい
$('Select Topic').first().json.topicName

// ❌ 間違い
$('Select Topic').first().json.topic  // プロパティ名が違う
```

### データアクセスパターン

#### パターン1: 単一アイテムへのアクセス

```javascript
// ✅ 推奨: .first() を使用
$('NodeName').first().json.propertyName

// ⚠️ 注意: [0] も動作するが .first() が推奨
$('NodeName').item[0].json.propertyName
```

#### パターン2: 全アイテムのループ処理

```javascript
// ✅ 正しい: 全アイテムをマッピング
$('NodeName').all().map(item => item.json.propertyName)

// ✅ 正しい: フィルタリングとマッピング
$('NodeName').all()
  .filter(item => item.json.status === 'active')
  .map(item => item.json.name)
```

#### パターン3: ネストされたプロパティ

```javascript
// ✅ 正しい: ネストされたプロパティへのアクセス
$('Notion Query').first().json.results[0].properties.Title.title[0].plain_text

// ✅ 正しい: Optional chaining（存在チェック）
$('Notion Query').first().json.results?.[0]?.properties?.Title?.title?.[0]?.plain_text || 'デフォルト値'
```

---

## 4. ワークフロー更新戦略

### 部分更新 vs 完全更新

#### 🚨 Critical: 部分更新のリスク（Execution 822エラー）

**❌ 危険な部分更新** (必須パラメータが欠落):
```javascript
// 操作: Node 9の jsonBody のみ更新
n8n_update_partial_workflow({
  operations: [{
    type: "updateNode",
    nodeId: "...",
    updates: {
      parameters: {
        jsonBody: "={{ {...} }}"  // ← これだけ更新
      }
    }
  }]
})

// 結果: method, url, sendHeaders等の必須パラメータが消失
// エラー: "The workflow has issues and cannot be executed"
```

**✅ 安全な完全更新**:
```javascript
n8n_update_partial_workflow({
  operations: [{
    type: "updateNode",
    nodeId: "...",
    updates: {
      parameters: {
        method: "POST",  // ← 全パラメータを含める
        url: "https://...",
        sendHeaders: true,
        headerParameters: {...},
        sendBody: true,
        contentType: "json",
        specifyBody: "json",
        jsonBody: "={{ {...} }}"
      }
    }
  }]
})
```

### 更新戦略の選択ガイド

| 状況 | 推奨戦略 | 理由 |
|------|---------|------|
| **新規ノード追加** | 完全パラメータ指定 | 必須パラメータの欠落を防ぐ |
| **単純な値変更** (URL、API Key等) | 部分更新OK | 他のパラメータに影響なし |
| **複雑な式変更** (jsonBody等) | 完全更新推奨 | 依存関係を明示的に管理 |
| **ノード移動・接続変更** | 完全ワークフロー更新 | 接続関係の整合性を保証 |
| **テスト後の修正** | 完全更新 | 予期しない副作用を防ぐ |

### ベストプラクティス

1. **更新前のバックアップ**:
```javascript
// 現在のワークフローを取得して保存
const currentWorkflow = await n8n_get_workflow({ id: workflowId });
// 更新実行
// エラー時はcurrentWorkflowから復元可能
```

2. **段階的更新**:
```javascript
// Step 1: 1つのノードを更新
// Step 2: テスト実行
// Step 3: 成功したら次のノードを更新
// Step 4: 繰り返し
```

3. **バージョン管理**:
```javascript
// 各更新後にバージョンIDを記録
// docs/setup/WF6-SETUP.md の変更履歴に記載
```

### ワークフローアクティブ化の制限

#### 🚨 Critical: MCPではワークフローをアクティブ化できない

**問題**: n8n MCPの`n8n_update_partial_workflow`で`active: true`を設定しても反映されない

**❌ 動作しない方法**:
```javascript
// MCPでactiveを更新しようとする
n8n_update_partial_workflow({
  id: "workflowId",
  operations: [{
    type: "updateSettings",
    settings: { active: true }
  }]
})
// 結果: ワークフローは更新されるが active: false のまま
```

**✅ 正しい方法**: n8n UIで手動アクティブ化

```
1. n8n管理画面でワークフローを開く
2. 右上のトグルスイッチを OFF → ON に切り替える
3. ワークフローが Active 状態になったことを確認
```

**理由**:
- n8n APIまたはMCPの制限により、プログラム経由でのアクティブ化ができない
- ワークフローのアクティブ化にはn8n内部での追加のバリデーションや初期化処理が必要
- 手動アクティブ化により、トリガーノード（Webhook等）が正しく登録される

**ベストプラクティス**:
1. MCPでワークフロー構築・更新を完了
2. n8n UIで手動アクティブ化
3. アクティブ化後にテスト実行

**適用例**: WF7 Phase1, Phase2で確認済み

---

## 5. テストとデバッグアプローチ

### テスト駆動開発（TDD）アプローチ

#### WF6で学んだ教訓: テスト優先、ドキュメント後回し

**❌ 非効率なアプローチ**:
```
修正 → ドキュメント更新 → テスト → エラー発見 → 修正 → ドキュメント更新...
```
- 問題: ドキュメント更新に時間がかかり、テストイテレーションが遅い

**✅ 効率的なアプローチ**:
```
修正 → テスト → エラー分析 → 修正 → テスト → 成功確認 → ドキュメント一括更新
```
- 利点: 高速なテスト-修正サイクル、成功後に包括的なドキュメント作成

### 段階的テスト戦略

#### Phase 1: データフローシミュレーション（テスト前）

```javascript
// 各ノードのパラメータを目視確認
// - 必須パラメータの存在確認
// - 式構文の妥当性チェック
// - ノード参照の正確性確認
// - データ型の一致確認
```

**チェックリスト**:
- [ ] HTTP Request Node: `specifyBody` パラメータ設定済み
- [ ] HTTP Request Node: `={{ }}` 式使用時は `specifyBody: "json"`
- [ ] Function Node: `return [{ json: {...} }]` 形式の戻り値
- [ ] ノード参照: 正確なノード名を使用
- [ ] プロパティアクセス: 前ノードの出力構造と一致

#### Phase 2: 単体テスト（n8n UI）

```javascript
// 各ノードを個別に "Execute Node" で実行
// 1. Schedule Trigger → 手動トリガーに切り替え
// 2. Notion Topics → 結果が10件取得されるか確認
// 3. Select Topic → topicName, score等が正しいか確認
// 4. GPT-4 Title → 3タイプのタイトルが生成されるか確認
// ... 以下同様
```

#### Phase 3: 統合テスト

```javascript
// 全ノードを一度に実行
// - n8n UI → "Execute Workflow" をクリック
// - 各ノードの入出力を確認
// - エラー発生時は該当ノードから調査
```

### デバッグ手法

#### 手法1: 実行ログの詳細分析

```javascript
// n8n MCP経由で実行詳細を取得
n8n_get_execution({
  id: "816",  // 失敗したExecution ID
  mode: "filtered",
  nodeNames: ["Notion: Register Article"]  // 失敗したノード
})

// 確認項目:
// - error.message: エラーメッセージ
// - error.httpCode: HTTPステータスコード
// - requestBody: 実際に送信されたリクエスト
// - responseBody: APIからのレスポンス
```

#### 手法2: Notion/Slack通知での確認

```javascript
// Slack通知ノードを追加してデバッグ情報を送信
{
  "jsonBody": "={{
    {
      text: 'Debug Info',
      blocks: [{
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*Title:* ' + $('Prepare Data').first().json.title + '\n' +
                '*Body Length:* ' + $('Prepare Data').first().json.bodyLength + '\n' +
                '*Categories:* ' + $('Prepare Data').first().json.categories.join(', ')
        }
      }]
    }
  }}"
}
```

#### 手法3: Function Nodeでのログ出力

```javascript
// Function Nodeでconsole.logを使用
const data = $('Previous Node').first().json;
console.log('Debug - topicName:', data.topicName);
console.log('Debug - score:', data.score);
return [{ json: data }];

// n8n実行ログのconsoleタブで確認可能
```

### エラーパターンと対処法

| エラータイプ | 症状 | 対処法 |
|------------|------|--------|
| **式評価エラー** | `specifyBody: "string"` + `={{ }}` | `specifyBody: "json"` + `jsonBody` に変更 |
| **ノード参照エラー** | "Referenced node doesn't exist" | ノード名を正確に確認、typoチェック |
| **プロパティアクセスエラー** | `undefined` または `null` | 前ノードの出力構造を確認、プロパティ名修正 |
| **設定エラー** | "The workflow has issues" | 必須パラメータ欠落、完全パラメータセット適用 |
| **API認証エラー** | 401 Unauthorized | API Key確認、Headerパラメータ確認 |
| **APIバリデーションエラー** | 400 Bad Request | リクエストボディの構造確認、API仕様書と照合 |

---

## 6. Notion API統合

### Notion APIの特性

#### 制限事項

1. **rich_text プロパティ**: 最大2000文字
```javascript
// ✅ 長い本文を扱う場合の対処法
{
  "Description": {
    "rich_text": [{
      "text": {
        "content": $('Prepare Data').first().json.body.substring(0, 2000)
      }
    }]
  }
}
```

2. **API Version**: 必須ヘッダー
```javascript
{
  "headerParameters": {
    "parameters": [
      { "name": "Notion-Version", "value": "2022-06-28" }
    ]
  }
}
```

### 🚨 Critical: n8n Notion Nodeのプロパティアクセスパターン

#### ルール1: Notion Nodeが返すプロパティには `property_` プレフィックスが付く

**n8n Notion Nodeの特性**:
- Notion APIから取得したページプロパティは `property_` プレフィックス付きで返される
- プロパティ値は**直接文字列として返される**（rich_text構造なし）
- 例: `Script JSON` プロパティ → `property_script_json` キー

**❌ 間違ったアクセスパターン** (rich_text構造を想定):
```javascript
// Python Code Nodeでの誤った実装
def generate_slides(script_data):
    # Notionプロパティ取得
    properties = script_data.get('properties', {})

    # Script JSONからsegments配列を取得
    script_json_raw = properties.get('Script JSON', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
    # ^^^ この構造は存在しない！

    try:
        script_json = json.loads(script_json_raw) if script_json_raw else {}
        segments = script_json.get('segments', [])
    except Exception as e:
        print(f"Script JSON解析エラー: {e}")
        segments = []

    # len(segments) は常に 0 になる
    # フォールバックテキストが使用される
```

**問題点**:
- `properties` オブジェクトは空 `{}` になる
- `script_json_raw` は常に `'{}'` (空のJSON文字列)
- `segments` 配列は常に空 `[]`
- 結果: すべてフォールバックテキスト（「フックテキストがありません」等）が使用される

**✅ 正しいアクセスパターン** (property_プレフィックス + 直接文字列):
```javascript
// Python Code Nodeでの正しい実装
def generate_slides(script_data):
    # Script JSONを直接取得（property_プレフィックス付き）
    script_json_raw = script_data.get('property_script_json', '{}')
    # ^^^ 直接文字列として取得

    try:
        script_json = json.loads(script_json_raw) if script_json_raw else {}
        segments = script_json.get('segments', [])
    except Exception as e:
        print(f"Script JSON解析エラー: {e}")
        segments = []

    # len(segments) >= 7 の場合、実際のデータが使用される
```

**正しい動作**:
- `property_script_json` キーから直接JSON文字列を取得
- JSON parse後に `segments` 配列を抽出
- 実際の台本データ（日本語字幕等）が使用される

#### ルール2: すべてのNotionプロパティに適用

**Notionプロパティとn8nキーの対応表**:

| Notionプロパティ名 | n8n Notion Nodeキー | データ型 | アクセス方法 |
|------------------|-------------------|---------|------------|
| **Script JSON** | `property_script_json` | string (JSON) | `script_data.get('property_script_json', '{}')` |
| **Brand Colors** | `property_brand_colors` | string (JSON) | `script_data.get('property_brand_colors', '{}')` |
| **Visual Elements** | `property_visual_elements` | string (JSON) | `script_data.get('property_visual_elements', '{}')` |
| **Duration Config** | `property_duration_config` | string (JSON) | `script_data.get('property_duration_config', '{}')` |
| **Motion Prompts** | `property_motion_prompts` | string (JSON) | `script_data.get('property_motion_prompts', '{}')` |
| **Title** | `property_title` または `name` | string | `script_data.get('name', '')` |

**命名規則**:
```
Notionプロパティ名をスネークケースに変換 + property_ プレフィックス

例:
- "Script JSON" → "property_script_json"
- "Brand Colors" → "property_brand_colors"
- "Visual Elements" → "property_visual_elements"
- "Duration Config" → "property_duration_config"
- "Motion Prompts" → "property_motion_prompts"
```

#### 実際のエラー事例（WF7 Phase4a）

**症状**:
- 7枚のスライドすべてにフォールバックテキストが表示
- 実際の日本語字幕（「子供の英語学習に最適な場所は？」等）が表示されない
- Notion Script JSONには正しいデータが存在

**原因分析**:
```javascript
// Notion Node実行結果（Execution #1674）
{
  "json": {
    "id": "2a568d5c-2986-81bd-8e64-fb2407df397b",
    "name": "渋谷で見つける: 子供の英語学習に最適な場所",
    "property_script_json": "{\n  \"segments\": [\n    {\n      \"assetTag\": \"渋谷の景色\",\n      \"duration\": 8,\n      \"subtitle\": \"子供の英語学習に最適な場所は？\",\n      \"narration\": \"渋谷で見つける、子供の英語学習に最適な場所を探していますか？\"\n    },\n    // ... 6 more segments
    ]\n}",
    "property_brand_colors": "",
    "property_motion_prompts": "",
    "property_visual_elements": "",
    "property_duration_config": ""
  }
}

// Python Code Nodeの誤った実装
properties = script_data.get('properties', {})  # Returns {}
script_json_raw = properties.get('Script JSON', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
# Returns '{}' (空のJSON文字列)

# 結果: len(segments) = 0
# フォールバックロジックが実行される
```

**修正内容**:
```python
# 修正前（誤り）
script_json_raw = properties.get('Script JSON', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
brand_colors_raw = properties.get('Brand Colors', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
visual_elements_raw = properties.get('Visual Elements', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
duration_config_raw = properties.get('Duration Config', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
motion_prompts_raw = properties.get('Motion Prompts', {}).get('rich_text', [{}])[0].get('plain_text', '{}')

# 修正後（正しい）
script_json_raw = script_data.get('property_script_json', '{}')
brand_colors_raw = script_data.get('property_brand_colors', '{}')
visual_elements_raw = script_data.get('property_visual_elements', '{}')
duration_config_raw = script_data.get('property_duration_config', '{}')
motion_prompts_raw = script_data.get('property_motion_prompts', '{}')
```

**修正結果**:
- ✅ 7枚のスライドすべてに実際の日本語字幕が表示
- ✅ duration が segments から正しく取得される
- ✅ motion_prompt が取得される（デフォルト値）
- ✅ Cloudinary アップロードが成功する

**実行例（修正後）**:
```json
{
  "slides_metadata": [
    {"section": "hook", "duration": 8, "text": "子供の英語学習に最適な場所は？"},
    {"section": "intro", "duration": 7, "text": "信頼できる場所が見つからない…"},
    {"section": "point1", "duration": 10, "text": "AI検索を活用しよう！"},
    {"section": "point2", "duration": 8, "text": "地図最適化で簡単検索"},
    {"section": "point3", "duration": 7, "text": "渋谷の優れた店舗が多数！"},
    {"section": "summary", "duration": 5, "text": "さあ、始めよう！"},
    {"section": "cta", "duration": 5, "text": "詳細はリンクをチェック！"}
  ]
}
```

### ベストプラクティス

#### 1. Notion Node出力を使う場合の実装パターン

```python
# Python Code Node実装例
def process_notion_data(script_data):
    # ✅ 正しい: property_プレフィックス付きで直接アクセス
    script_json_raw = script_data.get('property_script_json', '{}')
    brand_colors_raw = script_data.get('property_brand_colors', '{}')

    # JSON parse
    try:
        script_json = json.loads(script_json_raw) if script_json_raw else {}
        brand_colors = json.loads(brand_colors_raw) if brand_colors_raw else DEFAULT_COLORS
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        script_json = {}
        brand_colors = DEFAULT_COLORS

    # データ使用
    segments = script_json.get('segments', [])
    background_color = brand_colors.get('background', '#1a1a2e')

    return segments, background_color
```

#### 2. デバッグ時の確認手順

**Step 1**: Notion Node出力を確認
```javascript
// n8n_get_executionで実際のNotion Node出力を取得
{
  "json": {
    "property_script_json": "{...}",  // ← この形式で返される
    "property_brand_colors": "{...}",
    "name": "ページタイトル"
  }
}
```

**Step 2**: プロパティキー名を確認
```python
# デバッグ用ログ出力
print(f"Available keys: {list(script_data.keys())}")
# Output: ['id', 'name', 'property_script_json', 'property_brand_colors', ...]
```

**Step 3**: プロパティ値の取得確認
```python
# 値が正しく取得できているか確認
script_json_raw = script_data.get('property_script_json', '{}')
print(f"Script JSON raw length: {len(script_json_raw)}")
print(f"First 100 chars: {script_json_raw[:100]}")
```

#### 3. チェックリスト

- [ ] Notion Nodeからデータを取得する場合、`property_` プレフィックスを使用
- [ ] `properties.get('Prop Name').rich_text[0].plain_text` パターンは使わない
- [ ] `script_data.get('property_prop_name', '')` パターンを使用
- [ ] JSON文字列として返されるため、`json.loads()` でparse
- [ ] デフォルト値を必ず設定（空文字列 `''` または空JSON `'{}'`）
- [ ] JSON parse エラーハンドリングを実装

### 教訓

1. **n8n Notion Nodeの出力形式を理解する**: `property_` プレフィックス + 直接文字列
2. **rich_text構造を想定しない**: Notion APIの構造とn8n Nodeの出力は異なる
3. **デバッグ時はまずキー名を確認**: `list(script_data.keys())` で実際の構造を把握
4. **段階的な実装**: プロパティ取得 → JSON parse → データ使用の3段階で実装
5. **テストデータで検証**: 実際のNotionページで最初にテストし、データ構造を確認

### 適用例

- **WF7 Phase4a**: Execution #1674-1677でフォールバック問題発生 → 修正後正常動作確認 (2025-11-12)

### Notionページ作成の正しいリクエスト構造

```javascript
{
  "method": "POST",
  "url": "https://api.notion.com/v1/pages",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      { "name": "Authorization", "value": "Bearer ntn_..." },
      { "name": "Notion-Version", "value": "2022-06-28" },
      { "name": "Content-Type", "value": "application/json" }
    ]
  },
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "jsonBody": "={{ {
    parent: {
      database_id: '29968d5c298681ad90d0c24ed710503e'
    },
    properties: {
      Title: {
        title: [{
          text: {
            content: $('Prepare Data').first().json.title
          }
        }]
      },
      Description: {
        rich_text: [{
          text: {
            content: $('Prepare Data').first().json.body.substring(0, 2000)
          }
        }]
      },
      Status: {
        select: {
          name: '検知済み'
        }
      },
      Category: {
        multi_select: $('Prepare Data').first().json.categories.map(c => ({ name: c }))
      }
    }
  } }}"
}
```

### Notionプロパティタイプ別の構文

| プロパティタイプ | 構文例 |
|----------------|--------|
| **title** | `{ title: [{ text: { content: "タイトル" } }] }` |
| **rich_text** | `{ rich_text: [{ text: { content: "本文" } }] }` |
| **number** | `{ number: 42 }` |
| **select** | `{ select: { name: "選択肢名" } }` |
| **multi_select** | `{ multi_select: [{ name: "タグ1" }, { name: "タグ2" }] }` |
| **date** | `{ date: { start: "2025-10-29" } }` |
| **checkbox** | `{ checkbox: true }` |
| **url** | `{ url: "https://example.com" }` |
| **email** | `{ email: "user@example.com" }` |
| **phone_number** | `{ phone_number: "090-1234-5678" }` |
| **relation** | `{ relation: [{ id: "page-id-1" }, { id: "page-id-2" }] }` |

---

## 7. Webhook設計パターンとRailway制限

### 🚨 Critical: Railway環境でのWebhook永続化制限

#### ルール1: パスパラメータは使用不可

**Railway環境の特性**:
- Webhook URLはコンテナ再起動後も永続化される
- しかし、パスパラメータ形式のルーティングは**サポートされていない**

**❌ 動作しないパターン** (Railway環境):
```json
{
  "parameters": {
    "path": "wf7-files/script/:articleId",
    "responseMode": "onReceived"
  }
}
```

**問題点**:
- `:articleId` のようなパスパラメータはRailwayルーティングテーブルに登録できない
- 結果: 404 Not Found エラー
- n8n UI上では正常に見えるが、実際にはルーティングが機能しない

**✅ 正しいパターン** (Railway対応):
```json
{
  "parameters": {
    "httpMethod": "GET",
    "path": "wf7-files-script",
    "responseMode": "onReceived"
  }
}
```

**修正内容**:
1. パスパラメータ削除: `/script/:articleId` → `/script`
2. クエリパラメータで代替: `?articleId=xxx` をURLに含める
3. httpMethod明示: `"httpMethod": "GET"` 必須

#### ルール2: パラメータアクセス方法の違い

| 方式 | URL例 | n8n式構文 | Railway対応 |
|------|-------|----------|-----------|
| **パスパラメータ** | `/files/:id` | `$json.params.id` | ❌ 非対応 |
| **クエリパラメータ** | `/files?id=xxx` | `$json.query.id` | ✅ 対応 |
| **固定パス** | `/test-webhook` | N/A | ✅ 対応 |

**データ解析ノード修正例**:

```javascript
// ❌ パスパラメータアクセス (Railway非対応)
const articleId = $json.params.articleId;

// ✅ クエリパラメータアクセス (Railway対応)
const articleId = $json.query.articleId;
```

#### ルール3: httpMethodパラメータは必須

**問題**: httpMethodパラメータが未設定の場合、Webhook登録がスキップされる可能性

```json
// ❌ httpMethod未設定
{
  "parameters": {
    "path": "wf7-files-script"
  }
}

// ✅ httpMethod明示
{
  "parameters": {
    "httpMethod": "GET",
    "path": "wf7-files-script",
    "responseMode": "onReceived"
  }
}
```

### Webhook設計パターン

#### パターン1: File Server (ファイル配信Webhook)

**ユースケース**:
- 動画、音声、字幕、アセットなどの大容量ファイル配信
- articleId紐付けでファイル取得

**推奨設計**:
```json
{
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "GET",
    "path": "wf7-files-script",
    "responseMode": "onReceived"
  }
}
```

**URL生成パターン**:
```javascript
// Phase3やPhase4でFile Server URLを生成
const baseUrl = "https://n8n-python-production-344b.up.railway.app";
const scriptUrl = `${baseUrl}/webhook/wf7-files-script?articleId=${articleId}`;
const assetsUrl = `${baseUrl}/webhook/wf7-files-assets?articleId=${articleId}`;
```

**データ解析ノード**:
```javascript
const input = $input.first().json;
const articleId = input.query.articleId;  // ← クエリパラメータから取得

if (!articleId) {
  throw new Error('articleId is required as query parameter');
}

return [{
  json: {
    articleId,
    timestamp: new Date().toISOString()
  }
}];
```

#### パターン2: Phase Webhook (処理トリガー)

**ユースケース**:
- Phase1-5の各フェーズ起動
- 複雑な入力データを受け取る

**推奨設計**:
```json
{
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "wf7-phase4-render",
    "responseMode": "onReceived"
  }
}
```

**入力データ解析**:
```javascript
const input = $input.first().json;
const body = input.body?.body || input.body || input;

const articleId = body.articleId;
const notionPageId = body.notionPageId;
const scriptUrl = body.scriptUrl;    // File Server URLを受け取る
const assetsUrl = body.assetsUrl;

if (!articleId || !notionPageId || !scriptUrl || !assetsUrl) {
  throw new Error('articleId, notionPageId, scriptUrl, assetsUrl are required');
}

return [{
  json: {
    articleId,
    notionPageId,
    scriptUrl,
    assetsUrl
  }
}];
```

### Railway環境でのWebhook運用ベストプラクティス

#### 1. URL設計の統一ルール

```
✅ 推奨: ケバブケース + クエリパラメータ
/webhook/wf7-files-script?articleId=xxx
/webhook/wf7-files-assets?articleId=xxx
/webhook/wf7-phase4-render (POST body)

❌ 非推奨: パスパラメータ
/webhook/wf7-files/script/:articleId
/webhook/wf7-files/assets/:articleId
```

#### 2. Webhook登録確認方法

**n8n UI保存後の確認手順**:
```bash
# 1. Webhookエンドポイントに直接アクセス
curl https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-script?articleId=test

# 2. 200 OKまたは正常なエラーメッセージが返れば登録成功
# 3. 404エラーならWebhook未登録またはパスパラメータ問題
```

#### 3. File Server URL生成の共通関数

```javascript
// Phase3, Phase4など複数フェーズで使用
function generateFileServerUrls(baseUrl, articleId) {
  return {
    scriptUrl: `${baseUrl}/webhook/wf7-files-script?articleId=${articleId}`,
    assetsUrl: `${baseUrl}/webhook/wf7-files-assets?articleId=${articleId}`,
    voiceFileUrl: `${baseUrl}/webhook/wf7-files-audio?articleId=${articleId}`,
    subtitleFileUrl: `${baseUrl}/webhook/wf7-files-subtitle?articleId=${articleId}`,
    videoUrl: `${baseUrl}/webhook/wf7-files-video?articleId=${articleId}`,
    thumbUrl: `${baseUrl}/webhook/wf7-files-thumbnail?articleId=${articleId}`
  };
}

// 使用例
const baseUrl = "https://n8n-python-production-344b.up.railway.app";
const articleId = $('入力データ解析').first().json.articleId;
const urls = generateFileServerUrls(baseUrl, articleId);
```

### 実際のエラー事例と修正

#### 事例1: File Server 404エラー (WF7)

**症状**:
- File Server Webhook (6個) 全て404エラー
- WF7 Phase1-5 Webhookは正常動作

**原因**:
- File Server WebhookがパスパラメータURL形式: `/wf7-files/script/:articleId`
- Railwayがパスパラメータをサポートしていないためルーティング未登録

**修正内容**:
1. **Webhookノード**: パス変更 + httpMethod追加
   - 旧: `wf7-files/script/:articleId`
   - 新: `wf7-files-script` + `httpMethod: "GET"`

2. **データ解析ノード**: パラメータアクセス変更
   - 旧: `$json.params.articleId`
   - 新: `$json.query.articleId`

3. **Phase3/Phase4**: URL生成ロジック変更
   - 旧: `${baseUrl}/webhook/wf7-files/audio/${articleId}`
   - 新: `${baseUrl}/webhook/wf7-files-audio?articleId=${articleId}`

4. **Phase4**: ダウンロードノードURL参照修正
   - 旧: `$json.scriptUrl` (直接アクセス失敗)
   - 新: `$('レンダリングリクエスト構築').first().json.renderRequest.scriptUrl`

**結果**: ✅ 全File Server Webhook正常動作確認 (2025-11-01)

### 教訓とベストプラクティス

1. **Railway環境では常にクエリパラメータを使用**: パスパラメータは避ける
2. **httpMethodパラメータは必須**: Webhook登録の確実性を担保
3. **UI保存後に動作確認**: curlでWebhookエンドポイントをテスト
4. **URL生成ロジックを一元化**: 共通関数で一貫性を保つ
5. **ドキュメント化**: 各File ServerのURL形式を明記
6. **E2Eテスト**: Phase→File Server→Phaseの連携を検証

---

## 8. Execute Command ノードのベストプラクティス

### 🚨 Critical: 複数行コマンドパラメータの落とし穴

#### ルール1: commandパラメータは必ず単一行形式で記述

**n8n UIの危険な挙動**:
- n8n UIでExecute Commandノードの長いコマンドを編集すると、自動的に改行が挿入される
- 保存時には正常に見えるが、実行時にbash/shellがコマンドを正しく解釈できない
- 結果: ノード実行がスキップされ、ワークフロー全体が停止または非常に長い時間実行される

**❌ 動作しないパターン** (n8n UIが自動挿入した改行):
```javascript
{
  "parameters": {
    "command": "=python -c \"from PIL import Image; [Image.new('RGB', (1080, 1920), \n  color=['blue','green','red','yellow'][i%4]).save(f'/tmp/integration_asset_{i}.jpg') \n  for i in range(10)]\" && echo '{{ $json.scriptJson }}' > {{ $json.scriptPath }} &&\n  echo '{{ $json.assetsJson }}' > {{ $json.assetsPath }} && python\n  /app/render_video_ffmpeg.py --script {{ $json.scriptPath }} --assets {{\n  $json.assetsPath }} --out {{ $json.outputPath }}"
  }
}
```

**問題点**:
- コマンド文字列内に `\n` (改行文字) が含まれる
- bash/shellは改行を含むコマンドを正しく解釈できない
- Execute Commandノードが実行されず、後続のノードも実行されない
- ワークフロー全体が「canceled」ステータスで異常終了
- 実行時間が極端に長くなる（例: 7時間51分）

**✅ 正しいパターン** (単一行形式):
```javascript
{
  "parameters": {
    "command": "=python -c \"from PIL import Image; [Image.new('RGB', (1080, 1920), color=['blue','green','red','yellow'][i%4]).save(f'/tmp/integration_asset_{i}.jpg') for i in range(10)]\" && echo '{{ $json.scriptJson }}' > {{ $json.scriptPath }} && echo '{{ $json.assetsJson }}' > {{ $json.assetsPath }} && python /app/render_video_ffmpeg.py --script {{ $json.scriptPath }} --assets {{ $json.assetsPath }} --out {{ $json.outputPath }}"
  }
}
```

**正しい動作**:
- 改行なし、すべて1行で記述
- bashが正しくコマンドを解釈
- Execute Commandノードが正常に実行される
- 実行時間が正常範囲に収まる（例: 19秒）

#### ルール2: n8n UI保存後の検証手順

**必須検証ステップ**:
```
1. n8n UIでワークフローを保存
2. n8n_get_workflowでワークフロー定義をJSON取得
3. Execute CommandノードのcommandパラメータをJSONで確認
4. "\n" 文字が含まれていないか目視確認
5. 含まれていた場合、n8n_update_full_workflowで単一行形式に修正
```

**検証コマンド例**:
```javascript
// ワークフロー取得
const workflow = await n8n_get_workflow({ id: "workflowId" });

// Execute Commandノードを検索
const executeNodes = workflow.nodes.filter(n => n.type === "n8n-nodes-base.executeCommand");

// commandパラメータの改行チェック
executeNodes.forEach(node => {
  const command = node.parameters.command;
  if (command.includes("\n")) {
    console.warn(`⚠️ Node "${node.name}" contains newlines in command parameter`);
  }
});
```

#### 実際のエラー事例（WF7 Phase4 Execution 101）

**症状**:
- Execution ID: 101
- Status: canceled
- Duration: 28,239,429ms (7時間51分39秒)
- 実行されたノード: 6 / 13
- 停止位置: "レンダリングリクエスト構築"
- 未実行: "動画レンダリング実行", "動画メタデータ抽出", "Notionペイロード作成", "Notionページ更新", "Respond to Webhook"

**原因分析**:
```javascript
// Execution 101のワークフロー定義（2025-11-03T16:06:04に更新）
{
  "parameters": {
    "command": "=python -c \"from PIL import Image; [Image.new('RGB', (1080, 1920), \n  color=['blue','green','red','yellow'][i%4]).save(f'/tmp/integration_asset_{i}.jpg') \n  for i in range(10)]\" && ..."
  }
}
// ← commandパラメータに複数の"\n"が含まれている
```

**修正内容**:
```javascript
// 2025-11-04T01:12:15.357Zにn8n_update_full_workflowで修正
{
  "parameters": {
    "command": "=python -c \"from PIL import Image; [Image.new('RGB', (1080, 1920), color=['blue','green','red','yellow'][i%4]).save(f'/tmp/integration_asset_{i}.jpg') for i in range(10)]\" && echo '{{ $json.scriptJson }}' > {{ $json.scriptPath }} && echo '{{ $json.assetsJson }}' > {{ $json.assetsPath }} && python /app/render_video_ffmpeg.py --script {{ $json.scriptPath }} --assets {{ $json.assetsPath }} --out {{ $json.outputPath }}"
  }
}
// ← 改行をすべて削除し、単一行形式に統一
```

**修正結果（Execution 146）**:
- Status: success
- Duration: 19,056ms (19秒)
- 実行されたノード: 11 / 11 ✅
- すべてのノードが正常実行
- **パフォーマンス改善: 99.9%** (7h51m → 19s)

#### デバッグ手法: Execution Historyの分析

**Step 1: 失敗したExecutionを特定**
```javascript
// 実行履歴を取得
n8n_list_executions({
  workflowId: "workflowId",
  limit: 20
})

// Status: "canceled" または Duration異常に長い実行を探す
```

**Step 2: Execution詳細を分析**
```javascript
n8n_get_execution({
  id: "executionId",
  mode: "summary"
})

// 確認項目:
// - どのノードまで実行されたか（stoppedAt）
// - 未実行のノードは何か
// - エラーメッセージの有無
// - 実行時間の異常
```

**Step 3: ワークフロー定義を確認**
```javascript
n8n_get_workflow({
  id: "workflowId"
})

// Execute Commandノードのcommandパラメータを重点的にチェック
// "\n" 文字の有無を確認
```

**Step 4: タイムライン分析**
```javascript
// 複数のExecutionを時系列で比較
// - いつから問題が発生したか
// - どのワークフロー更新が原因か
// - 成功していたExecutionと失敗したExecutionの差分

// 例: Execution 101の前後
// - Execution 100 (2025-11-03 15:00) ← 成功
// - ワークフロー更新 (2025-11-03 16:06:04) ← この時点で改行が混入
// - Execution 101 (2025-11-03 16:10) ← 失敗開始
```

### ベストプラクティス

#### 1. Execute Command ノード作成時
- [ ] commandパラメータは必ず単一行で記述
- [ ] 長いコマンドでも改行を使わず、`&&` で連結
- [ ] n8n式構文 `={{ }}` を使う場合も単一行を維持

#### 2. ワークフロー保存後
- [ ] n8n_get_workflowでJSON定義を取得
- [ ] Execute Commandノードのcommandパラメータを確認
- [ ] "\n" が含まれていないか検証
- [ ] 含まれていた場合は即座に単一行形式に修正

#### 3. テスト実行前
- [ ] Execute Commandノードを含むワークフローは必ず検証
- [ ] 単体テスト（Execute Node）で動作確認
- [ ] 実行時間が正常範囲内か確認

#### 4. デバッグ時
- [ ] Execution Historyで実行パターンを分析
- [ ] 成功/失敗の境界となったワークフロー更新を特定
- [ ] Execute Commandノードのcommandパラメータを重点調査
- [ ] タイムアウトや長時間実行は改行混入の可能性を疑う

#### 5. ドキュメンテーション
- [ ] Execute Commandノードの修正履歴を記録
- [ ] 改行問題の発生と修正をナレッジベースに記載
- [ ] 次回の同様問題を防ぐための教訓を明記

### 教訓

1. **n8n UIは信頼しない**: UI上で正常に見えても、JSON定義を必ず確認する
2. **単一行の徹底**: Execute Commandノードのcommandパラメータは例外なく単一行形式
3. **保存後検証**: n8n UIで保存した直後に、MCPまたはAPIで実際のJSON定義を確認
4. **高速検証サイクル**: ドキュメント更新より先にテスト実行で問題を発見
5. **Execution History活用**: 実行履歴の時系列分析で問題原因を特定

### 適用例

- **WF7 Phase4**: Execution 101 (7h51m失敗) → Execution 146 (19s成功) - 2025-11-04
- **影響範囲**: Execute Commandノードを使う全ワークフロー
- **再発防止**: 本ナレッジセクションの作成と共有

---

## 9. 非同期API処理とポーリングループ

### 🚨 Critical: fal.ai Queue APIの非同期処理パターン

#### ルール1: 非同期APIは必ずポーリングループを実装

**fal.ai Queue APIの特性**:
- リクエスト後すぐに完了しない（非同期処理）
- ステータス遷移: `IN_QUEUE` → `IN_PROGRESS` → `COMPLETED`
- 処理時間: 5-30秒程度（動画の長さや複雑さに依存）

**❌ 動作しないパターン** (単純な待機):
```json
{
  "nodes": [
    {"name": "FFmpegレンダラー", "type": "httpRequest"},
    {"name": "Wait 5 Seconds", "type": "wait"},
    {"name": "Check Render Status", "type": "httpRequest"},
    {"name": "Get Rendered Video", "type": "set"}
  ]
}
```

**問題点**:
- 5秒では完了しない場合がある
- ステータスが`IN_PROGRESS`のままで分岐条件が失敗
- Webhook Responseノードに到達せず、空のレスポンスが返る
- クライアント側でタイムアウトエラー

**✅ 正しいパターン** (ポーリングループ):
```json
{
  "nodes": [
    {"name": "FFmpegレンダラー", "type": "httpRequest"},
    {"name": "Wait 5 Seconds", "type": "wait"},
    {"name": "Check Render Status", "type": "httpRequest"},
    {"name": "Render Completed?", "type": "if"},
    {"name": "Retry Counter", "type": "set"},
    {"name": "Check Retry Limit", "type": "if"},
    {"name": "Wait Before Retry", "type": "wait"},
    {"name": "Timeout Error Response", "type": "respondToWebhook"}
  ]
}
```

#### ルール2: ポーリングループ設計の必須要素

**4つの核心ノード**:

1. **Retry Counter (Set node)**:
```javascript
{
  "parameters": {
    "mode": "manual",
    "assignments": {
      "assignments": [{
        "name": "retry_count",
        "value": "={{ $json.retry_count ? $json.retry_count + 1 : 1 }}",
        "type": "number"
      }]
    }
  }
}
```
- 役割: 現在のリトライ回数を追跡
- 初回: `retry_count = 1`
- 2回目以降: 既存値に+1

2. **Check Retry Limit (IF node)**:
```javascript
{
  "parameters": {
    "conditions": {
      "conditions": [{
        "leftValue": "={{ $json.retry_count }}",
        "rightValue": 6,
        "operator": {
          "type": "number",
          "operation": "smaller"
        }
      }]
    }
  }
}
```
- 役割: リトライ上限チェック
- TRUE分岐: `retry_count < 6` → 再試行
- FALSE分岐: `retry_count >= 6` → タイムアウトエラー

3. **Wait Before Retry (Wait node)**:
```javascript
{
  "parameters": {
    "amount": 5,
    "unit": "seconds"
  }
}
```
- 役割: リトライ間隔の制御
- 推奨値: 5秒（APIレート制限を考慮）

4. **Timeout Error Response (Respond to Webhook)**:
```javascript
{
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ {
      success: false,
      error: 'Rendering timeout after 30 seconds',
      request_id: $json.request_id,
      status: $json.status,
      retry_count: $json.retry_count
    } }}"
  }
}
```
- 役割: タイムアウト時のエラーレスポンス
- 必須情報: エラー内容、request_id、最終ステータス

#### ルール3: 接続構造とループバック

**完全な接続マップ**:
```javascript
{
  "Render Completed?": {
    "main": [
      [{"node": "Get Rendered Video"}],     // TRUE: 完了時
      [{"node": "Retry Counter"}]            // FALSE: 未完了時
    ]
  },
  "Retry Counter": {
    "main": [[{"node": "Check Retry Limit"}]]
  },
  "Check Retry Limit": {
    "main": [
      [{"node": "Wait Before Retry"}],       // TRUE: リトライ継続
      [{"node": "Timeout Error Response"}]   // FALSE: タイムアウト
    ]
  },
  "Wait Before Retry": {
    "main": [[{"node": "Check Render Status"}]]  // ← ループバック！
  }
}
```

**重要ポイント**:
- `Wait Before Retry` から `Check Render Status` へのループバック接続が核心
- これにより5秒ごとに最大6回（30秒）ステータスをチェック
- 完了まで自動的にリトライし続ける

#### ルール4: タイムアウト設計の計算式

**推奨パラメータ**:
```
最大待機時間 = 初回待機 + (リトライ回数 × リトライ間隔)
例: 5秒 + (5回 × 5秒) = 30秒
```

**調整ガイドライン**:

| 処理時間 | 初回待機 | リトライ間隔 | 最大リトライ | 合計待機 |
|---------|---------|------------|------------|----------|
| **短い** (5-10秒) | 3秒 | 3秒 | 3回 | 12秒 |
| **標準** (10-20秒) | 5秒 | 5秒 | 5回 | 30秒 |
| **長い** (20-40秒) | 10秒 | 5秒 | 6回 | 40秒 |
| **非常に長い** (40-60秒) | 10秒 | 10秒 | 5回 | 60秒 |

**選択基準**:
- **fal.ai動画レンダリング**: 標準設定（5秒 + 5×5秒 = 30秒）
- **画像生成**: 短い設定（3秒 + 3×3秒 = 12秒）
- **大容量動画**: 長い設定（10秒 + 6×5秒 = 40秒）

### 実際のエラー事例と修正

#### 事例1: 空のWebhookレスポンス (WF7-TEST Execution 454)

**症状**:
- Webhook呼び出し: `POST /webhook/wf7-ffmpeg-test`
- レスポンス: `200 OK` だが body が空
- クライアント側でJSON parse error

**原因分析**:
```javascript
// Execution 454の詳細
{
  "status": "success",
  "stoppedAt": 6,  // "Render Completed?" で停止
  "data": {
    "resultData": {
      "runData": {
        "Check Render Status": [{
          "json": {
            "status": "IN_PROGRESS",  // ← まだ完了していない
            "request_id": "...",
            "queue_position": 0
          }
        }]
      }
    }
  }
}
```

**問題点**:
1. 5秒待機では動画レンダリングが完了していない
2. IF条件: `status === "COMPLETED"` が `false`
3. FALSE分岐に何も接続されていない
4. Webhook Responseノードに到達せず
5. 結果: 空のレスポンス

**修正内容**:
```javascript
// FALSE分岐にポーリングループを追加
{
  "operations": [
    {
      "type": "addNode",
      "node": {
        "name": "Retry Counter",
        "type": "n8n-nodes-base.set",
        "parameters": {
          "assignments": {
            "assignments": [{
              "name": "retry_count",
              "value": "={{ $json.retry_count ? $json.retry_count + 1 : 1 }}"
            }]
          }
        }
      }
    },
    // ... 他の3ノードも追加
    {
      "type": "addConnection",
      "source": "Render Completed?",
      "target": "Retry Counter",
      "sourceOutput": "main",
      "targetInput": "main",
      "sourceIndex": 1  // FALSE分岐
    }
    // ... 他の接続も追加
  ]
}
```

**修正結果**:
- ポーリングループ実装により最大30秒待機
- レンダリング完了まで自動リトライ
- 完了時に正しいvideo URLをWebhook Responseで返す
- タイムアウト時は明示的なエラーレスポンス

#### 事例2: n8n_update_partial_workflowの制限

**試行錯誤の過程**:

**Attempt 1-5**: 接続パラメータエラー
```javascript
// ❌ 失敗: "must NOT have additional properties"
{
  "type": "addConnection",
  "source": "Render Completed?",
  "target": "Retry Counter",
  "sourceOutput": "main",
  "sourceIndex": 1
}
```
- エラー: `sourceOutput` と `sourceIndex` の組み合わせが無効
- 原因: n8n MCP APIの検証ルールが厳格

**Attempt 6**: ノードのみ追加
```javascript
// ❌ 失敗: "Disconnected nodes detected"
{
  "operations": [
    {"type": "addNode", "node": {...}},
    {"type": "addNode", "node": {...}},
    {"type": "addNode", "node": {...}},
    {"type": "addNode", "node": {...}}
  ]
}
```
- エラー: 接続のないノードは保存不可
- n8n: "Operations were applied but the workflow was NOT saved"

**Solution**: `n8n_update_full_workflow` への切り替え
```javascript
// ✅ 成功: 完全なワークフロー更新
n8n_update_full_workflow({
  id: "0SI8qdISZ087GEj0",
  name: "WF7-TEST: FFmpeg Async Polling Test",  // ← 必須パラメータ
  nodes: [...12 nodes...],     // 8既存 + 4新規
  connections: {...}           // 完全な接続マップ
})
```

**教訓**:
1. 複雑な接続変更は `n8n_update_full_workflow` を使用
2. `n8n_update_partial_workflow` はシンプルな更新のみ
3. `name` パラメータは必須（忘れやすいので注意）
4. 完全更新は接続整合性が保証される

### ベストプラクティス

#### 1. 非同期API処理時の設計チェックリスト

- [ ] APIが非同期処理か確認（Queue API、Job APIなど）
- [ ] ステータス遷移パターンを把握
- [ ] 完了までの標準的な処理時間を測定
- [ ] ポーリング間隔を決定（推奨: 5秒）
- [ ] 最大リトライ回数を決定（推奨: 5-6回）
- [ ] タイムアウト時のエラーハンドリングを実装

#### 2. ポーリングループ実装時の手順

**Step 1**: 基本フローの構築
```
Webhook → データ準備 → API呼び出し → 初回待機 → ステータス確認 → IF分岐
```

**Step 2**: 成功パスの実装
```
IF (TRUE) → 結果取得 → Webhook Response
```

**Step 3**: ポーリングループの追加
```
IF (FALSE) → Retry Counter → Retry Limit Check → Wait → (ループバック)
```

**Step 4**: タイムアウトハンドリング
```
Retry Limit (FALSE) → Timeout Error Response
```

**Step 5**: 接続の完全性確認
- すべてのIF分岐に接続があるか
- ループバック接続が正しいノードに戻るか
- エラーパスがWebhook Responseに到達するか

#### 3. デバッグ手法

**症状: 空のWebhookレスポンス**
```javascript
// Step 1: Executionを取得
n8n_get_execution({
  id: "executionId",
  mode: "summary"
})

// Step 2: どのノードで停止したか確認
// stoppedAt: 6 → IF nodeで停止

// Step 3: IF nodeの条件評価結果を確認
// 前ノードのstatusプロパティをチェック

// Step 4: FALSE分岐の接続を確認
// 接続がない場合はポーリングループを追加
```

**症状: タイムアウトしても完了しない**
```javascript
// 原因候補:
// 1. Retry Limit設定が高すぎる
// 2. Wait時間が短すぎる（APIに負荷）
// 3. ループバック接続が誤っている

// 確認方法:
// - retry_countの値を各ノードでログ出力
// - 実際のループ回数をカウント
// - 合計待機時間を計算
```

### ワークフロー設計パターン: 非同期処理

#### パターンA: シンプルポーリング（標準）
```
API Call → Wait → Status Check → IF (Completed?)
  ├─ TRUE → Get Result → Response
  └─ FALSE → Retry Counter → Retry Check → Wait → (loop back to Status Check)
           └─ Retry Limit → Timeout Error
```
- **適用**: 単一の非同期API呼び出し
- **例**: fal.ai動画レンダリング、画像生成

#### パターンB: 複数ステップポーリング
```
Step1 API → Poll Step1 → Step2 API → Poll Step2 → Final Result
```
- **適用**: 複数の非同期処理を連鎖
- **例**: 動画生成 → 音声生成 → 最終合成

#### パターンC: 並列ポーリング
```
API Call A → Poll A ─┐
API Call B → Poll B ─┼→ Wait All → Merge Results → Response
API Call C → Poll C ─┘
```
- **適用**: 複数の独立した非同期処理
- **例**: 複数動画の同時レンダリング

### 適用例

**WF7-TEST Workflow**:
- **Before**: 5秒固定待機 → 空のレスポンス（Execution 454失敗）
- **After**: ポーリングループ（最大30秒） → 正常なレスポンス（テスト待ち）
- **改善**: 非同期処理対応、タイムアウトハンドリング追加
- **日付**: 2025-11-06

**次のステップ**:
- WF7-TEST でのE2Eテスト実行
- 成功確認後、WF7 Phase4本番環境に適用
- 他の非同期API（音声生成等）にも同様のパターンを適用

---

## 10. n8n IF Nodeの挙動とリトライループ実装パターン

### 🚨 Critical: n8n IF Nodeの特異な挙動

#### ルール1: IFノードは常にoutput[1]にデータをルーティングする

**n8n IF Nodeの特性**:
- 条件評価の結果（TRUE/FALSE）に関わらず、**常にデータはoutput[1]に流れる**
- output[0]は条件結果を示すメタデータのみで、実際のデータは含まれない
- この挙動はn8nの既知のバグまたは設計仕様

**❌ 直感的な接続（動作しない）**:
```json
{
  "IF - Check Retry Limit": {
    "main": [
      [{"node": "HTTP Request - Check Status"}],  // output[0] → リトライ継続
      [{"node": "Code - Timeout Error"}]           // output[1] → タイムアウト
    ]
  }
}
```

**問題点**:
- TRUEと評価されても、データはoutput[1]に流れる
- 結果: リトライループが動作せず、常にタイムアウトエラーノードに到達
- リトライカウンタが増加しないため、初回で「リトライ上限到達」と判定される

**✅ 正しい接続（動作する）**:
```json
{
  "IF - Check Retry Limit": {
    "main": [
      [{"node": "Code - Timeout Error"}],          // output[0] → タイムアウト（反転）
      [{"node": "HTTP Request - Check Status"}]    // output[1] → リトライ継続（反転）
    ]
  }
}
```

**正しい動作**:
- output[0]とoutput[1]の接続先を**逆にする**
- これにより、実際のデータフロー（output[1]）がリトライループに流れる
- FALSE評価時のみ、output[0]経由でタイムアウトエラーに到達

#### ルール2: リトライループ実装の標準パターン

**完全なノード構成**:

1. **HTTP Request - Submit to FAL** (非同期API呼び出し)
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://queue.fal.run/fal-ai/vidu/image-to-video",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ {...} }}"
  }
}
```
- 役割: Vidu APIにリクエスト送信
- 戻り値: `request_id`, `status_url`, `response_url`

2. **Wait - Initial** (初回待機)
```json
{
  "parameters": {
    "amount": 2,
    "unit": "seconds"
  }
}
```
- 役割: API処理開始までの最小待機時間
- 推奨値: 2-5秒

3. **HTTP Request - Check Status** (ステータス確認)
```json
{
  "parameters": {
    "method": "GET",
    "url": "={{ $json.status_url }}"
  }
}
```
- 役割: FAL APIのステータスをポーリング
- 戻り値: `status` (IN_QUEUE, IN_PROGRESS, COMPLETED)

4. **IF - Status is Completed** (完了判定)
```json
{
  "parameters": {
    "conditions": {
      "conditions": [{
        "leftValue": "={{ $json.status }}",
        "rightValue": "COMPLETED",
        "operator": {
          "type": "string",
          "operation": "equals"
        }
      }]
    }
  }
}
```
- 役割: 処理完了の判定
- TRUE → 結果取得へ
- FALSE → リトライカウンタへ

5. **Code - Increment Retry** (リトライカウンタ)
```javascript
const currentRetry = $input.first().json.retry_count || 0;
return [{
  json: {
    ...$input.first().json,
    retry_count: currentRetry + 1
  }
}];
```
- 役割: リトライ回数の追跡
- 初回: `retry_count = 1`
- 2回目以降: 既存値+1

6. **IF - Check Retry Limit** (リトライ上限チェック)
```json
{
  "parameters": {
    "conditions": {
      "conditions": [{
        "leftValue": "={{ $json.retry_count }}",
        "rightValue": 5,
        "operator": {
          "type": "number",
          "operation": "smaller"
        }
      }]
    }
  }
}
```
- 役割: リトライ上限（5回）の判定
- TRUE (`retry_count < 5`) → リトライ継続（**output[1]経由**）
- FALSE (`retry_count >= 5`) → タイムアウトエラー（**output[0]経由**）
- **⚠️ 重要**: 接続を逆にする必要がある（上記ルール1参照）

7. **Wait - Before Retry** (リトライ前待機)
```json
{
  "parameters": {
    "amount": 5,
    "unit": "seconds"
  }
}
```
- 役割: リトライ間隔の制御
- 推奨値: 5秒（APIレート制限考慮）
- **ループバック接続**: このノードから「HTTP Request - Check Status」へ接続

8. **Code - Timeout Error** (タイムアウトエラー)
```javascript
const section = $('Code - Prepare FAL Payload').item.json.slide_metadata.section;
const retryCount = $input.first().json.retry_count || 0;
return [{
  json: {
    success: false,
    error: `Rendering timeout for ${section} after ${retryCount} retries`,
    section: section,
    retry_count: retryCount
  }
}];
```
- 役割: タイムアウト時のエラーレスポンス
- エラー内容、section、retry_countを含む

#### ルール3: 接続構造の完全マップ

**正しい接続（output[0]とoutput[1]が反転）**:
```json
{
  "connections": {
    "HTTP Request - Submit to FAL": {
      "main": [[{"node": "Wait - Initial"}]]
    },
    "Wait - Initial": {
      "main": [[{"node": "HTTP Request - Check Status"}]]
    },
    "HTTP Request - Check Status": {
      "main": [[{"node": "IF - Status is Completed"}]]
    },
    "IF - Status is Completed": {
      "main": [
        [{"node": "HTTP Request - Get Result"}],    // TRUE → 完了時
        [{"node": "Code - Increment Retry"}]        // FALSE → 未完了時
      ]
    },
    "Code - Increment Retry": {
      "main": [[{"node": "IF - Check Retry Limit"}]]
    },
    "IF - Check Retry Limit": {
      "main": [
        [{"node": "Code - Timeout Error"}],         // output[0] → タイムアウト（反転！）
        [{"node": "Wait - Before Retry"}]           // output[1] → リトライ継続（反転！）
      ]
    },
    "Wait - Before Retry": {
      "main": [[{"node": "HTTP Request - Check Status"}]]  // ← ループバック
    },
    "Code - Timeout Error": {
      "main": [[{"node": "Respond to Webhook"}]]
    },
    "HTTP Request - Get Result": {
      "main": [[{"node": "Code - Build Video Metadata"}]]
    },
    "Code - Build Video Metadata": {
      "main": [[{"node": "Respond to Webhook"}]]
    }
  }
}
```

**重要ポイント**:
- `IF - Check Retry Limit`のoutput[0]とoutput[1]が**逆接続**
- この反転により、実際のデータフロー（output[1]）がリトライループに流れる
- ループバック: `Wait - Before Retry` → `HTTP Request - Check Status`

### 実際のエラー事例と修正

#### 事例1: リトライループが1回も実行されない (WF7 Phase4b Version 40以前)

**症状**:
- Webhook呼び出し: `POST /webhook/wf7-phase4b-image-to-video`
- 実行時間: ~2秒（異常に短い）
- エラー: "Rendering timeout for hook after 1 retries"
- 期待動作: 最大5回リトライ（約27秒）

**原因分析**:
```javascript
// Version 40の接続（誤り）
{
  "IF - Check Retry Limit": {
    "main": [
      [{"node": "HTTP Request - Check Status"}],  // output[0] → リトライ継続
      [{"node": "Code - Timeout Error"}]           // output[1] → タイムアウト
    ]
  }
}

// 実際のデータフロー:
// 1. Code - Increment Retry → IF - Check Retry Limit
// 2. IFノードは常にデータをoutput[1]に流す
// 3. output[1]に接続されているのは「Code - Timeout Error」
// 4. 結果: 初回（retry_count=1）で即座にタイムアウトエラー
```

**問題点**:
- 直感的な接続（TRUE→リトライ、FALSE→エラー）が動作しない
- n8n IFノードの特異な挙動により、常にoutput[1]にデータが流れる
- リトライループが一度も実行されない

**修正内容（Version 41）**:
```json
{
  "operations": [{
    "type": "updateNode",
    "nodeId": "...",  // IF - Check Retry Limit
    "updates": {
      "name": "IF - Check Retry Limit",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1780, 400],
      "parameters": {
        "conditions": {
          "conditions": [{
            "leftValue": "={{ $json.retry_count }}",
            "rightValue": 5,
            "operator": {
              "type": "number",
              "operation": "smaller"
            }
          }]
        }
      }
    }
  }]
},
{
  "connections": {
    "IF - Check Retry Limit": {
      "main": [
        [{"node": "Code - Timeout Error"}],         // output[0] → タイムアウト（反転！）
        [{"node": "HTTP Request - Check Status"}]   // output[1] → リトライ継続（反転！）
      ]
    }
  }
}
```

**修正結果（Execution 1835, Version 40/41）**:
- HTTP Request - Check Status: 32回実行 ✅
- IF - Check Retry Limit: 31回実行 ✅
- 実行時間: 27秒（リトライループが正常動作）
- 最終結果: 動画レンダリング完了、メタデータ取得成功

**パフォーマンス改善**:
- Version 40以前: 2秒で失敗（リトライ1回のみ）
- Version 41以降: 27秒で成功（リトライ31回、完了まで自動ポーリング）

#### 事例2: 動画URL抽出失敗 (WF7 Phase4b Version 41→43)

**症状**:
- リトライループは正常動作（Version 41の修正により）
- エラー: "Video URL not found in FAL API response [line 10]"
- FAL APIは正常に動画を生成

**原因分析**:
```javascript
// Code - Build Video Metadata (Version 41, 誤り)
const videoUrl = resultData.output?.video_url ||
                 resultData.video_url ||
                 resultData.result?.video_url;
// ❌ resultData.video?.url のチェックが欠落

// 実際のFAL APIレスポンス (HTTP Request - Get Result):
{
  "video": {
    "url": "https://v3b.fal.media/files/b/monkey/wcMoML5e1xQeiLMIRoEVK_output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 1068711
  }
}
```

**修正内容（Version 43）**:
```javascript
// Code - Build Video Metadata (Version 43, 正しい)
const videoUrl = resultData.video?.url ||              // ✅ 最優先チェック追加
                 resultData.output?.video_url ||
                 resultData.video_url ||
                 resultData.result?.video_url;

if (!videoUrl) {
  throw new Error('Video URL not found in FAL API response');
}

return {
  json: {
    section: slideData.section,
    duration: slideData.duration,
    video_url: videoUrl,
    fal_request_id: requestId,
    motion_prompt: slideData.motion_prompt,
    filename: `video_${slideIndex + 1}_${slideData.section}.mp4`,
    text: slideData.text,
    slide_index: slideIndex,
    script_id: scriptId
  }
};
```

**修正結果（Version 43テスト）**:
- 実行時間: ~27秒（リトライループ正常動作）
- HTTP Status: 200 OK
- レスポンスボディ: 完全な動画メタデータ
```json
{
  "section": "hook",
  "duration": 3,
  "video_url": "https://v3b.fal.media/files/b/koala/vMh7M9AjM4xYRHPbzqgYn_output.mp4",
  "fal_request_id": "37b83e75-c9c8-49c1-b009-99f5f1078f88",
  "motion_prompt": "Subtle zoom in effect",
  "filename": "video_1_hook.mp4",
  "text": "驚きの事実！",
  "slide_index": 0,
  "script_id": "test-phase4b-vidu-20250112"
}
```

### ベストプラクティス

#### 1. IFノードを使ったリトライループ実装時

- [ ] IFノードのoutput[0]とoutput[1]の接続を**逆にする**
- [ ] リトライ継続条件（TRUE評価）を**output[1]**に接続
- [ ] エラー/タイムアウト条件（FALSE評価）を**output[0]**に接続
- [ ] ループバック接続を確実に実装（Wait → Status Check）
- [ ] リトライカウンタノードで`retry_count`を追跡
- [ ] タイムアウトエラーノードでエラー情報を含むレスポンス生成

#### 2. 非同期API処理パターン

- [ ] 初回待機時間を設定（2-5秒）
- [ ] ステータスチェックノードでAPI状態を確認
- [ ] 完了判定IFノードで処理終了を検出
- [ ] リトライ間隔を適切に設定（5秒推奨）
- [ ] 最大リトライ回数を設定（5-6回推奨）
- [ ] 合計タイムアウト時間を計算（初回待機 + リトライ×間隔）

#### 3. デバッグ手法

**Step 1: Execution履歴でリトライ回数を確認**
```javascript
n8n_get_execution({
  id: "executionId",
  mode: "summary"
})

// 確認項目:
// - HTTP Request - Check Status の itemsOutput 回数
// - IF - Check Retry Limit の itemsOutput 回数
// - 期待値: リトライ上限+1回（初回+リトライ）
```

**Step 2: IFノードの接続方向を確認**
```javascript
n8n_get_workflow_structure({
  id: "workflowId"
})

// connections オブジェクトを確認:
// - IF - Check Retry Limit の main[0] → エラーノード
// - IF - Check Retry Limit の main[1] → リトライループ
// ^^^ この順序が重要！
```

**Step 3: データフローの追跡**
```javascript
// 各ノードの実行データを確認
// - retry_count が増加しているか
// - status が COMPLETED になるまでループしているか
// - 最終的に正しいノードに到達しているか
```

### タイムアウト設計の計算式

**推奨パラメータ（Vidu API）**:
```
初回待機: 2秒
リトライ間隔: 5秒
最大リトライ: 5回

合計待機時間 = 2秒 + (5回 × 5秒) = 27秒
```

**調整ガイドライン**:

| API処理時間 | 初回待機 | リトライ間隔 | 最大リトライ | 合計 |
|-----------|---------|------------|------------|------|
| **短い** (5-10秒) | 2秒 | 3秒 | 3回 | 11秒 |
| **標準** (10-20秒) | 2秒 | 5秒 | 5回 | 27秒 |
| **長い** (20-40秒) | 5秒 | 5秒 | 7回 | 40秒 |

### 教訓

1. **n8n IFノードの挙動を理解する**: 常にoutput[1]にデータが流れる
2. **接続を逆にする**: 直感に反するが、これが正しい実装
3. **実行履歴で検証**: リトライ回数が期待値と一致するか確認
4. **段階的デバッグ**: まずループ動作、次にデータ処理の順で修正
5. **API仕様の確認**: レスポンス構造を正確に把握し、適切にパース

### 適用例

**WF7 Phase4b - Single Video Generator**:
- **Version 40以前**: リトライループ非動作（2秒で失敗）
- **Version 41**: IFノード接続反転によりリトライループ動作（27秒で完了）
- **Version 43**: 動画URL抽出修正により完全動作
- **日付**: 2025-11-12
- **Workflow ID**: `mfRdJJFJRKmeBjKv`

**次のステップ**:
- 他の非同期API統合にも同じパターンを適用
- リトライループの標準テンプレートとして文書化
- Phase4b完成後、Phase4c（動画結合）への統合

---

## 11. チェックリスト

### ワークフロー構築時チェックリスト

#### 設計フェーズ

- [ ] ワークフローの目的と期待する結果を明確化
- [ ] 各ノードの役割と責任を定義
- [ ] データフローを図示（入力→処理→出力）
- [ ] 外部API/サービスの仕様書を確認
- [ ] エラーハンドリング戦略を計画

#### 実装フェーズ

- [ ] **HTTP Request Node v4**:
  - [ ] `specifyBody` パラメータを明示的に設定
  - [ ] `={{ }}` 式を使う場合は `specifyBody: "json"` + `jsonBody`
  - [ ] 必須パラメータ（method, url, sendHeaders等）をすべて含める
- [ ] **Webhook Node**:
  - [ ] `httpMethod` パラメータを明示的に設定（GET/POST/PUT/DELETE）
  - [ ] Railway環境ではパスパラメータ(`:id`)を使用しない
  - [ ] クエリパラメータ(`?id=xxx`)形式でデータを渡す
  - [ ] データ解析ノードで `$json.query.paramName` でアクセス
  - [ ] UI保存後にcurlで動作確認（404エラーチェック）
- [ ] **Function Node**:
  - [ ] 戻り値が `return [{ json: {...} }]` 形式
  - [ ] エラーハンドリングを実装（try-catch）
- [ ] **ノード参照**:
  - [ ] ノード名が正確（typoなし）
  - [ ] プロパティ名が前ノードの出力と一致
  - [ ] `.first()` または `.all()` を適切に使用
- [ ] **Notion API**:
  - [ ] `Notion-Version` ヘッダーを含める
  - [ ] rich_textフィールドは2000文字以内
  - [ ] プロパティタイプが正しい構文

#### テストフェーズ

- [ ] データフローシミュレーション（目視確認）
- [ ] 各ノードの単体テスト（Execute Node）
- [ ] 統合テスト（Execute Workflow）
- [ ] エラーケースのテスト
- [ ] 実行ログの詳細確認
- [ ] 外部システム（Notion, Slack等）での結果確認

#### デバッグフェーズ

- [ ] エラーメッセージの完全な読解
- [ ] 実行ログから実際のリクエスト/レスポンスを取得
- [ ] ノード間のデータ構造を確認
- [ ] API仕様書とリクエスト構造を照合
- [ ] 段階的なテストで問題箇所を特定

#### ドキュメンテーションフェーズ

- [ ] ワークフローの概要説明
- [ ] 各ノードの設定詳細
- [ ] テスト結果の記録
- [ ] エラーと修正内容の記録
- [ ] バージョンIDと変更履歴の記録
- [ ] 次のステップと改善点の記載

### ワークフロー更新時チェックリスト

- [ ] 更新前のワークフローバージョンIDを記録
- [ ] 変更内容を明確に定義
- [ ] 部分更新の場合、必須パラメータが保持されるか確認
- [ ] 更新後すぐにテスト実行
- [ ] 成功するまで修正-テストサイクルを繰り返す
- [ ] 最終成功後にドキュメント更新
- [ ] 新しいバージョンIDを記録

---

## 実践例: WF6構築から学んだワークフロー

### テストイテレーション記録

```
Iteration 1 (Execution 816):
  問題: Node 8 (Notion登録) 失敗
  原因: specifyBody: "string" + n8n式構文の誤用
  修正: specifyBody: "json" + jsonBody に変更
  結果: Node 8成功 → Node 9失敗

Iteration 2 (Execution 817):
  問題: Node 9 (Slack通知) 失敗
  原因: 存在しないノード名参照 + プロパティ名誤り
  修正: $('Select Topic').first().json.topicName に修正
  結果: Node 9成功 → ワークフロー設定エラー

Iteration 3 (Execution 822):
  問題: ワークフロー設定エラー
  原因: Node 9の部分更新により必須パラメータ欠落
  修正: 完全パラメータセット適用
  結果: 設定エラー解消 → 全ノード実行準備完了

Iteration 4 (Execution 823):
  結果: ✅ 完全成功
  実行時間: 36.855秒
  全ノード正常動作確認
```

### 今後のワークフロー構築への応用

1. **設計時**: HTTP Request Nodeの`specifyBody`パラメータを最初から正しく設定
2. **実装時**: ノード参照とプロパティアクセスを前ノード出力と照合
3. **更新時**: 部分更新ではなく完全パラメータセット更新を優先
4. **テスト時**: 高速な修正-テストサイクル、ドキュメントは成功後
5. **デバッグ時**: 実行ログの詳細分析、段階的な問題切り分け

---

---

## クリティカル: Error Handler実装パターン（n8nエラーデータ構造の制限対応）

### 問題: n8nのエラー出力にノード名が含まれない

**発見日時**: 2025-11-22 (WF-A: Generate Note Drafts from Editorial Ideas)

**背景**:
- n8nのエラーハンドリングで、エラー発生元ノードを特定しようとした
- `errorData.node`プロパティでノード名を取得しようとしたが、常に`undefined`
- 実際のn8nエラーデータ構造には**`node`フィールドが存在しない**

**n8nエラーデータの実際の構造**:
```javascript
{
  // 元の入力データ（すべてのフィールドそのまま）
  "trending_keyword": "...",
  "abstract": "...",
  // ... その他の入力フィールド

  // エラー情報（追加される）
  "error": {
    "message": "Credentials not found",
    "stack": "...",
    // その他のエラー詳細
  }
}
```

**重要**: `node`フィールドや`failedNodeName`などのメタデータは含まれない。

### 解決策: パターンマッチング戦略

エラーメッセージとデータ構造から発生元ノードを推測する実装パターン:

```javascript
// エラーハンドリング関数（改善版 - エラー発生元ノードを推測）
const errorData = $input.first().json;
const errorMessage = errorData.error?.message || JSON.stringify(errorData.error) || 'Unknown Error';
const timestamp = new Date().toISOString();

// エラー発生元ノードを推測（エラーメッセージまたはデータ構造から）
let failedNode = 'Unknown Node';

// 1. OpenAIエラーの検出（認証エラー、APIキーエラーなど）
if (errorMessage.includes('Credentials not found') ||
    errorMessage.includes('Invalid API key') ||
    errorMessage.includes('OpenAI')) {
  failedNode = 'OpenAI - Generate Note Draft1';
}
// 2. Parseエラーの検出（JSONパースエラーの特徴的なメッセージ）
else if (errorMessage.includes('parse') ||
         errorMessage.includes('JSON') ||
         errorMessage.includes('Unexpected token')) {
  failedNode = 'Parse OpenAI Note JSON1';
}
// 3. Google Sheetsエラーの検出
else if (errorMessage.includes('Sheets') ||
         errorMessage.includes('Google Sheets') ||
         errorMessage.includes('spreadsheet')) {
  failedNode = 'Google Sheets - Update Draft Row1';
}
// 4. データ構造から推測（特定のフィールドの有無で判断）
else if (errorData.draft_text || errorData.formatted_content) {
  failedNode = 'Parse OpenAI Note JSON1 or Google Sheets - Update Draft Row1';
}

return {
  json: {
    channel: '#content-ops',
    text: `⚠️ *WF-A エラー発生*\n\n*Failed Node:* ${failedNode}\n*Error:* ${errorMessage}\n*Time:* ${timestamp}\n*Workflow:* Generate Note Drafts from Editorial Ideas`
  }
};
```

### パターンマッチング戦略の設計指針

1. **エラーメッセージキーワード検出**: 各ノードタイプ固有のエラーメッセージを検出
   - API認証エラー: "Credentials not found", "Invalid API key"
   - サービス名: "OpenAI", "Sheets", "Google Sheets"
   - パースエラー: "parse", "JSON", "Unexpected token"

2. **データ構造分析**: エラーデータ内のフィールド存在で処理段階を推測
   - 生成済みデータ（`draft_text`, `formatted_content`など）の有無
   - API特有のレスポンスフィールド

3. **検出ロジックの優先順位**:
   - 最も特徴的なエラーから順に判定（OpenAI → Parse → Sheets）
   - データ構造推論は最後の手段（曖昧性が高い）

4. **フォールバック戦略**:
   - 特定できない場合は `'Unknown Node'` または範囲を示す（`'Node X or Y'`）
   - エラーメッセージ全文をログに含め、後で手動分析可能にする

### 適用時の注意点

- **ワークフロー固有のカスタマイズ必須**: 各ワークフローのノード構成とエラーパターンに応じて検出ロジックを調整
- **テストケース作成**: 各ノードで意図的にエラーを発生させ、検出ロジックを検証
- **継続的な改善**: 新しいエラーパターンが発見されたら検出ロジックを追加

### 実装効果（WF-A）

**Before**（Version 45以前）:
```
*Failed Node:* Unknown Node
*Error:* "Credentials not found"
```

**After**（Version 47以降）:
```
*Failed Node:* OpenAI - Generate Note Draft1
*Error:* "Credentials not found"
```

**改善結果**:
- エラー発生箇所が明確化され、デバッグ時間を大幅短縮
- Slack通知から即座に問題箇所を特定可能
- 複数ノードでエラーが発生する場合の切り分けが容易

---

## 10. AI Agent + JSON出力パイプライン

### 概要

AI Agent + Code ノードを使用したJSON出力パイプラインにおける3つのクリティカルな問題と解決策。これらは**Phase 4型インシデント**（データフロー・構文エラーによる実行時失敗）の典型例。

**検証環境**: Railway n8n (https://n8n-python-production-344b.up.railway.app)
**対象ワークフロー**: WF-B: Analyze & Suggest Next Actions (ID: 2mBYCQMjW2Vw1Xaa)

---

### 🚨 Critical Fix 1: Code ノードでのテンプレートリテラル構文エラー

#### 問題

**症状**:
```
SyntaxError: Invalid or unexpected token
evalmachine.<anonymous>:30
  throw new Error(`Missing required fields: ${missingFields.join(',
                                                                 ^^^
```

**根本原因**:
- Code ノード（JavaScript）内でバッククォート文字列が複数行にまたがると構文エラー
- n8nのCode実行環境がテンプレートリテラルの改行を正しく処理できない

#### 解決策

❌ **NG例** - テンプレートリテラル使用:
```javascript
throw new Error(`Missing required fields: ${missingFields.join(',
')}`);
```

✅ **OK例** - 文字列連結使用:
```javascript
throw new Error('Missing required fields: ' + missingFields.join(', '));
```

#### ベストプラクティス

```javascript
// Code ノード内のエラーメッセージは文字列連結で構築
const validationErrors = [];

if (missingFields.length > 0) {
  throw new Error('Missing required fields: ' + missingFields.join(', '));
}

if (!['improve', 'pause', 'scale'].includes(data.next_decision)) {
  validationErrors.push('Invalid next_decision: ' + data.next_decision);
}

if (validationErrors.length > 0) {
  throw new Error('Schema validation failed: ' + validationErrors.join(', '));
}
```

**キーポイント**:
- 動的な値を含むエラーメッセージは `+` 演算子で連結
- `Array.join()` で配列を文字列化
- バッククォートは使用しない

---

### 🚨 Critical Fix 2: AI Agent JSON出力のパース処理

#### 問題

**AI Agent出力形式**:
```json
{
  "output": "{\"next_decision\":\"improve\",\"next_action\":\"...\",\"insights\":[...]}"
}
```

- AI Agentは `{output: "JSON文字列"}` 形式で返す
- 直接 `$json` では構造化データとしてアクセス不可

#### 解決策

**Function - Validate Schema の実装**:

```javascript
// AI AgentのJSON文字列出力をパース
const aiOutput = $input.item.json.output;

// Markdownコードブロック除去
let parsedData;
try {
  const cleanedOutput = aiOutput
    .replace(/```json\n?/g, '')
    .replace(/```\n?/g, '')
    .trim();
  parsedData = JSON.parse(cleanedOutput);
} catch (error) {
  throw new Error('JSON parse failed: ' + error.message);
}

// スキーマバリデーション
const requiredFields = ['next_decision', 'next_action', 'next_segment', 'next_keyword_idea', 'insights', 'reasoning'];
const missingFields = requiredFields.filter(field => !(field in parsedData));

if (missingFields.length > 0) {
  throw new Error('Missing required fields: ' + missingFields.join(', '));
}

// バリデーション詳細チェック
const validationErrors = [];

if (!['improve', 'pause', 'scale'].includes(parsedData.next_decision)) {
  validationErrors.push('Invalid next_decision: ' + parsedData.next_decision);
}

if (!['Cold', 'Middle', 'Hot', 'Current'].includes(parsedData.next_segment)) {
  validationErrors.push('Invalid next_segment: ' + parsedData.next_segment);
}

if (parsedData.next_action && parsedData.next_action.length > 200) {
  validationErrors.push('next_action exceeds max length (200 chars)');
}

if (parsedData.next_keyword_idea && parsedData.next_keyword_idea.length > 100) {
  validationErrors.push('next_keyword_idea exceeds max length (100 chars)');
}

if (!Array.isArray(parsedData.insights) || parsedData.insights.length < 2 || parsedData.insights.length > 4) {
  validationErrors.push('insights must have 2-4 items');
}

if (parsedData.reasoning && parsedData.reasoning.length > 500) {
  validationErrors.push('reasoning exceeds max length (500 chars)');
}

if (validationErrors.length > 0) {
  throw new Error('Schema validation failed: ' + validationErrors.join(', '));
}

// フラットな構造でGoogle Sheetsに渡す
return {
  json: {
    ...parsedData,
    validation_passed: true,
    validated_at: new Date().toISOString()
  }
};
```

#### データフロー

```
AI Agent → {output: "JSON string"}
    ↓
Function - Validate Schema:
  1. $input.item.json.output 抽出
  2. Markdownコードブロック除去
  3. JSON.parse()
  4. スキーマバリデーション（enum, length, array size）
  5. フラット化して返却
    ↓
Google Sheets Update → ={{ $json.next_decision }} でアクセス可能
```

---

### 🚨 Critical Fix 3: AI Agent プロンプトの式評価エラー

#### 問題

**症状**:
AI Agentが記事データを受け取れず、以下のような応答を返す:
```json
{
  "output": "Please provide the article data in JSON format so I can perform the analysis..."
}
```

**根本原因**:

❌ **NG例** - 文字列連結が式評価されない:
```javascript
="You are a data-driven marketing analyst.\n\nPUBLISHED ARTICLE DATA:\n" + JSON.stringify($json.row, null, 2) + "\n\nANALYSIS TASK:..."
```

- `=` で始まっても `{{ }}` がないため、n8nは式として評価しない
- `JSON.stringify()` が実行されず、リテラル文字列として渡される

#### 解決策

✅ **OK例1** - テンプレートリテラル（推奨）:
```javascript
={{ `You are a data-driven marketing analyst.

PUBLISHED ARTICLE DATA:
${JSON.stringify($json.row, null, 2)}

ANALYSIS TASK:
Based on the above article data, provide your analysis in STRICT JSON format.

CRITICAL REQUIREMENTS:
1. Your response must be ONLY a valid JSON object
2. NO markdown code blocks (no \`\`\`json\`\`\`)
3. NO additional text before or after the JSON
4. Use the exact field names specified below

DECISION CRITERIA:
- "improve": PV < 1000 OR conversion < 1%
- "pause": PV < 100 AND conversion < 0.5% AND segment is Cold
- "scale": PV > 3000 AND conversion > 2%

REQUIRED JSON STRUCTURE:
{
  "next_decision": "improve" | "pause" | "scale",
  "next_action": "One concrete action (max 200 chars)",
  "next_segment": "Cold" | "Middle" | "Hot" | "Current",
  "next_keyword_idea": "One keyword suggestion (max 100 chars)",
  "insights": [
    "Insight 1 (max 200 chars)",
    "Insight 2 (max 200 chars)",
    "Insight 3 (max 200 chars, optional)",
    "Insight 4 (max 200 chars, optional)"
  ],
  "reasoning": "Concise explanation of your decision (max 500 chars)"
}

Remember: Return ONLY the JSON object, nothing else.` }}
```

**構文ポイント**:
- `={{ }}` で全体をラップ → n8nが式として評価
- バッククォート `` ` `` でテンプレートリテラル開始
- `${変数}` で変数展開
- 内部のバッククォートはエスケープ: `\`\`\`json\`\`\``

✅ **OK例2** - 配列join（より安全）:
```javascript
={{ [
  "You are a data-driven marketing analyst.",
  "",
  "PUBLISHED ARTICLE DATA:",
  JSON.stringify($json.row, null, 2),
  "",
  "ANALYSIS TASK:",
  "Based on the above article data, provide your analysis in STRICT JSON format.",
  // ... 各行を配列要素として列挙
].join("\n") }}
```

#### ベストプラクティス

**AI Agent プロンプトの黄金律**:

1. **式評価の明示**: `={{ }}` で必ずラップ
2. **変数展開**: テンプレートリテラルまたはarray join使用
3. **プロンプト構造**:
   ```javascript
   ={{ `[役割定義]

   INPUT DATA:
   ${JSON.stringify($json.data, null, 2)}

   TASK:
   [具体的なタスク指示]

   OUTPUT FORMAT:
   [JSON構造の明示]

   CONSTRAINTS:
   [制約条件]` }}
   ```

4. **JSON出力の強制**:
   - "Your response must be ONLY a valid JSON object"
   - "NO markdown code blocks"
   - "Use the exact field names specified below"

---

### 🔄 完全なデータフローパターン

#### WF-B成功パターン

```
1. Google Sheets Get
   ↓
   row_data: {status, trending_keyword, abstract, segment, ...}

2. Function - Filter published
   ↓
   filtered_rows with row_id, sheet_url

3. Split In Batches (size=1)
   ↓
   単一行データ

4. Project Config
   ↓
   config: {project_name, default_segment}

5. Merge (combine all)
   ↓
   row_data + config

6. Function - Preprocess
   ↓
   {row_id, sheet_url, row: {...}}

7. AI Agent (gpt-4o-mini)
   prompt: ={{ `...${JSON.stringify($json.row, null, 2)}...` }}
   ↓
   {output: "JSON string"}

8. Function - Validate Schema
   const aiOutput = $input.item.json.output;
   const cleanedOutput = aiOutput.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
   const parsedData = JSON.parse(cleanedOutput);
   // validate...
   return {json: {...parsedData, validation_passed: true}};
   ↓
   {next_decision, next_action, next_segment, next_keyword_idea, insights[], reasoning, validation_passed, validated_at}

9. Google Sheets Update (Append Row)
   next_decision: ={{ $json.next_decision }}
   next_action: ={{ $json.next_action }}
   next_segment: ={{ $json.next_segment }}
   next_keyword_idea: ={{ $json.next_keyword_idea }}
   insights_json: ={{ JSON.stringify($json.insights) }}
   reasoning: ={{ $json.reasoning }}
   analyzed_at: ={{ $json.validated_at }}
   ↓
   Google Sheets書き込み成功

10. Loop Back → Split In Batches (次の行へ)
```

---

### 📋 Phase 0チェックリスト更新

#### AI Agent + JSON出力パイプラインの追加検証項目

**設計段階**:
- [ ] AI Agentの出力形式を確認（`{output: "JSON string"}` 形式）
- [ ] Output Parser使用 vs 手動パース処理の選択
- [ ] JSONスキーマの明示的な定義
- [ ] 文字数制限・enum値の設計

**実装段階**:
- [ ] AI Agent プロンプト: `={{ }}` で式評価を明示
- [ ] 変数展開: テンプレートリテラルまたはarray join使用
- [ ] Function - Validate Schema: `$input.item.json.output` 抽出処理
- [ ] Markdownコードブロッククリーンアップ（```json```除去）
- [ ] エラーメッセージ: 文字列連結（`+`）使用、テンプレートリテラル禁止

**テスト段階**:
- [ ] AI Agentが実際のデータを受け取っているか確認
- [ ] JSON parseエラーの有無
- [ ] スキーマバリデーション通過確認
- [ ] 下流ノード（Google Sheets等）でフィールドアクセス可能か

---

### 🎯 再発防止のための原則

#### 1. Code ノード JavaScript 記述原則

```javascript
// ✅ DO: 文字列連結でエラーメッセージ構築
throw new Error('Error: ' + variable);

// ❌ DON'T: テンプレートリテラルの複数行
throw new Error(`Error: ${variable}
more text`);
```

#### 2. AI Agent プロンプト記述原則

```javascript
// ✅ DO: {{ }} + テンプレートリテラル
={{ `prompt text ${variable} more text` }}

// ✅ DO: {{ }} + array join
={{ ["line1", variable, "line2"].join("\n") }}

// ❌ DON'T: 文字列連結が式評価されない
="text" + variable + "more text"
```

#### 3. AI Agent 出力処理原則

```javascript
// ✅ DO: .output抽出 → clean → parse → validate
const aiOutput = $input.item.json.output;
const cleanedOutput = aiOutput.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
const parsedData = JSON.parse(cleanedOutput);
// validate schema...
return {json: {...parsedData}};

// ❌ DON'T: 直接 $json にアクセス
const data = $json.next_decision; // undefined
```

---

### 📚 参考リソース

**成果物**:
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-24_01-59_function-validate-schema-fixed.js` - 完全なバリデーション実装
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-23_22-22_WF-B-backup.json` - 修正前のワークフロー

**検証実行**:
- Execution 3952: Function - Validate Schema構文エラー
- Execution 3955: Google Sheets Update設定エラー
- Execution 3959: AI Agent式評価エラー
- Execution 3962: 全ノード成功（✅ 本番稼働可能）

**AI分析結果例** (Execution 3962):
```json
{
  "next_decision": "pause",
  "next_action": "Reassess content quality and targeting for Cold segment; consider updating article with more engaging visuals and examples.",
  "next_segment": "Cold",
  "next_keyword_idea": "AI導入 効果",
  "insights": [
    "Current article has zero PV and conversions, indicating low engagement.",
    "Segment is Cold, which typically requires awareness-raising strategies.",
    "Trending keyword is relevant but the content lacks traction.",
    "Improvement needed before scaling."
  ],
  "reasoning": "PV is 0 and conversion is 0%, both below thresholds for improvement or scaling; segment is Cold, meeting criteria for pause to reassess strategy before further promotion."
}
```

---

### ✅ 検証完了

- ✅ Code ノード構文エラー解決
- ✅ AI Agent JSON出力パース処理実装
- ✅ AI Agent プロンプト式評価修正
- ✅ Google Sheets フィールドマッピング修正
- ✅ 完全パイプライン実行成功（Execution 3962）

**WF-Bは本番環境で稼働可能です**。

---

## 11. Google Sheets ノード制約事項

### 🚨 Critical: Google Sheets Update ノードの0件出力問題

#### 問題の発見経緯

WF-B（記事分析ワークフロー）構築時、Google Sheets Update ノードが書き込み操作後に **0件の出力** を返すことが判明。これにより、後続ノードが実行されない問題が発生。

**発生状況**:
```
Function - Validate Schema
    └─→ Google Sheets - Update Row
          └─→ Slack - Send Message  ← 実行されない！
```

#### 原因

Google Sheets Update ノード（Resource: `sheet`, Operation: `update`）は、成功しても `outputItems: 0` を返すケースがある。n8nのデータフロー制御により、0件出力のノードから後続ノードは実行されない。

#### 解決策: 並列接続パターン

後続処理が必要な場合、Update ノードと並列に接続する：

```
Function - Validate Schema
    ├─→ Google Sheets - Update Row（書き込み用）
    └─→ Slack - Send Message（後続処理用）
```

**接続構造**:
```json
{
  "connections": {
    "Function - Validate Schema": {
      "main": [
        [
          { "node": "Google Sheets - Update Row", "type": "main", "index": 0 },
          { "node": "Slack - Send Message", "type": "main", "index": 0 }
        ]
      ]
    }
  }
}
```

### 🚨 matchingColumns パラメータの要件

#### ルール1: カラム名は実際のシートヘッダーと完全一致が必要

```javascript
// ❌ エラー: 存在しないカラムを指定
{
  "matchingColumns": ["row_number"],  // シートに row_number カラムがない
  "columns": {
    "mappingMode": "defineBelow",
    "value": {
      "next_decision": "={{ $json.next_decision }}"
    }
  }
}
// エラー: "The 'Column to Match On' parameter is required"

// ✅ 正しい: 実際のシートカラムを指定
{
  "matchingColumns": ["article_id"],  // シートに article_id カラムが存在
  "columns": {
    "mappingMode": "defineBelow",
    "value": {
      "next_decision": "={{ $json.next_decision }}"
    }
  }
}
```

#### ルール2: カラム名の大文字・小文字も一致させる

Google Sheets のカラム名が `Article_ID` なら、`matchingColumns` も `"Article_ID"` と指定する。

### 🚨 行番号（row_number）の取得と伝播

#### 問題: Google Sheets Read ノードは行番号を返さない

Google Sheets Read ノードの出力には、行番号情報が含まれない。これにより、Update 操作で「どの行を更新するか」を特定できない問題が発生。

#### 解決策: Code ノードで行番号を手動追加

**Google Sheets Read 直後に追加するCode ノード**:
```javascript
// Function - Add Row Numbers
const items = $input.all();
const results = [];

for (let i = 0; i < items.length; i++) {
  results.push({
    json: {
      ...items[i].json,
      row_number: i + 2  // ヘッダー行(1) + 0ベースインデックス
    }
  });
}

return results;
```

**行番号計算の理由**:
- Google Sheets の行番号は 1 から開始
- 行 1 はヘッダー
- データは行 2 以降
- 0ベースインデックス `i` に +2 することで、正しい行番号を取得

#### 🚨 Critical: row_number が 0 の場合の範囲エラー

```javascript
// ❌ row_number = 0 の場合
// 生成される範囲: "ideas!N0"
// エラー: "Invalid data[0]: Unable to parse range: ideas!N0"

// Google Sheets の有効な行番号は 1 以上
// 行 0 は存在しない
```

**検証コードの追加推奨**:
```javascript
if (!row_number || row_number < 2) {
  throw new Error(`Invalid row_number: ${row_number}. Must be >= 2 (row 1 is header)`);
}
```

### データフロー確認パターン

Google Sheets を使用するワークフローでは、以下のデータフローを検証：

```
1. Google Sheets - Read Row(s)
   ↓
   {status, segment, abstract, pv, likes, ...}  ← row_number なし

2. Function - Add Row Numbers
   ↓
   {status, segment, abstract, pv, likes, ..., row_number: 2}  ← 追加

3. Split In Batches / Loop Over Items
   ↓
   各アイテムに row_number が含まれている

4. 処理ノード群
   ↓
   row_number を維持して伝播

5. Function - Validate Schema
   ↓
   {next_decision, ..., row_number: 2}  ← 維持されていることを確認

6. Google Sheets - Update Row
   matchingColumns または Range で row_number を使用
```

---

## 12. n8n MCP API 使用時の注意事項

### 🚨 Critical: n8n_update_full_workflow の必須パラメータ

#### ルール1: `name` パラメータは必須

```javascript
// ❌ エラー: name パラメータ不足
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "2mBYCQMjW2Vw1Xaa",
  nodes: [...],
  connections: {...}
})
// エラー: "Invalid request: request/body must have required property 'name'"

// ✅ 正しい: name パラメータを含める
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "2mBYCQMjW2Vw1Xaa",
  name: "WF-B: Analyze & Suggest Next Actions",  // 必須
  nodes: [...],
  connections: {...}
})
```

#### ルール2: 既存ワークフロー更新時のname取得

ワークフロー更新前に `n8n_get_workflow` で現在の name を取得して使用：

```javascript
// 1. 現在のワークフロー情報を取得
const workflow = await mcp__n8n-mcp__n8n_get_workflow({ id: "2mBYCQMjW2Vw1Xaa" });

// 2. 取得した name を使用して更新
await mcp__n8n-mcp__n8n_update_full_workflow({
  id: "2mBYCQMjW2Vw1Xaa",
  name: workflow.name,  // 既存の name を維持
  nodes: [...],
  connections: {...}
});
```

### n8n_update_partial_workflow の制限

#### 制限事項

`n8n_update_partial_workflow` は差分更新用のAPIだが、以下の制限がある：

1. **Diff engine エラー**: 複雑なノード構造変更で失敗することがある
2. **ノード追加/削除**: 新規ノード追加や既存ノード削除は失敗しやすい
3. **接続変更**: connections の変更は特にエラーが発生しやすい

#### 推奨事項

**複雑な更新には `n8n_update_full_workflow` を使用**:
- ノード追加・削除
- 接続構造の変更
- 複数ノードの同時更新

**`n8n_update_partial_workflow` は以下の場合のみ使用**:
- 単一ノードのパラメータ変更
- シンプルな設定値の更新

### API呼び出しベストプラクティス

```javascript
// 推奨: 完全なワークフロー更新フロー
async function updateWorkflow(workflowId, updates) {
  // 1. 現在の状態を取得
  const current = await mcp__n8n-mcp__n8n_get_workflow({ id: workflowId });

  // 2. ノードと接続を更新
  const updatedNodes = applyNodeUpdates(current.nodes, updates);
  const updatedConnections = applyConnectionUpdates(current.connections, updates);

  // 3. Full Update で反映（name を含める）
  await mcp__n8n-mcp__n8n_update_full_workflow({
    id: workflowId,
    name: current.name,
    nodes: updatedNodes,
    connections: updatedConnections
  });

  // 4. 検証
  const result = await mcp__n8n-mcp__n8n_validate_workflow({ id: workflowId });
  if (result.errors?.length > 0) {
    throw new Error(`Validation failed: ${JSON.stringify(result.errors)}`);
  }
}
```

---

**このナレッジベースは実際のワークフロー構築経験から抽出されたものです。**
**新しいワークフロー構築時にこのドキュメントを参照し、同じ過ちを繰り返さないようにしてください。**

**最終更新**: 2025-11-25

**出典**:
- WF6 (tkmG4YSZyi5RLiPw): note記事自動生成 - HTTP Request Node v4設定、n8n式構文 (Execution 816-823)
- WF7 (Phase1-5 + File Server 6 workflows): SNS動画生成パイプライン - Railway Webhook制限対応、File Server設計パターン (2025-11-01)
- WF-A (7isXtFeTvjKuW5GD): Editorial Ideas→Note Draft生成 - Error Handler実装パターン、n8nエラーデータ構造制限対応 (2025-11-22, Version 47)
- WF7 Phase4 (xvlnFeJJwHKMHBwK): Execute Commandノード改行問題、トラブルシューティング (Execution 101→146, 2025-11-04)
- WF-B (2mBYCQMjW2Vw1Xaa): AI Agent分析パイプライン - AI Agent JSON出力パース処理、Code ノード構文制限、プロンプト式評価パターン (Execution 3952-3962, 2025-11-24)
- WF-B (2mBYCQMjW2Vw1Xaa): Google Sheets Update 0件出力問題、row_number伝播問題、並列接続パターン、n8n MCP API注意事項 (Execution 4199+, 2025-11-25)
