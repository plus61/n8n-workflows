# WF7 Phase4 最終総合テスト計画書

**作成日**: 2025-11-09  
**対象**: WF7 Phase4a/4b/4c 統合テスト  
**前提**: Phase4a/4b/4c全ての修正が完了  
**目的**: Phase4全体のE2Eテストを実施し、本番環境への移行準備を完了する

---

## 📋 テスト概要

### テスト範囲

WF7 Phase4の全フェーズを統合したE2Eテストを実施します：

1. **Phase4a**: スライド画像生成（7枚）
2. **Phase4b**: 動画生成（7本）
3. **Phase4c**: 動画結合（1本の完成動画）

### テスト目標

- ✅ Phase4a/4b/4cが正常に連携動作することを確認
- ✅ データフローが正しく機能することを確認
- ✅ エラーハンドリングが適切に動作することを確認
- ✅ パフォーマンス目標を達成することを確認
- ✅ 最終動画の品質が基準を満たすことを確認

---

## 📊 各フェーズの評価結果

### 評価サマリー

| フェーズ | 単体テスト | 統合テスト | 評価 |
|---------|-----------|-----------|------|
| **Phase4a** | ✅ 成功 | ✅ 成功 | ✅ 合格 |
| **Phase4b** | - | ⏸️ 修正後テスト待ち | ✅ 修正完了 |
| **Phase4c** | ✅ 成功 | ⏸️ 未実行 | ✅ 合格 |

### 現在の状況

#### Phase4a: ✅ 合格
- **単体テスト**: ✅ 成功
- **統合テスト**: ✅ 成功
- **確認事項**: 統合テストで7枚のスライド生成を確認
- **状態**: 本番環境への移行準備完了

#### Phase4b: ✅ 修正完了
- **単体テスト**: 未実施
- **統合テスト**: ⏸️ 修正後テスト待ち
- **修正内容**: 
  - ✅ 親ワークフロー（ID: `r9Sp5n0mkUCcH8cw`）のPhase4b呼び出しをHTTP RequestからExecute Sub-workflowに変更
  - ✅ ノード名: `HTTP Request - Call Phase4b` → `Execute Sub-workflow - Phase4b`
  - ✅ ワークフローID: `wHaKi98mTlUvFIOR` を設定
  - ✅ データマッピング設定:
    - `script_id`: `={{ $('Set - Phase4a Payload New').item.json.script_id }}`
    - `slides_metadata`: `={{ $('Set - Phase4a Payload New').item.json.slides_metadata }}`
- **状態**: 修正完了、統合テスト実施待ち

#### Phase4c: ✅ 合格（統合テスト未実行）
- **単体テスト**: ✅ 成功
- **統合テスト**: ⏸️ 未実行
- **確認事項**: 単体テストで全フローが正常動作を確認
- **状態**: Phase4b修正後に統合テストを実施予定

### 次のアクション

1. **Phase4bの修正** ✅ 完了
   - ✅ 親ワークフロー（`r9Sp5n0mkUCcH8cw`）のPhase4b呼び出しをHTTP RequestからExecute Sub-workflowに変更
   - ✅ データマッピング設定を確認・修正
     - `script_id`: `={{ $('Set - Phase4a Payload New').item.json.script_id }}`
     - `slides_metadata`: `={{ $('Set - Phase4a Payload New').item.json.slides_metadata }}`
   - ✅ ワークフローID: `wHaKi98mTlUvFIOR` を設定
   - ⏸️ 修正後の統合テストを実施（次ステップ）

2. **Phase4cの統合テスト**
   - Phase4b修正完了後、Phase4a → Phase4b → Phase4cのE2Eテストを実施
   - 最終動画の生成とGoogle Driveアップロードを確認

3. **最終総合テスト**
   - 全フェーズが正常に動作することを確認
   - パフォーマンステストと品質確認テストを実施

### Phase4b修正後の統合テスト実施手順

