# WF7 Phase4 動画レンダリング処理 要件定義書

**プロジェクト**: MEO集客自動化プロジェクト
**ドキュメント作成日**: 2025-11-11
**バージョン**: v2.0（全面再設計）
**目的**: Phase4a（スライド生成）完了後の動画レンダリング処理を5原則に則り再設計

---

## 📋 目次

1. [背景と目的](#背景と目的)
2. [技術選定・要件定義の原則](#技術選定要件定義の原則)
3. [現状の課題](#現状の課題)
4. [理想の運用フロー](#理想の運用フロー)
5. [機能要件](#機能要件)
6. [非機能要件](#非機能要件)
7. [技術スタック](#技術スタック)
8. [実装フェーズ](#実装フェーズ)
9. [成功基準](#成功基準)

---

## 背景と目的

### 背景

**Phase4の現状**:
- ✅ **Phase4a**: スライド画像生成（Pillow）- **完成**
- ❌ **Phase4b**: Image-to-Video変換（FAL.ai）- **複雑化・エラー多発**
- ❌ **Phase4c**: 動画結合（FFmpeg）- **未完成**

**現状の問題点**:
1. **実装の複雑化**:
   - Phase4関連ドキュメント: 29件（過剰）
   - Phase4bワークフロー: 検証エラー6件、警告16件
   - 19🍅投入したが完成せず（2025-11-02失敗ログより）

2. **原則1違反: 事例不足**:
   - Railway Python + FFmpegレンダリング: 事例少、エラー多発
   - FAL.ai + n8n統合: トラブルシューティング困難

3. **原則5違反: タイムボックス超過**:
   - 当初見積: 6🍅（Phase4b: 2🍅、Phase4c: 1🍅）
   - 実績: 19🍅+（進行中）
   - 判断: 8🍅時点で代替案検討すべきだった

**ビジネス上の影響**:
- 動画生成パイプライン未完成 → Phase5まで到達不可
- 開発リソース消費 → 他機能開発の遅延
- 複雑化による保守困難性 → 将来の改善コスト増大

### 目的

**達成したいゴール**:
1. **Phase4の完成**: スライド画像 → 完成動画への変換を確実に実現
2. **5原則遵守**: 事例ベース選定、既存資産活用、適切な内製化範囲設定
3. **シンプル化**: 保守可能な実装（ドキュメント5件以内、エラー0件目標）

**期待効果**:
- 開発完了: Phase4完成 → Phase5連携 → WF7パイプライン全体完成
- 工数削減: 現行19🍅+ → 新設計5🍅以内（74%削減）
- 保守性向上: ドキュメント29件 → 5件以内（83%削減）

---

## 技術選定・要件定義の原則

**本要件定義は標準化ナレッジ5原則に厳密に従う**

### ❌ 原則1違反の検出: 事例ベース選定の徹底

**現行実装の問題**:
| 技術 | 事例状況 | 判定 | 理由 |
|------|---------|------|------|
| Railway Python + FFmpeg | 事例少 | ❌ 不採用 | 19🍅投入も未完成、トラブル多発 |
| FAL.ai + n8n統合 | 事例少 | ❌ 不採用 | エラーハンドリング複雑、検証エラー6件 |
| n8n Code node FFmpeg | 事例少 | ❌ 不採用 | ファイルシステムアクセス制約 |

**失敗事例からの学び（標準化ナレッジより）**:
- Phase 4ビルド問題: Railway Python環境でのレンダリング実装
- 19🍅投入したが完成せず、深夜01:28まで作業継続
- **教訓**: 事例不足の技術は早期に見切る

### ✅ 原則1に基づく新技術選定

**採用基準**: 実装事例3件以上、成功事例複数確認、公式ドキュメント充実

**候補技術の事例調査**:

#### 候補A: Creatomate（外部動画レンダリングSaaS）
- ✅ **事例**: n8n公式統合あり、コミュニティ事例多数
- ✅ **ドキュメント**: 公式n8nノードあり、サンプルコード充実
- ✅ **成功事例**: Zapier、Make.com等で実績
- ⚠️ **コスト**: 月額$39+（従量課金）
- **判定**: 採用候補（事例十分、高コストだが確実性重視）

#### 候補B: Cloudinary Video API
- ✅ **事例**: n8n統合事例あり、公式HTTP Requestノードで実績
- ✅ **ドキュメント**: REST API充実、n8nサンプルあり
- ✅ **成功事例**: 大規模サービスで採用実績
- ✅ **コスト**: 無料枠あり、従量課金で透明性高い
- **判定**: 採用候補（事例十分、コスト効率良好）

#### 候補C: Runway ML API
- ⚠️ **事例**: n8n統合事例少（1-2件）
- ⚠️ **ドキュメント**: HTTP API充実だがn8n事例少
- ✅ **品質**: 高品質だが事例不足
- **判定**: 要検証（原則1の「⚠️要検証」該当）

#### 候補D: 外部Python FastAPI（Railway別プロジェクト）
- ❌ **事例**: ほぼなし（独自実装）
- ❌ **ドキュメント**: 自作必要
- ❌ **トラブルシューティング**: 独自実装のため困難
- **判定**: 不採用（原則1違反、既に19🍅消費した失敗パターン）

**選定結果**:
1. **第1候補**: Creatomate（確実性最優先）
2. **第2候補**: Cloudinary Video API（コスト効率とのバランス）

### ✅ 原則2: 既存資産の最大活用

**流用可能な既存コード**:
1. ✅ **Phase4a - スライド画像生成**（完成）
   - 既存: Pillowでスライド7枚生成、Cloudinaryアップロード
   - 流用: 100%（変更不要）

2. ✅ **Notion API統合パターン**（WF7全体で実績）
   - 既存: Notion DB読取・更新パターン確立
   - 流用: 100%（Phase4でも同じパターン適用）

3. ✅ **エラーハンドリング構造**（WF7 Phase1-3で実績）
   - 既存: 統一されたエラーハンドリング
   - 流用: 100%

**工数削減効果**:
- 新規フル実装: 20🍅（Phase4b: 10🍅、Phase4c: 10🍅）
- 既存資産活用: 5🍅（Phase4統合のみ）
- **削減率: 75%**

### ✅ 原則3: 内製化の本質理解

**内製化判断**:

| 機能 | 判断 | 理由 |
|------|------|------|
| スライド画像生成 | ✅ 内製化 | デザイン改善の高速PDCA必要（週次） |
| 動画レンダリング | ❌ 外部依存 | 変更頻度低、技術複雑度高、事例不足 |
| 動画メタデータ管理 | ✅ 内製化 | Notion統合、既存パターン活用 |

**判断根拠**:
- **動画レンダリング外部依存の理由**:
  1. 改善頻度: 低（月次レベル、スライドデザインほど頻繁でない）
  2. 実装難易度: 高（19🍅投入も未完成）
  3. 事例の有無: 少（原則1違反）
  4. **内製化メリット < 実装コスト**

- **Creatomate採用の正当性**:
  - 打席数（試行回数）: スライドデザイン >> 動画レンダリング設定
  - 改善サイクル: スライド（週次）vs レンダリング（月次）
  - 内製化による高速PDCA効果: レンダリングでは限定的

### ✅ 原則4: プロトタイプ駆動の要件定義

**Phase 1: クイックプロトタイプ（最大2🍅）**

**検証項目**:
1. [ ] Phase4a出力（スライド画像7枚）の取得確認（0.5🍅）
2. [ ] Creatomate/Cloudinary APIテスト呼び出し（1🍅）
3. [ ] 1枚のスライド画像 → 動画変換 → URL取得確認（0.5🍅）

**Go/No-Go判断基準**:
- ✅ **Go条件**:
  - API認証成功
  - 1枚のスライド → 動画変換成功
  - レスポンス時間 <2分/スライド
  - 生成動画品質: 1080p、音声なし、期待通り
- ❌ **No-Go条件**:
  - API認証失敗 → 代替API候補へ切替
  - 変換失敗率 >10% → 代替API候補へ切替
  - レスポンス時間 >3分/スライド → 仕様見直し

**代替案準備**:
- Creatomate失敗 → Cloudinary Video API
- Cloudinary失敗 → Runway ML API（要検証フェーズ実施）
- 全API失敗 → Phase4要件の根本見直し

### ✅ 原則5: タイムボックス方式の適用

**タイムボックス設定**:
- **最大工数**: 5🍅（プロトタイプ2🍅 + 本実装3🍅）
- **現行実績**: 19🍅+（超過）
- **判断**: 19🍅時点で既に3.8倍超過 → 早期に代替案へ切替必要だった

**中間評価ポイント**:
- **30%時点（1.5🍅）**: プロトタイプ完成 → API動作確認
  - ✅ Go: API正常動作、1枚変換成功
  - ❌ No-Go: 代替API候補へ即座に切替
- **50%時点（2.5🍅）**: Phase4b実装完了 → 7枚変換成功
  - ✅ Go: 7枚全変換成功、エラー率<5%
  - ❌ No-Go: 仕様簡素化または代替案検討
- **80%時点（4🍅）**: Phase4c実装完了 → E2Eテスト成功
  - ✅ Go: 残り1🍅でリリース可能
  - ❌ No-Go: MVP範囲を絞り込み、残機能は次フェーズへ

**Go/No-Go判断の厳格化**:
- 各評価ポイントで判断を明確化
- 深追いしない = 損切りの重要性
- 1.5🍅時点でNo-Go → 即座に代替案実行（0.5🍅ロス）
- 2.5🍅時点でNo-Go → 仕様見直し（1.5🍅ロス）

---

## 🔥 MCP対応確認（絶対ルール）

| サービス | MCP対応 | MCPサーバー | 採用理由 |
|---------|---------|-------------|----------|
| n8n | ✅ 対応 | n8n-mcp | Claude Codeから直接操作可能 |
| Notion | ✅ 対応 | notion (公式) | DB操作の自動化 |
| Creatomate | ⚠️ 部分対応 | HTTP Request経由 | n8n公式ノードあり、MCP直接対応なし |
| Cloudinary | ⚠️ 部分対応 | HTTP Request経由 | REST API充実、n8n事例多数 |

**MCP非対応の例外採用理由**:
- Creatomate/Cloudinary: n8n公式ノード/HTTP Requestノードで実績多数
- 事例が豊富（原則1）により例外採用
- MCP対応よりも「事例の豊富さ」を優先（原則1 > MCP対応）

---

## 現状の課題

### 課題1: Phase4b/4cの複雑化と未完成

**問題**:
- Phase4関連ドキュメント: 29件（過剰な複雑化）
- Phase4bワークフロー: 検証エラー6件、警告16件
- 実装工数: 19🍅投入も未完成（見積6🍅の3.2倍）

**影響**:
- Phase5連携不可 → WF7パイプライン未完成
- 保守困難性 → 将来の改善コスト増大
- 開発リソース枯渇 → 他機能開発遅延

### 課題2: 原則1違反 - 事例不足技術の採用

**問題**:
- Railway Python + FFmpegレンダリング: 事例少
- FAL.ai + n8n統合: トラブルシューティング困難
- 試行錯誤の時間 = プロジェクト遅延リスク（標準化ナレッジより）

**影響**:
- 深夜01:28まで作業継続（2025-11-02）
- 19🍅消費も完成せず
- 精神的疲弊 → モチベーション低下

### 課題3: 原則5違反 - タイムボックス超過

**問題**:
- 見積: 6🍅（Phase4b: 2🍅、Phase4c: 1🍅）
- 実績: 19🍅+（3.2倍超過）
- 8🍅時点でGo/No-Go判断すべきだった

**影響**:
- 損切りタイミング逸失
- 代替案検討の遅延
- 機会コスト増大

---

## 理想の運用フロー

### シーン1: Phase4動画生成（自動化後）

```
1. Phase4a完了: スライド画像7枚生成完了
   - 出力: slides_metadata[7] (Cloudinary URL付き)

2. Phase4b: 外部API（Creatomate/Cloudinary）呼び出し
   - n8n HTTP Request node × 7回（並列または逐次）
   - スライド画像URL → 動画変換API
   - レスポンス: 動画URL × 7本

3. Phase4c: 動画結合（外部API or 簡素化）
   - オプション1: Creatomate Concatenate API（1リクエストで結合）
   - オプション2: Cloudinary Video Concatenation（1リクエストで結合）
   - 出力: 最終動画URL

4. Phase4完了: Notion DB更新
   - Video URL保存
   - Status: "Rendered"

5. Phase5へ連携: メタデータ登録処理開始
```

**処理時間**: Phase4全体 <5分（並列処理の場合）

### シーン2: エラーハンドリング

```
1. API呼び出し失敗: リトライ3回（n8n標準機能）
2. 3回失敗後: エラーログ出力、Notion DB更新（Status: Error）
3. ユーザー通知: LINE通知 or Notion コメント
4. 手動介入: Phase4再実行 or 個別調査
```

**エラー率目標**: <5%（API信頼性依存）

---

## 機能要件

### 必須機能（MVP）

#### F1: Phase4a出力データの取得

**概要**: Phase4a完了後の`slides_metadata`を取得

**入力**:
- Phase4a出力: `slides_metadata[7]`
```json
[
  {
    "section": "hook",
    "image_url": "https://res.cloudinary.com/.../hook.png",
    "duration": 3,
    "motion_prompt": "...",
    "text": "..."
  },
  // ... 7要素
]
```

**処理**:
1. Simplified Orchestratorから`slides_metadata`受け取り
2. データ検証（7要素、全image_url存在確認）

**出力**:
- 検証済み`slides_metadata[7]`

**成功基準**:
- データ検証成功率: 100%
- 処理時間: <1秒

---

#### F2: スライド画像 → 動画変換（外部API）

**概要**: Creatomate/Cloudinary APIでスライド画像を動画化

**入力**:
- `slides_metadata[7]` (F1の出力)

**処理**:

##### オプション1: Creatomate API
```javascript
// n8n HTTP Request node
{
  method: "POST",
  url: "https://api.creatomate.com/v1/renders",
  authentication: "headerAuth", // API Key
  body: {
    template_id: "TEMPLATE_ID",
    modifications: {
      "image-1": slides_metadata[0].image_url,
      "duration-1": slides_metadata[0].duration
    }
  }
}
```

##### オプション2: Cloudinary Video API
```javascript
// n8n HTTP Request node
{
  method: "POST",
  url: "https://api.cloudinary.com/v1_1/CLOUD_NAME/video/upload",
  authentication: "genericCredentialType",
  body: {
    file: slides_metadata[0].image_url,
    resource_type: "video",
    eager: [
      { duration: slides_metadata[0].duration }
    ]
  }
}
```

**並列処理 vs 逐次処理**:
- **並列**: 7本同時変換（処理時間短縮）
- **逐次**: 1本ずつ変換（API負荷軽減、エラーハンドリング容易）
- **推奨**: プロトタイプで決定（API制限による）

**出力**:
```json
{
  "videos_metadata": [
    {
      "section": "hook",
      "video_url": "https://cdn.creatomate.com/.../hook.mp4",
      "duration": 3,
      "status": "completed"
    },
    // ... 7要素
  ]
}
```

**成功基準**:
- 変換成功率: ≥95%
- 処理時間: <2分/スライド（並列時は<3分/全7本）
- 動画品質: 1080p、MP4形式

---

#### F3: 動画結合（外部API）

**概要**: 7本の動画を1本に結合

##### オプション1: Creatomate Concatenate API
```javascript
{
  method: "POST",
  url: "https://api.creatomate.com/v1/renders",
  body: {
    template_id: "CONCATENATE_TEMPLATE_ID",
    modifications: {
      "videos": videos_metadata.map(v => v.video_url)
    }
  }
}
```

##### オプション2: Cloudinary Video Concatenation
```javascript
{
  method: "POST",
  url: "https://api.cloudinary.com/v1_1/CLOUD_NAME/video/concatenate",
  body: {
    videos: videos_metadata.map(v => ({ public_id: extractPublicId(v.video_url) })),
    output_public_id: `final_video_${script_id}`
  }
}
```

##### オプション3: 簡素化（結合なし）
- 7本の動画URLをそのままNotion DBに保存
- Phase5で動画結合処理を実装（または手動結合）
- **メリット**: Phase4完成を最優先、Phase5への連携確保

**出力**:
```json
{
  "final_video_url": "https://cdn.creatomate.com/.../final_video.mp4",
  "total_duration": 21,
  "video_size_mb": 15.3,
  "status": "completed"
}
```

**成功基準**:
- 結合成功率: ≥95%
- 処理時間: <2分
- 動画品質: 1080p、MP4形式、音声なし

---

#### F4: Notion DB更新

**概要**: 最終動画URLをNotion DBに保存

**入力**:
- `final_video_url` (F3の出力)
- `script_id`

**処理**:
1. Notion API PATCH呼び出し
2. プロパティ更新:
   - `Video URL`: final_video_url
   - `Status`: "Rendered"
   - `Rendered At`: 現在時刻

**出力**:
- Notion DB更新完了

**成功基準**:
- 更新成功率: 100%
- 処理時間: <3秒

---

## 非機能要件

### 性能要件

- **Phase4全体処理時間**: <5分（並列処理時）
- **API呼び出しタイムアウト**: 2分/リクエスト
- **リトライ設定**: 3回（n8n標準機能）
- **エラー率**: <5%

### 信頼性要件

- **稼働率**: 95%以上（外部API依存）
- **データ整合性**: Notion DB更新の100%保証
- **エラーハンドリング**:
  - API失敗 → リトライ3回
  - 3回失敗 → エラーログ、Notion更新、通知

### 操作性要件

- **手動介入不要**: Phase4a完了 → Phase4完了まで完全自動
- **エラー通知**: LINE/Notionコメント（Phase5実装予定）

### 保守性要件

- **ドキュメント**: 5件以内（現行29件から83%削減）
- **ワークフロー検証**: エラー0件、警告5件以内
- **設定変更時間**: <10分（API Key変更、テンプレート変更）

---

## 技術スタック

### 技術選定（原則1-5に基づく）

**選定プロセス**:
1. **🔥 MCP対応状況**: Creatomate/Cloudinary共に部分対応（HTTP Request経由）
2. **事例調査**: Creatomate（n8n公式ノード）、Cloudinary（コミュニティ事例多数）
3. **既存資産**: Phase4a（100%流用）、Notion統合（100%流用）
4. **内製化判断**: レンダリングは外部依存（改善頻度低、実装難易度高）
5. **プロトタイプ**: 2🍅でAPI動作確認

**採用技術**:

```yaml
プラットフォーム: n8n (Railway)
MCP対応: ✅ 対応（n8n-mcp）

Phase4a:
  技術: Pillow + Cloudinary
  MCP対応: ⚠️ 部分対応
  ステータス: ✅ 完成（変更不要）

Phase4b - 第1候補: Creatomate
  MCP対応: ⚠️ 部分対応（n8n公式ノード）
  API: REST API v1
  事例: ✅ 豊富（n8n公式、コミュニティ多数）
  コスト: 月額$39+ (従量課金)
  選定理由: 確実性最優先、n8n公式ノードで実績

Phase4b - 第2候補: Cloudinary Video API
  MCP対応: ⚠️ 部分対応（HTTP Request）
  API: REST API v1
  事例: ✅ 豊富（大規模サービス採用実績）
  コスト: 無料枠あり、従量課金透明
  選定理由: コスト効率、柔軟性

Phase4c:
  オプション1: Creatomate Concatenate API
  オプション2: Cloudinary Video Concatenation
  オプション3: 簡素化（結合なし、7本URL保存）

データベース: Notion
MCP対応: ✅ 対応（notion公式）
```

**選定理由（原則に基づく）**:
- **原則1**: Creatomate/Cloudinary共に事例豊富、公式ドキュメント充実
- **原則2**: Phase4a完成品100%流用、Notion統合パターン100%流用
- **原則3**: レンダリングは外部依存（改善頻度低、内製化メリット小）
- **原則4**: 2🍅プロトタイプで実現可能性確認
- **原則5**: 5🍅タイムボックス、各評価ポイントでGo/No-Go判断

**不採用とした技術**:
| 技術 | 不採用理由 | 代替案 |
|------|-----------|--------|
| FAL.ai | 事例少（原則1違反）+ 複雑化 | Creatomate（事例豊富） |
| Railway Python FFmpeg | 事例少（原則1違反）+ 19🍅未完成 | Cloudinary（事例豊富） |
| n8n Code node FFmpeg | ファイルシステム制約 | 外部API（制約なし） |
| Runway ML API | 事例少（要検証レベル） | プロトタイプ失敗時の次候補 |

---

## 実装フェーズ

### Phase 1: プロトタイプ（最大2🍅）

**目標**: 技術的実現可能性の検証

**検証項目**:
- [ ] **1.1 API認証テスト**（0.5🍅）
  - Creatomate API Key設定
  - Cloudinary API Key設定
  - n8n Credentials登録
  - 認証テスト呼び出し成功確認

- [ ] **1.2 単一スライド変換テスト**（1🍅）
  - Phase4a出力から1枚取得
  - Creatomate API呼び出し
  - 動画変換成功確認
  - 動画URL取得、品質確認

- [ ] **1.3 エラーハンドリング確認**（0.5🍅）
  - API失敗時のリトライ動作
  - タイムアウト設定確認
  - エラーログ出力確認

**Go/No-Go判断基準**:
- ✅ **Go条件**（プロトタイプ成功 → Phase 2へ）:
  - API認証成功
  - 1枚のスライド → 動画変換成功
  - レスポンス時間 <2分
  - 動画品質OK（1080p、期待通り）

- ❌ **No-Go条件**（代替案検討）:
  - API認証失敗 → Cloudinary候補へ切替（+0.5🍅）
  - 変換失敗率 >10% → Cloudinary候補へ切替（+0.5🍅）
  - レスポンス時間 >3分 → 仕様見直し（並列処理検討）

**デリバリー**: プロトタイプ動作デモ、API動作確認レポート

---

### Phase 2: MVP実装（3🍅）

**目標**: Phase4b/4c実装、E2Eテスト成功

**機能範囲**:
- F1: Phase4a出力データ取得（Phase4a既存出力利用）
- F2: スライド画像 → 動画変換（7本）
- F3: 動画結合（または簡素化オプション）
- F4: Notion DB更新

**タイムボックス**:
- 最大工数: 3🍅
- 中間評価:
  - **50%時点（1.5🍅）**: Phase4b実装完了、7本変換成功
    - ✅ Go: 変換成功率 ≥95%、処理時間OK
    - ❌ No-Go: 仕様簡素化（並列→逐次、または結合なし）
  - **80%時点（2.4🍅）**: Phase4c実装完了、E2Eテスト成功
    - ✅ Go: E2Eテスト成功、残り0.6🍅でリリース可能
    - ❌ No-Go: Phase4c簡素化（結合なし、7本URL保存）

**実装優先順位**:
1. **最優先**: F2（スライド → 動画変換）
2. **次優先**: F4（Notion DB更新）
3. **最低優先**: F3（動画結合）← 時間不足なら簡素化

**デリバリー**: Phase4完成、E2Eテスト成功、本番デプロイ

---

### Phase 3: 品質向上（オプション、Phase5後に実施）

**目標**: Phase4の安定性・品質向上

**タスク**:
- [ ] エラーハンドリング強化（0.5🍅）
- [ ] 動画結合実装（Phase2で簡素化した場合）（1🍅）
- [ ] モニタリング・ロギング追加（0.5🍅）

**実施タイミング**: Phase5完成後、Phase4に余裕ができた時点

---

## 成功基準

### 定量的基準

- ✅ **Phase4完成**: Phase4a → Phase4b → Phase4c → Notion更新の完全自動化
- ✅ **処理時間**: Phase4全体 <5分（並列処理時）
- ✅ **エラー率**: <5%（API信頼性依存）
- ✅ **工数**: プロトタイプ2🍅 + MVP3🍅 = 合計5🍅以内（現行19🍅+から74%削減）
- ✅ **ドキュメント**: 5件以内（現行29件から83%削減）
- ✅ **ワークフロー検証**: エラー0件、警告5件以内

### 定性的基準

- ✅ **5原則遵守**: 事例ベース選定、既存資産活用、適切な内製化、プロトタイプ駆動、タイムボックス厳守
- ✅ **保守性**: シンプルな実装、明確なエラーハンドリング、将来の改善容易性
- ✅ **Phase5連携**: Phase4完成により Phase5実装開始可能
- ✅ **チーム士気**: 完成による達成感、モチベーション回復

---

## 参考資料

### 技術資料

- [Creatomate API Documentation](https://creatomate.com/docs/api/introduction)
- [Cloudinary Video API Reference](https://cloudinary.com/documentation/video_manipulation_and_delivery)
- [n8n Creatomate Integration](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.creatomate/)
- [n8n HTTP Request Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)

### プロジェクト資料

- [WF7-Phase4a-ResponWithWebhook-Fix.md](../implementation/WF7-Phase4a-ResponWithWebhook-Fix.md)
- [WF7-Phase4b-改善レポート.md](../implementation/WF7-Phase4b-改善レポート.md)
- [WF7-Phase4-FAL実装計画書.md](../implementation/WF7-Phase4-FAL実装計画書.md)
- [MEO標準化ナレッジ](file:///Users/yuichiroooosuger/Desktop/2rd_brain/Projects/01_Active/MEO/標準化ナレッジ/)

### 標準化ナレッジ参照

- [_テンプレート_要件定義.md](file:///Users/yuichiroooosuger/Desktop/2rd_brain/Projects/01_Active/MEO/標準化ナレッジ/_テンプレート_要件定義.md)
- [Week02_失敗ログ.md](file:///Users/yuichiroooosuger/Desktop/2rd_brain/Projects/01_Active/MEO/標準化ナレッジ/失敗と改善ログ/Week02_失敗ログ.md) - Phase4ビルド問題の教訓

---

## 📊 新旧実装比較

| 項目 | 旧実装（FAL.ai + Railway FFmpeg） | 新実装（Creatomate/Cloudinary） |
|------|----------------------------------|--------------------------------|
| 事例の豊富さ | ❌ 少（原則1違反） | ✅ 豊富（n8n公式/コミュニティ） |
| 実装工数 | 19🍅+（未完成） | 5🍅目標（74%削減） |
| ドキュメント数 | 29件 | 5件以内（83%削減） |
| ワークフロー検証 | エラー6件、警告16件 | エラー0件目標 |
| 完成見込み | 不明（既に3.2倍超過） | 高（事例豊富、5🍅タイムボックス） |
| 保守性 | 低（複雑化、独自実装） | 高（シンプル、外部API） |
| 原則1遵守 | ❌ 違反 | ✅ 遵守 |
| 原則5遵守 | ❌ 違反（タイムボックス超過） | ✅ 遵守（厳格なGo/No-Go） |

---

**次のステップ**: プロトタイプ実装（Phase 1）
**推定工数**: Phase 1（2🍅）+ Phase 2（3🍅）= 合計5🍅
**Go/No-Go判断**: 1.5🍅時点（プロトタイプ完成）

**作成者**: Claude Code
**承認**: 未承認
**次回レビュー**: Phase 1完了後（プロトタイプ動作確認）

---

## 📝 重要な決定事項

1. **Phase4b/4cの技術スタック変更**: FAL.ai → Creatomate/Cloudinary
2. **原則1違反の認識**: 事例不足技術の採用が19🍅+消費の原因
3. **原則5の厳格化**: 1.5🍅、2.5🍅、4🍅時点でGo/No-Go判断を明確化
4. **Phase4c簡素化オプション**: 時間不足時は動画結合をスキップ可能
5. **Phase5優先**: Phase4完成を最優先、Phase4品質向上はPhase5後に実施
