# WF7 Phase2 テストデータ収集レポート

**作成日**: 2025-11-05
**目的**: WF7 Phase2 (OAuth版) 検証用のテストページIDとメタ情報を収集
**ステータス**: ドキュメントベースでの情報収集完了

---

## 📋 実行サマリー

### Notion API 認証状況
❌ **Notion MCP API認証エラー**
- エラー: `API token is invalid` (401 Unauthorized)
- 影響: 直接的なNotion API検索が不可
- 対応: 既存ドキュメントから情報収集

### 収集方法
✅ **既存ドキュメントからの情報抽出**
- E2Eテストレポート
- Phase4トラブルシューティングガイド
- Phase2テスト計画書
- その他関連ドキュメント

---

## 🔍 収集したテストページ情報

### テストページ1: E2Eテスト用 (Phase1で作成)

| 項目 | 値 |
|------|-----|
| **Notion Page ID** | `29e68d5c-2986-81c7-a260-cf9084f8d864` |
| **Article ID** | `test-meo-001` |
| **タイトル** | (Phase1で生成されたタイトル) |
| **Database ID** | `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` |
| **ステータス** | `AssetsReady` (Phase2実行後) |
| **作成日** | 2025-11-01 |
| **用途** | Phase1→Phase2統合テスト |
| **Phase2実行結果** | ✅ 成功 (実行ID: 1241) |

**Phase2実行時の入力データ**:
```json
{
  "articleId": "test-meo-001",
  "notionPageId": "29e68d5c-2986-81c7-a260-cf9084f8d864",
  "assetTags": "店舗,AI,検索,AI検索,位置情報,顧客,MEO,Googleマップ,最適化,CTA,リンク,店舗選択"
}
```

**取得結果**:
- 成功: 1画像 (Pexels) - タグ「店舗」
- 失敗: 11タグ (日本語タグの検索性能問題)

---

### テストページ2: Phase4統合テスト用

| 項目 | 値 |
|------|-----|
| **Notion Page ID** | `2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9` |
| **Article ID** | `integration-test-001` |
| **タイトル** | "Phase1→Phase4統合テスト記事" |
| **Database ID** | `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` |
| **ステータス** | 不明 |
| **用途** | Phase1→Phase4統合テスト |

---

### テストページ3: Google Drive統合テスト用 (推奨)

| 項目 | 値 |
|------|-----|
| **Notion Page ID** | `<新規作成が必要>` |
| **Article ID** | `gdrive-test-001` (推奨) |
| **タイトル** | "WF7 Phase2 Google Drive統合テスト" |
| **Database ID** | `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` |
| **ステータス** | `Draft` |
| **用途** | Phase2 OAuth版 (Google Drive) 検証 |

**推奨テストデータ**:
```json
{
  "articleId": "gdrive-test-001",
  "notionPageId": "<新規作成したページID>",
  "assetTags": "opening,problem,solution,cta"
}
```

---

## 📊 Phase2 Webhook入力形式

### 通常版 (Pexels/Unsplash)
**Webhook URL**: `POST /webhook/wf7-phase2-assets`

**入力形式**:
```json
{
  "articleId": "<記事ID>",
  "notionPageId": "<NotionページID>",
  "assetTags": "<カンマ区切りタグ>"
}
```

### OAuth版 (Google Drive)
**Webhook URL**: `POST /webhook/wf7-phase2-assets-google`

**入力形式**:
```json
{
  "articleId": "<記事ID>",
  "notionPageId": "<NotionページID>",
  "assetTags": "<カンマ区切りタグ>"
}
```

**注意**: OAuth版と通常版は入力形式が同じです。

---

## 🎯 Phase2 OAuth版検証用データ

### 推奨テストケース1: 既存ページを使用

```json
{
  "articleId": "test-meo-001",
  "notionPageId": "29e68d5c-2986-81c7-a260-cf9084f8d864",
  "assetTags": "opening,problem,solution,cta"
}
```

**実行コマンド**:
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-meo-001",
    "notionPageId": "29e68d5c-2986-81c7-a260-cf9084f8d864",
    "assetTags": "opening,problem,solution,cta"
  }'
```

**メリット**:
- ✅ 既存ページを使用できる
- ✅ 過去のテスト結果と比較可能

**デメリット**:
- ⚠️ 既存データが上書きされる可能性

---

### 推奨テストケース2: 新規ページを作成

**ステップ1: Notionで新規ページ作成**
1. Notionデータベース `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` を開く
2. 新規ページを作成
3. 以下のプロパティを設定:
   - **Title**: "WF7 Phase2 OAuthテスト"
   - **Article ID**: `phase2-oauth-test-001`
   - **Status**: `Draft`
4. ページIDをコピー (URLの最後の部分)

**ステップ2: Webhook実行**
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "phase2-oauth-test-001",
    "notionPageId": "<ステップ1で取得したページID>",
    "assetTags": "opening,problem,solution,cta"
  }'
```