**修正内容の確認**:
- ✅ 親ワークフロー `r9Sp5n0mkUCcH8cw` のPhase4b呼び出しがExecute Sub-workflowに変更済み
- ✅ データマッピングが正しく設定されている
- ✅ Phase4bワークフローID `wHaKi98mTlUvFIOR` が設定されている

**テスト実行準備**:
1. 親ワークフローがn8nにインポートされ、アクティブになっているか確認
2. Phase4bワークフローがアクティブになっているか確認
3. テスト用NotionページIDを準備: `2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9`

**テスト実行**:

方法1: スクリプトを使用（推奨）
```bash
./test-phase4b-fixed-e2e.sh [NOTION_PAGE_ID]
```

方法2: curlコマンドを直接実行
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"
  }'
```

**確認項目**:
- ✅ Phase4aが正常に実行され、7枚のスライドが生成される
- ✅ Phase4bがExecute Sub-workflowで正常に呼び出される
- ✅ Phase4bが正常に実行され、7本の動画が生成される
- ✅ Phase4cが正常に実行され、1本の完成動画が生成される
- ✅ Google Driveに最終動画がアップロードされる
- ✅ Notion DBが正しく更新される

---

## 🎯 前提条件チェックリスト

### 環境準備

- [ ] n8n UIにアクセス可能: `https://n8n-python-production-344b.up.railway.app/`
- [ ] 親ワークフローID `r9Sp5n0mkUCcH8cw` が存在し、アクティブ
- [ ] Phase4aワークフローID `LYPbvJfkMzLlhc6t` が存在し、アクティブ
- [ ] Phase4bワークフローID `wHaKi98mTlUvFIOR` が存在し、アクティブ
- [ ] Phase4cワークフローID `chPw11OY5sex6d9I` が存在し、アクティブ

### 認証情報確認

- [ ] **FAL API Key** (Header Auth)
  - Credential ID: `voV5kURaCkiUjLTZ`
  - Header Name: `Authorization`
  - Value: `Key YOUR_FAL_API_KEY`
  - クレジット残高確認

- [ ] **Google Drive OAuth2**
  - Credential ID: `plniYONxQ1iPNoAi`
  - アップロード先フォルダへのアクセス権限あり

- [ ] **Notion API**
  - Credential ID: `y89xQdP2gCTcdyup`
  - 対象データベースへのアクセス権限あり

### データ準備

- [ ] テスト用NotionページIDを準備
- [ ] Notionページに必要なデータが設定済み
  - Script JSON（7セクション分のテキスト）
  - Assets JSON（ブランドカラー、Duration Config、Motion Prompts、Visual Elements）
  - Status: `approved` または `pending`

---

## 🧪 テストケース

### テストケース1: 正常系E2Eテスト

**目的**: Phase4a → 4b → 4cの全フローが正常に動作することを確認

**実行手順**:

1. **Webhook呼び出し**
   ```bash
   curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
     -H "Content-Type: application/json" \
     -d '{
       "notionPageId": "YOUR_TEST_NOTION_PAGE_ID"
     }'
   ```

2. **実行フロー確認**
   - Webhook受信 → Notion API呼び出し
   - Execute Phase4a → スライド生成（7枚）
   - Execute Phase4b → 動画生成（7本）
   - Execute Phase4c → 動画結合（1本）
   - Google Drive Upload → Notion更新 → Webhook応答

**期待結果**:

| フェーズ | 期待出力 | 確認方法 |
|---------|---------|---------|
| **Phase4a** | `success: true`, `slides_count: 7`, `slides_metadata: [7要素]` | n8n実行ログ |
| **Phase4b** | `success: true`, `videos_count: 7`, `videos_metadata: [7要素]` | n8n実行ログ |
| **Phase4c** | `success: true`, `final_video_url: "https://drive.google.com/..."` | n8n実行ログ |
| **Google Drive** | ファイルアップロード成功 | Google Drive確認 |
| **Notion** | Status更新、Video URL記録 | Notion DB確認 |

