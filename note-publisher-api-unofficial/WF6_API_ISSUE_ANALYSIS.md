# WF6 note.com API問題 - 分析と解決策提案

**作成日**: 2025-10-29
**状態**: 解決策検討中
**優先度**: P0 (クリティカル)

## 問題概要

### 現象
- **WF6**: note記事自動生成ワークフローが最終ノード「note: Publish Article」で失敗
- **エラー**: HTTP 404 - `{"success":false,"error":"note API request failed","details":"Status: 404, Response: {\"status\":404,\"error\":\"Not Found\"}"}`
- **影響範囲**: note.com自動投稿機能が完全停止

### 根本原因
Vercel API (`publish-note.ts`) が使用している `POST https://note.com/api/v2/notes` エンドポイントが404を返す。

note.comは公式APIを提供しておらず、非公式APIエンドポイントは予告なく変更される可能性がある。

## 実施した調査

### 1. エンドポイント検証テスト

#### テスト1: `/api/v2/notes` (現在の実装)
```bash
curl -X POST https://note.com/api/v2/notes \
  -H "Content-Type: application/json" \
  -H "Cookie: _note_session_v5=..." \
  -d '{"name":"テスト記事","body":"本文","status":"published"}'

→ {"status":404,"error":"Not Found"}
```
**結果**: ❌ エンドポイント自体が存在しないか廃止済み

#### テスト2: `/api/v1/text_notes` (Web調査で発見)
```bash
curl -X POST https://note.com/api/v1/text_notes \
  -H "Content-Type: application/json" \
  -H "Cookie: _note_session_v5=..." \
  -d '{"name":"テスト記事","body":"本文","status":"published"}'

→ {"error":{"code":"auth","message":"not_login"}}
```
**結果**: ✅ エンドポイントは存在、❌ 認証方式が異なる（CSRFトークン等が必要な可能性）

#### テスト3: `/api/v3/drafts` (Web調査で発見)
```bash
curl -X POST https://note.com/api/v3/drafts \
  -H "Content-Type: application/json" \
  -H "Cookie: _note_session_v5=..." \
  -d '{"name":"テスト記事","body":"本文"}'

→ {"status":404,"error":"Not Found"}
```
**結果**: ❌ エンドポイント存在せず

### 2. Health Check確認
```bash
curl https://note-publisher-api-unofficial-1jzu3j144-plus62s-projects.vercel.app/api/health

→ {"status":"healthy","timestamp":"2025-10-29T06:32:43.622Z","checks":{"apiKeyConfigured":true,"noteSessionConfigured":true,"noteSessionValid":true},"message":"All systems operational"}
```
**結果**: Vercel APIサーバー自体は正常稼働

## 検討した解決策とリスク評価

### オプションA: DevTools調査で実際のAPIを特定
**アプローチ**: ブラウザでnote.comに手動投稿し、Network tabで実際のAPIコールを確認

**リスク評価**:
- 変動性リスク: **高** - note.comは公式APIなし、予告なく変更される
- 実装難易度: 中
- 運用負荷: 高 - API変更のたびに追従が必要

**判定**: ❌ 非推奨 - 持続可能性に欠ける

### オプションB: セッションクッキー再取得
**アプローチ**: 書き込み権限付きでセッションクッキーを再取得

**リスク評価**:
- 変動性リスク: **高** - 非公式API依存
- 実装難易度: 低
- 運用負荷: 高 - 定期的なクッキー更新が必要

**判定**: ❌ 非推奨 - 根本解決にならない

### オプションC-1: Playwright自動化 ⭐ 推奨
**アプローチ**: UIベースのブラウザ自動操作で記事投稿

**メリット**:
- UIはAPIより変更頻度が低い（安定性高）
- 人間の操作と同じため検出されにくい
- note.comの仕様変更に強い

**デメリット**:
- 実行時間が長い（30秒〜1分程度）
- Vercelで実行不可 → Railway等の別環境が必要
- UI変更時にセレクタ修正が必要（ただし頻度は低い）