**メリット**:
- ✅ クリーンなテスト環境
- ✅ 既存データに影響なし

---

## 📝 メタ情報まとめ

### Notion Database情報

| Database名 | Database ID | 用途 |
|-----------|-------------|------|
| 動画管理DB | `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` | WF7 Phase1-5共通 |
| note記事管理DB | `29968d5c298681ad90d0c24ed710503e` | WF6記事生成用 |

### プロパティ構造 (動画管理DB)

| プロパティ名 | 型 | 説明 |
|------------|---|------|
| Title | Title | ページタイトル |
| Article ID | Rich Text | 記事識別子 |
| Status | Select | ステータス (Draft, Processing, ScriptGenerated, AssetsReady, Rendered, Failed) |
| Script | Rich Text | 台本JSON (Phase1で生成) |
| Assets | Rich Text | アセットJSON (Phase2で生成) |
| Needs Narration | Checkbox | 音声生成フラグ |
| Created At | Date | 作成日時 |
| Error Message | Rich Text | エラーメッセージ (失敗時) |

### アセットタグ推奨値

**標準4セグメント動画用**:
```
opening,problem,solution,cta
```

**日本語タグ例** (Pexels/Unsplash検索用):
```
ビジネス,オフィス,会議,チーム,成功,成長,テクノロジー,未来,イノベーション
```

**英語タグ例** (推奨 - 検索性能が高い):
```
business,office,meeting,team,success,growth,technology,future,innovation
```

---

## ⚠️ 注意事項

### 1. Notion API認証の問題
- Notion MCP APIが認証エラーで使用不可
- 手動でNotionページを作成・確認する必要がある
- ページIDはNotion URLから手動で取得

### 2. テストページIDの取得方法
```
https://www.notion.so/[TITLE]-[PAGE_ID]
                                    ^^^^^^^^^ これをコピー
```

例:
```
https://www.notion.so/WF7-Phase2-OAuth-test-2a068d5c298681a3ab0cff0bc1e4ebb9
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^
                                                      ↑ これをコピー
```

### 3. Phase2 OAuth版の前提条件
- ✅ Google Drive OAuth2認証情報が設定済み
- ✅ n8nで認証情報が有効
- ✅ Google Drive APIが有効化されている
- ✅ テスト用Google Driveフォルダが作成済み (オプション)

### 4. エラーハンドリング
Phase2実行時に以下のエラーが発生する可能性:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON is not set` → 環境変数未設定
- `Failed to obtain Google access token` → JSON形式エラー
- `invalid_grant` → サービスアカウントが無効
- `unauthorized_client` → APIが無効化されている
- `insufficient_permissions` → ロールが不足

詳細は `wf7-google-auth-fix-guide.md` を参照。

---

## 🚀 次のステップ

### 即座に実行可能
1. ✅ **既存テストページを使用したPhase2 OAuth版実行**
   - Page ID: `29e68d5c-2986-81c7-a260-cf9084f8d864`
   - Article ID: `test-meo-001`
   - Asset Tags: `opening,problem,solution,cta`

2. ✅ **新規テストページ作成**
   - Notionで手動作成
   - ページIDを取得
   - Phase2 OAuth版を実行

### 推奨アクション
1. **Notion MCP API認証の修正**
   - APIトークンの確認と再設定
   - 認証情報の検証

2. **テスト結果の検証**
   - Railway logsで実行状況を確認
   - NotionページのStatus更新を確認
   - Assets JSONフィールドの内容を確認

3. **ドキュメント更新**
   - 新しいテストページIDを記録
   - テスト結果をレポートに追記

---

## 📚 関連ドキュメント

- `wf7-google-auth-fix-guide.md` - Google認証エラー修正ガイド
- `wf7-oauth-json-body-fix.md` - OAuth JSON Body修正
- `phase2-google-drive-test-plan.md` - Phase2 Google Drive統合テスト計画
- `WF7-E2E-TEST-REPORT.md` - E2Eテスト実行レポート
- `wf7-phase4-troubleshooting-guide.md` - Phase4トラブルシューティング

---

**最終更新**: 2025-11-05
**ステータス**: 情報収集完了・検証用データ準備済み