**成功基準**:

- ✅ Phase4aで7枚のスライド画像が生成される
- ✅ Phase4bで7本の動画が生成される
- ✅ Phase4cで1本の完成動画が生成される
- ✅ Google Driveに最終動画がアップロードされる
- ✅ Notion DBが正しく更新される
- ✅ Webhook応答が成功を返す

---

### テストケース2: データフロー検証

**目的**: 各フェーズ間のデータ受け渡しが正しく機能することを確認

**確認項目**:

1. **Notion → Phase4a**
   - `script_id`が正しく渡される
   - `scriptData`が正しい形式で渡される
   - 7セクション分のテキストが含まれる

2. **Phase4a → Phase4b**
   - `slides_metadata`が7要素の配列で渡される
   - 各要素に`section`, `duration`, `image_url`, `motion_prompt`が含まれる
   - 順序が正しい（hook → intro → point1 → point2 → point3 → summary → cta）

3. **Phase4b → Phase4c**
   - `videos_metadata`が7要素の配列で渡される
   - 各要素に`section`, `duration`, `video_url`が含まれる
   - 順序が正しい（hook → intro → point1 → point2 → point3 → summary → cta）

4. **Phase4c → Google Drive/Notion**
   - `final_video_url`が正しく生成される
   - `total_duration`が正しく計算される（約73秒）

**確認方法**:

- n8n実行ログで各ノードの入出力を確認
- Execute Sub-workflowノードの`workflowInputs.mapping`を確認
- 各サブワークフローの出力データ構造を確認

---

### テストケース3: エラーハンドリングテスト

**目的**: 各フェーズでエラーが発生した場合の処理が適切に動作することを確認

#### 3.1 Phase4a失敗時のテスト

**シミュレーション**: Phase4aが`success: false`を返す

**期待動作**:
- IFノードでエラー検知
- エラー時Notion更新実行（Status: `Error`, errorMessage設定）
- エラー時Webhook応答実行（`success: false`, `error`フィールド含む）
- Phase4b/4cは実行されない

#### 3.2 Phase4b失敗時のテスト

**シミュレーション**: Phase4bが`success: false`を返す（例: FAL APIタイムアウト）

**期待動作**:
- IFノードでエラー検知
- エラー時Notion更新実行
- エラー時Webhook応答実行
- Phase4cは実行されない

#### 3.3 Phase4c失敗時のテスト

**シミュレーション**: Phase4cが`success: false`を返す（例: 動画ダウンロード失敗）

**期待動作**:
- IFノードでエラー検知
- エラー時Notion更新実行
- エラー時Webhook応答実行

**確認方法**:

- 各フェーズで意図的にエラーを発生させる
- エラーハンドリングノードが正しく実行されることを確認
- Notion DBとWebhook応答にエラー情報が記録されることを確認

---

### テストケース4: パフォーマンステスト

**目的**: 処理時間とリソース使用量が目標値を満たすことを確認

**測定項目**:

| 項目 | 目標値 | 測定方法 |
|------|--------|---------|
| **Phase4a処理時間** | <30秒 | n8n実行ログ |
| **Phase4b処理時間** | <5分 | n8n実行ログ |
| **Phase4c処理時間** | <2分 | n8n実行ログ |
| **全体処理時間** | <8分 | Webhook受信から応答まで |
| **メモリ使用量** | <500MB | Railwayメトリクス |

**測定手順**:

1. Webhook呼び出し時刻を記録
2. 各フェーズの開始・終了時刻をn8n実行ログで確認
3. Railwayメトリクスでメモリ使用量を確認
4. Webhook応答時刻を記録

**成功基準**:

- ✅ 全ての項目が目標値を満たす

---

### テストケース5: 品質確認テスト

**目的**: 最終動画の品質が基準を満たすことを確認

**確認項目**:

1. **動画の基本情報**
   - 再生時間: 約73秒（hook: 3s + intro: 10s + point1-3: 13s×3 + summary: 20s + cta: 7s）
   - ファイルサイズ: <50MB（推奨）
   - フォーマット: MP4
   - 解像度: 1920x1080（推奨）

2. **動画の品質**
   - テキスト可読性: 全てのテキストが読み取れる
   - 動きの自然さ: ズーム、スライド、フェードが自然
   - 結合の滑らかさ: セクション間のトランジションがスムーズ
   - 音声: なし（Phase 3で追加予定）

3. **スライド画像の品質**
   - ブランドカラーが正しく適用されている
   - テキスト配置が正確
   - アイコン・図解が適切に配置されている

**確認方法**:

- Google Driveから動画をダウンロードして再生
- 各セクションの内容を確認
- 動画編集ソフトで詳細を確認（必要に応じて）

**成功基準**:

- ✅ 動画の基本情報が期待値と一致
- ✅ テキストが全て読み取れる
- ✅ 動きが自然で滑らか
- ✅ 結合がスムーズ

---

## 📊 テスト実行記録テンプレート

```yaml
テスト実行日時: YYYY-MM-DD HH:MM:SS
テスト種別: 最終総合テスト
テストケース: テストケース1-5

# テストケース1: 正常系E2Eテスト
正常系E2Eテスト:
  実行ID: [n8n実行ID]
  実行ステータス: ✅ 成功 / ❌ 失敗
  実行時間: X分Y秒
  
  Phase4a:
    実行時間: X秒
    slides_count: 7
    success: true / false
    エラー: [あれば記録]
  
  Phase4b:
    実行時間: X秒
    videos_count: 7
    success: true / false
    エラー: [あれば記録]
  
  Phase4c:
    実行時間: X秒
    final_video_url: https://drive.google.com/...
    success: true / false
    エラー: [あれば記録]
  
  Google Drive:
    アップロード成功: true / false
    ファイルID: [ファイルID]
    エラー: [あれば記録]
  
  Notion:
    更新成功: true / false
    Status: [更新後のステータス]
    エラー: [あれば記録]

# テストケース2: データフロー検証
データフロー検証:
  Notion → Phase4a: ✅ / ❌
  Phase4a → Phase4b: ✅ / ❌
  Phase4b → Phase4c: ✅ / ❌
  Phase4c → Google Drive/Notion: ✅ / ❌
  問題点: [あれば記録]

# テストケース3: エラーハンドリングテスト
エラーハンドリングテスト:
  Phase4a失敗時: ✅ / ❌
  Phase4b失敗時: ✅ / ❌
  Phase4c失敗時: ✅ / ❌
  問題点: [あれば記録]

# テストケース4: パフォーマンステスト
パフォーマンステスト:
  Phase4a処理時間: X秒 (目標: <30秒)
  Phase4b処理時間: X秒 (目標: <5分)
  Phase4c処理時間: X秒 (目標: <2分)
  全体処理時間: X分Y秒 (目標: <8分)
  メモリ使用量: XMB (目標: <500MB)
  目標達成: ✅ / ❌

# テストケース5: 品質確認テスト
品質確認テスト:
  再生時間: X秒 (期待: 約73秒)
  ファイルサイズ: XMB (期待: <50MB)
  フォーマット: MP4
  解像度: [解像度]
  テキスト可読性: ✅ 良好 / ⚠️ 要改善 / ❌ 不良
  動きの自然さ: ✅ 良好 / ⚠️ 要改善 / ❌ 不良
  結合の滑らかさ: ✅ 良好 / ⚠️ 要改善 / ❌ 不良
  品質評価: ✅ 良好 / ⚠️ 要改善 / ❌ 不良

総合評価: ✅ 合格 / ⚠️ 要修正 / ❌ 不合格
備考: [その他の気づき]
```

---

## 🐛 トラブルシューティング

### 問題1: Execute Sub-workflowノードでデータが渡らない

