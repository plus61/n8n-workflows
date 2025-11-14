# Phase3: CVR最適化 - n8nワークフロー詳細設計書

**フェーズ**: Phase3 - CVR最適化（Week 7-10）
**目標**: 成約率30%達成
**総工数**: 80U = 240🍅
**状態**: ⏳ 待機中（Phase2完了後に着手）
**作成日**: 2025-10-27
**バージョン**: 1.0

---

## 📋 目次

1. [Phase3概要](#phase3概要)
2. [WF10: LINEステップ配信拡張](#wf10-lineステップ配信拡張)
3. [WF11: デモ予約自動化](#wf11-デモ予約自動化)
4. [WF12: 営業資料自動化](#wf12-営業資料自動化)
5. [CVR改善戦略](#cvr改善戦略)
6. [技術要件](#技術要件)

---

## Phase3概要

### ビジネス目標

**定量目標**:
- LP CVR 30%達成（Phase2完了時点で25%想定）
- デモ予約自動化稼働（手動→自動化）
- 成約率向上確認（デモ→成約 28%→32%）

**定性目標**:
- LINEステップ配信のA/Bテスト基盤構築
- パーソナライズ配信の実現
- 営業プロセスの自動化・効率化

### 全体アーキテクチャ

```
[WF2: LINE Step Delivery System] (Phase1)
   ↓
[WF10: LINEステップ配信拡張]
   ├→ A/Bテスト
   ├→ パーソナライズ
   └→ リエンゲージメント
   ↓
[リード育成強化]
   ↓
[WF11: デモ予約自動化]
   ├→ カレンダー統合
   ├→ 自動調整
   └→ リマインダー
   ↓
[デモ実施]
   ↓
[WF12: 営業資料自動化]
   ├→ リード情報取得
   ├→ PDF生成
   └→ 自動送信
   ↓
[成約率向上]
```

### ワークフロー一覧

| WF | 名称 | 工数 | 優先度 | 依存 | 主要技術 |
|----|------|------|--------|------|----------|
| **WF10** | LINEステップ配信拡張 | 30🍅 | P0 | WF2 | LINE API, GPT-4 |
| **WF11** | デモ予約自動化 | 30🍅 | P0 | WF3 | Google Calendar API |
| **WF12** | 営業資料自動化 | 24🍅 | P1 | WF3, WF11 | Puppeteer, PDF.co |

---

## WF10: LINEステップ配信拡張

### 基本情報

- **工数**: 30🍅（10ユニット）
- **目的**: Phase1のWF2を拡張し、A/Bテスト・パーソナライズ・リエンゲージメント機能を追加
- **トリガー**: Schedule（毎時0分）+ Webhook（ユーザーアクション検知）
- **実行頻度**: 毎時1回 + イベント駆動

### 設計意図

**Phase1のWF2からの進化**:
- Phase1: 全員に同じステップ配信
- Phase3: セグメント別・行動別にパーソナライズ配信

**なぜこのワークフローが必要か**:
- 開封率・クリック率を最大化してCVR向上
- ユーザー属性・行動に応じた最適なメッセージ配信
- 離脱ユーザーの再エンゲージメント

### ワークフロー構成

#### サブフロー1: A/Bテスト配信

```
[1] Schedule Trigger（毎時0分）
     ↓
[2] Google Sheets: ステップ配信キュー取得
     ↓ 配信対象ユーザー
[3] Function: A/Bグループ分け
     ↓ userIdのハッシュ値でA/B振り分け
[4] Notion: A/Bテストマスタ取得
     ↓ パターンA、パターンBのメッセージ
[5] IF: グループ判定
     ├→ A: メッセージA配信
     └→ B: メッセージB配信
[6] Google Sheets: A/Bテストログ保存
     ↓ userId, group, messageId, deliveredAt
[7] Webhook: クリック検知（LINE Webhookから）
     ↓ ユーザーがURLクリック
[8] Google Sheets: クリックログ保存
     ↓ userId, messageId, clickedAt
[9] Function: CTR計算・比較
     ↓ グループAとグループBのCTR比較
[10] Slack: A/Bテスト結果通知
     ↓ 「パターンAのCTR: 12.5%, パターンB: 15.3%」
```

#### サブフロー2: パーソナライズ配信

```
[1] Webhook Trigger（ユーザーアクション検知）
     ↓ note記事閲覧、LINE URL クリック
[2] Google Sheets: ユーザー行動履歴保存
     ↓ userId, action, articleId, timestamp
[3] Function: ユーザーセグメント判定
     ↓ 高関心/中関心/低関心
[4] GPT-4: パーソナライズメッセージ生成
     ↓ セグメント別最適化
[5] HTTP Request: LINE Messaging API
     ↓ パーソナライズメッセージ配信
[6] Notion: パーソナライズログ保存
```

#### サブフロー3: リエンゲージメント

```
[1] Schedule Trigger（週1回：月曜 09:00）
     ↓
[2] Google Sheets: 離脱ユーザー抽出
     ↓ 14日間未開封ユーザー
[3] GPT-4: リエンゲージメントメッセージ生成
     ↓ 「お久しぶりです。最新情報をお届けします」
[4] HTTP Request: LINE Messaging API
     ↓ リエンゲージメント配信
[5] Google Sheets: 反応確認
     ↓ 開封率モニタリング
```

### A/Bテストマスタ設計

**Notion: A/Bテストマスタ**

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| Test Name | Title | テスト名 |
| Step No | Number | ステップ番号 |
| Pattern A Title | Rich Text | パターンAタイトル |
| Pattern A Body | Rich Text | パターンA本文 |
| Pattern B Title | Rich Text | パターンBタイトル |
| Pattern B Body | Rich Text | パターンB本文 |
| Start Date | Date | テスト開始日 |
| End Date | Date | テスト終了日 |
| Winner | Select | A/B/未決定 |

---

## WF11: デモ予約自動化

### 基本情報

- **工数**: 30🍅（10ユニット）
- **目的**: LINE経由でのデモ予約をGoogle Calendarと統合し、自動調整・リマインダー送信
- **トリガー**: Webhook（LINE「デモ予約希望」ボタンクリック）
- **実行頻度**: イベント駆動

### 設計意図

**なぜこのワークフローが必要か**:
- 手動のカレンダー調整を自動化（工数削減）
- 予約確定までのリードタイム短縮
- リマインダー自動送信でNo-show削減

### ワークフロー構成

```
[1] Webhook Trigger（LINE「デモ予約」ボタンクリック）
     ↓ userId
[2] Google Sheets: ユーザー情報取得
     ↓ displayName, email（事前アンケートで取得）
[3] HTTP Request: Google Calendar API - 空き時間取得
     ↓ 今週・来週の空き枠
[4] Function: 候補日時生成（3候補）
     ↓ 空き時間から最適な3つを選択
[5] HTTP Request: LINE Messaging API - 日時選択
     ↓ 「以下の日時から選択してください」
[6] Webhook: 日時選択受信
     ↓ ユーザーが選択した日時
[7] HTTP Request: Google Calendar API - イベント作成
     ↓ デモ予約イベント登録
[8] Notion: デモ予約DB登録
     ↓ userId, scheduledAt, status=confirmed
[9] HTTP Request: LINE Messaging API - 確定通知
     ↓ 「予約確定しました。{日時}にお待ちしております」
[10] Schedule Trigger: リマインダー送信
     ├→ デモ前日 17:00: 「明日のデモ予約について」
     └→ デモ当日 09:00: 「本日{時刻}からデモです」
```

### Google Calendar API統合

```yaml
# 空き時間取得
Node Type: HTTP Request
Method: GET
URL: https://www.googleapis.com/calendar/v3/calendars/primary/events
Authentication: OAuth2 (Google)
Query Parameters:
  - timeMin: {{今日の日時}}
  - timeMax: {{2週間後の日時}}
  - singleEvents: true
  - orderBy: startTime

# イベント作成
Node Type: HTTP Request
Method: POST
URL: https://www.googleapis.com/calendar/v3/calendars/primary/events
Body:
  {
    "summary": "デモ予約 - {{displayName}}",
    "description": "LINE経由のデモ予約",
    "start": {
      "dateTime": "{{selectedDateTime}}",
      "timeZone": "Asia/Tokyo"
    },
    "end": {
      "dateTime": "{{endDateTime}}",
      "timeZone": "Asia/Tokyo"
    },
    "attendees": [
      {"email": "{{userEmail}}"}
    ],
    "reminders": {
      "useDefault": false,
      "overrides": [
        {"method": "email", "minutes": 1440},
        {"method": "popup", "minutes": 30}
      ]
    }
  }
```

---

## WF12: 営業資料自動化

### 基本情報

- **工数**: 24🍅（8ユニット）
- **目的**: リード情報から営業資料PDFを自動生成し、デモ前にLINEで送信
- **トリガー**: Webhook（WF11からデモ予約確定通知）
- **実行頻度**: イベント駆動（デモ予約確定時）

### 設計意図

**なぜこのワークフローが必要か**:
- 営業資料作成の工数削減（1件30分→自動化）
- パーソナライズされた提案資料で成約率向上
- デモ前に資料を送ることで理解促進

### ワークフロー構成

```
[1] Webhook Trigger（WF11からのデモ予約確定通知）
     ↓ userId, scheduledAt
[2] Google Sheets: リード情報取得
     ↓ displayName, email, 興味分野, 子供年齢
[3] Notion: 教室情報取得
     ↓ 料金、カリキュラム、実績データ
[4] GPT-4: 営業資料コンテンツ生成
     ↓ リード情報に基づくパーソナライズ提案
[5] Function: HTML生成
     ↓ 営業資料テンプレート + GPT-4コンテンツ
[6] HTTP Request: Puppeteer/PDF.co - PDF変換
     ↓ HTML → PDF
[7] Google Drive: PDF保存
     ↓ ファイルURL取得
[8] Notion: 営業資料DB登録
     ↓ userId, pdfUrl, generatedAt
[9] HTTP Request: LINE Messaging API - PDF送信
     ↓ 「デモ前にご確認ください」+ PDF添付
[10] Slack: 資料送信完了通知
```

### PDF生成方法

#### オプション1: Puppeteer（セルフホスト）

```javascript
// Function ノード
const puppeteer = require('puppeteer');

const html = $json.htmlContent;

const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.setContent(html);
const pdfBuffer = await page.pdf({
  format: 'A4',
  printBackground: true
});
await browser.close();

// Base64エンコード
const pdfBase64 = pdfBuffer.toString('base64');

return {
  json: {
    pdfBase64: pdfBase64
  }
};
```

#### オプション2: PDF.co（API）

```yaml
Node Type: HTTP Request
Method: POST
URL: https://api.pdf.co/v1/pdf/convert/from/html
Authentication: API Key
Headers:
  - x-api-key: {{PDF_CO_API_KEY}}
Body:
  {
    "html": "{{$json.htmlContent}}",
    "name": "営業資料_{{$json.displayName}}.pdf",
    "margins": "10mm",
    "paperSize": "A4",
    "orientation": "Portrait"
  }
```

### 営業資料テンプレート

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Noto Sans JP', sans-serif; }
    .header { background: #4A90E2; color: white; padding: 20px; }
    .section { margin: 20px; }
    .highlight { background: #FFF9C4; padding: 10px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>{{displayName}}様 専用提案資料</h1>
    <p>Smart Review - 英語学童MEOサービス</p>
  </div>

  <div class="section">
    <h2>{{displayName}}様の課題</h2>
    <p>{{GPT-4が生成した課題分析}}</p>
  </div>

  <div class="section">
    <h2>Smart Reviewの解決策</h2>
    <div class="highlight">
      {{GPT-4が生成したパーソナライズ提案}}
    </div>
  </div>

  <div class="section">
    <h2>料金プラン</h2>
    <table>
      {{料金表}}
    </table>
  </div>

  <div class="section">
    <h2>導入実績</h2>
    {{実績データ}}
  </div>
</body>
</html>
```

---

## CVR改善戦略

### CVRファネル分析

```
[LP訪問] 1,000人
   ↓ CVR 5% (Phase1)
[LINE友だち追加] 50人
   ↓ CVR 40% (Phase3目標: LINEステップ配信最適化)
[デモ予約] 20人
   ↓ CVR 70% (Phase3目標: デモ自動化 + 営業資料)
[成約] 14人

最終CVR = 50/1000 × 20/50 × 14/20 = 1.4%
Phase3目標: 最終CVR 2.1%（+50%向上）
```

### CVR向上施策マトリクス

| フェーズ | 現状CVR | 施策 | 目標CVR | 寄与度 |
|---------|---------|------|---------|--------|
| **LP→LINE** | 5% | Phase2でPV増加 | 5% | - |
| **LINE→デモ** | 40% | WF10: ステップ配信最適化 | 50% | +25% |
| **デモ→成約** | 70% | WF11+WF12: 自動化・資料 | 80% | +14% |
| **最終CVR** | 1.4% | - | 2.0% | +43% |

---

## 技術要件

### API統合

| API | 用途 | 認証方式 | レート制限 |
|-----|------|----------|-----------|
| **LINE Messaging API** | メッセージ配信 | Bearer Token | 500通/月（無料） |
| **GPT-4 API** | パーソナライズ生成 | API Key | 10,000 req/日 |
| **Google Calendar API** | デモ予約管理 | OAuth2 | 1,000,000 req/日 |
| **PDF.co API** | PDF生成 | API Key | 300 req/月（$29プラン） |
| **Google Drive API** | PDF保存 | OAuth2 | 1,000 req/日 |

### データベース追加設計

#### Notion: A/Bテストログ

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| User ID | Text | LINE userId |
| Test Name | Relation | A/Bテストマスタへ |
| Group | Select | A/B |
| Message ID | Text | 配信メッセージID |
| Delivered At | Date | 配信日時 |
| Clicked | Checkbox | クリック有無 |
| Clicked At | Date | クリック日時 |

#### Notion: デモ予約DB

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| User Name | Title | ユーザー名 |
| User ID | Text | LINE userId |
| Email | Email | メールアドレス |
| Scheduled At | Date | デモ予定日時 |
| Calendar Event ID | Text | Google CalendarイベントID |
| Status | Select | confirmed/completed/cancelled |
| Reminder Sent | Checkbox | リマインダー送信済み |

#### Notion: 営業資料DB

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| User Name | Title | ユーザー名 |
| Related Demo | Relation | デモ予約DBへ |
| PDF URL | URL | Google Drive URL |
| Generated At | Date | 生成日時 |
| Sent At | Date | LINE送信日時 |
| Opened | Checkbox | PDF開封確認 |

---

## Phase3完了判定基準

- [ ] WF10, WF11, WF12すべて稼働
- [ ] A/Bテスト実施（最低3パターン）
- [ ] パーソナライズ配信開封率 >45%
- [ ] デモ予約自動化成功率 >90%
- [ ] 営業資料自動生成成功率 >95%
- [ ] 最終CVR 2.0%達成

---

## 関連ドキュメント

- [[MEO集客自動化_n8nワークフロー全体構成]]
- [[Phase1_n8nワークフロー詳細設計書]]
- [[Phase2_n8nワークフロー詳細設計書]]
- [[Phase4_n8nワークフロー詳細設計書]]

---

## 更新履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|----------|--------|
| 1.0 | 2025-10-27 | 初版作成 - Phase3全ワークフロー設計 | Claude + User |

---

**次のステップ**: Phase2完了後にWF10から順次実装