**アーキテクチャ**:
```
n8n WF6
  ↓ HTTP POST
Railway Playwright APIサーバー
  ↓ ブラウザ自動操作
note.com (記事公開)
  ↓ レスポンス
Notion DB登録 + Slack通知
```

**リスク評価**:
- 変動性リスク: **低〜中** - UIはAPIより安定
- 実装難易度: 中〜高
- 運用負荷: 中

**判定**: ⭐ **推奨** - 中長期的に最も持続可能

### オプションC-2: RSS/Atom対応
**アプローチ**: note.comの公式RSS/Atom APIを利用

**判定**: ❌ 実現不可 - note.comは投稿用RSS/Atom APIを提供していない（閲覧用のみ）

### オプションC-3: 半自動化（手動投稿 + 自動準備） ○ 短期推奨
**アプローチ**: GPT-4での記事生成まで自動化、note.com投稿のみ手動

**フロー**:
```
WF6: GPT-4生成 → Notion DB保存 → Slack通知（投稿用データ送信）
  ↓
手動: Slackの内容をコピー → note.comに投稿 → 完了報告
  ↓
WF6: Notion DB更新（公開URL記録）
```

**メリット**:
- 変更リスク: **極めて低**
- 実装難易度: 極めて低
- 即座に運用開始可能

**デメリット**:
- 完全自動化ではない
- 毎日の手動作業が発生（1日1回、5分程度）

**判定**: ○ **短期推奨** - 即座に運用開始、並行してC-1を開発

## リスク評価まとめ

| アプローチ | 変動性リスク | 実装難易度 | 運用負荷 | 持続可能性 | 推奨度 |
|-----------|------------|-----------|---------|-----------|--------|
| A: DevTools調査 | 高 | 中 | 高 | 低 | ❌ |
| B: Cookie再取得 | 高 | 低 | 高 | 低 | ❌ |
| **C-1: Playwright** | **低〜中** | 中〜高 | 中 | **高** | ⭐ |
| C-2: RSS/Atom | N/A | - | - | - | ❌ |
| C-3: 半自動化 | 極めて低 | 極めて低 | 低 | 中 | ○ |

## 推奨実装計画

### フェーズ1（即時実施）: C-3（半自動化）
**目的**: WF6を即座に運用可能状態にする

**実装内容**:
1. WF6の最終ノードを「Slack通知」に変更
2. Slack通知内容: タイトル、本文、カテゴリを整形して送信
3. 手動投稿ガイドをREADMEに追加

**工数**: 1🍅（30分）

### フェーズ2（並行開発）: C-1（Playwright完全自動化）
**目的**: 中長期的に持続可能な完全自動化を実現

**実装内容**:
1. Railway上にPlaywright APIサーバー構築
2. note.com記事投稿フローの自動化実装
3. n8n → Railway Playwright API連携
4. エラーハンドリングとリトライロジック

**工数**: 10🍅（5時間）

## 次のアクション

1. **即時**: C-3（半自動化）の実装承認
2. **1週間以内**: C-1（Playwright）の詳細設計
3. **2週間以内**: C-1の実装とテスト

## 関連ファイル

- `/Users/yuichiroooosuger/Desktop/n8n-workflows/note-publisher-api-unofficial/pages/api/publish-note.ts` - 現行Vercel API
- n8n WF6 ID: `tkmG4YSZyi5RLiPw`
- Vercel API URL: `https://note-publisher-api-unofficial-1jzu3j144-plus62s-projects.vercel.app`

## 参考情報

### Web調査結果
- note.comは公式APIを提供していない
- 非公式APIは予告なく変更される
- 現在（2025年）使用されているエンドポイント:
  - `/api/v1/text_notes` - 認証方式が複雑（CSRF等）
  - `/api/v2/notes/{note_key}/publish` - 下書きからの公開用

---

**最終更新**: 2025-10-29
**次回レビュー**: フェーズ1実装完了後