**症状**: Phase4a/4b/4cのサブワークフローが正しく実行されない

**確認事項**:
- `workflowInputs.mapping`の設定を確認
- サブワークフローの入力データ契約を確認
- n8n MCPツールで検証: `validate_node_operation`

**対処法**:
- データマッピング設定を修正
- サブワークフローの入力データ契約を確認

---

### 問題2: Phase4bでFAL APIタイムアウト

**症状**: Phase4bの実行が長時間かかる、またはタイムアウトする

**確認事項**:
- FAL APIのクレジット残高を確認
- 動画の長さ・ファイルサイズを確認
- ポーリング設定を確認

**対処法**:
- FAL APIのクレジットを追加
- 動画の長さを調整
- ポーリングのリトライ回数を増やす

---

### 問題3: Phase4cで動画URL取得失敗

**症状**: Phase4cで動画URLが取得できない

**確認事項**:
- Phase4bの出力データ構造を確認
- FAL APIのレスポンス構造を確認
- `tracks`形式のペイロードが正しく設定されているか確認

**対処法**:
- Phase4cの動画URL取得ロジックを確認
- `tracks`形式のペイロード設定を確認
- 関連ドキュメント: `docs/testing/WF7-Phase4c-実行1032-1036-修正まとめ.md`

---

### 問題4: Google Driveアップロード失敗

**症状**: Google Driveへのアップロードが失敗する

**確認事項**:
- Google Drive OAuth2認証を確認
- フォルダIDを確認
- ファイルサイズを確認

**対処法**:
- Google Drive OAuth2認証を再実行
- フォルダIDを確認
- ファイルサイズを確認（50MB以下推奨）

---

### 問題5: Notion DB更新失敗

**症状**: Notion DBの更新が失敗する

**確認事項**:
- Notion API認証を確認
- Page ID（script_id）が有効か確認
- プロパティ名が正確か確認

**対処法**:
- Notion API認証を確認
- Page IDを確認
- プロパティ名を確認

---

## 📝 テスト実行手順

### Step 0: Phase4b修正の確認（修正後テスト実施前）

1. **親ワークフローの修正確認**
   - 親ワークフロー `r9Sp5n0mkUCcH8cw` をn8n UIで開く
   - `Execute Sub-workflow - Phase4b` ノードが存在することを確認
   - ワークフローIDが `wHaKi98mTlUvFIOR` に設定されていることを確認
   - データマッピング設定を確認:
     - `script_id`: `={{ $('Set - Phase4a Payload New').item.json.script_id }}`
     - `slides_metadata`: `={{ $('Set - Phase4a Payload New').item.json.slides_metadata }}`

2. **ワークフローのインポート確認**
   - 修正済みワークフロー `wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json` がn8nにインポートされているか確認
   - ワークフローがアクティブになっているか確認

### Step 1: 事前準備

1. **前提条件チェックリストを確認**
   - 環境準備項目を全て確認
   - 認証情報を確認
   - テストデータを準備

2. **ワークフローの状態確認**
   - 親ワークフローがアクティブか確認
   - 各サブワークフローがアクティブか確認
   - ノードの接続を確認
   - Phase4bがExecute Sub-workflowで呼び出されていることを確認

### Step 2: テストケース1実行（正常系E2Eテスト）

1. **Webhook呼び出し**
   ```bash
   curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
     -H "Content-Type: application/json" \
     -d '{
       "notionPageId": "YOUR_TEST_NOTION_PAGE_ID"
     }'
   ```

2. **実行ログの確認**
   - n8n UIで実行ログを確認
   - 各フェーズの実行状況を確認
   - エラーがあれば記録

3. **結果の確認**
   - Google Driveに最終動画がアップロードされているか確認
   - Notion DBが正しく更新されているか確認
   - Webhook応答を確認

### Step 3: テストケース2実行（データフロー検証）

1. **各ノードの入出力を確認**
   - Execute Sub-workflowノードの入出力を確認
   - データマッピングが正しいか確認

2. **データ構造の確認**
   - Phase4aの出力データ構造を確認
   - Phase4bの出力データ構造を確認
   - Phase4cの出力データ構造を確認

### Step 4: テストケース3実行（エラーハンドリングテスト）

1. **各フェーズで意図的にエラーを発生させる**
   - Phase4aでエラーを発生させる方法を検討
   - Phase4bでエラーを発生させる方法を検討
   - Phase4cでエラーを発生させる方法を検討

2. **エラーハンドリングの動作を確認**
   - IFノードが正しくエラーを検知するか確認
   - エラー時Notion更新が実行されるか確認
   - エラー時Webhook応答が実行されるか確認

### Step 5: テストケース4実行（パフォーマンステスト）

1. **処理時間の測定**
   - 各フェーズの処理時間を記録
   - 全体処理時間を記録

2. **リソース使用量の確認**
   - Railwayメトリクスでメモリ使用量を確認

### Step 6: テストケース5実行（品質確認テスト）

1. **動画の基本情報を確認**
   - Google Driveから動画をダウンロード
   - 再生時間、ファイルサイズ、フォーマットを確認

2. **動画の品質を確認**
   - 動画を再生して品質を確認
   - テキスト可読性、動きの自然さ、結合の滑らかさを確認

### Step 7: テスト結果の記録

1. **テスト実行記録テンプレートに記録**
   - 各テストケースの結果を記録
   - 問題点があれば記録

2. **総合評価を実施**
   - 全てのテストケースが成功したか確認
   - 問題点があれば修正計画を立てる

---

## ✅ 成功基準

以下の全てが満たされた場合、最終総合テストは成功とみなします：

### 必須項目

- ✅ テストケース1（正常系E2Eテスト）が成功
- ✅ テストケース2（データフロー検証）が成功
- ✅ テストケース3（エラーハンドリングテスト）が成功
- ✅ テストケース4（パフォーマンステスト）が目標値を達成
- ✅ テストケース5（品質確認テスト）が基準を満たす

### 品質基準

- ✅ 最終動画が正常に生成される
- ✅ テキストが全て読み取れる
- ✅ 動きが自然で滑らか
- ✅ 結合がスムーズ
- ✅ エラーハンドリングが適切に動作する

---

## 📚 関連ドキュメント

- `/docs/implementation/WF7-Phase4-簡素化実装ガイド.md`: 実装ガイド
- `/docs/testing/WF7-Phase4c-実行1032-1036-修正まとめ.md`: Phase4c修正まとめ
- `/docs/testing/wf7-phase4c-e2e-test-execution-guide.md`: Phase4c E2Eテストガイド
- `/docs/testing/wf7-phase4ab-integrated-e2e-test-report.md`: Phase4ab統合テストレポート
- `/docs/implementation/WF7-Phase4-FAL実装計画書.md`: Phase4実装計画書

---

**作成者**: AI Assistant (Claude Sonnet 4.5)  
**最終更新**: 2025-11-09  
**次回更新**: テスト実行完了時

## 🔧 テスト実行スクリプト

Phase4b修正後の統合テストを実行するためのスクリプトが用意されています：

**スクリプト**: `/test-phase4b-fixed-e2e.sh`

**使用方法**:
```bash
# デフォルトのNotion Page IDを使用
./test-phase4b-fixed-e2e.sh

# カスタムNotion Page IDを指定
./test-phase4b-fixed-e2e.sh YOUR_NOTION_PAGE_ID
```

**スクリプトの機能**:
- Webhook呼び出しの実行
- HTTPステータスコードの確認
- レスポンスのJSONフォーマット表示
- 実行ログのファイル出力
- 結果判定と次のステップの表示

**ログファイル**:
- 実行ログは `test-phase4b-fixed-e2e-YYYYMMDD_HHMMSS.log` に保存されます

