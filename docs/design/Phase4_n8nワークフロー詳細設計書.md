# Phase4: AI PDCA - n8nワークフロー詳細設計書

**フェーズ**: Phase4 - AI PDCA（Week 11-12）
**目標**: 改善ループがAI自走
**総工数**: 40U = 120🍅
**状態**: ⏳ 待機中（Phase3完了後に着手）
**作成日**: 2025-10-27
**バージョン**: 1.0

---

## 📋 目次

1. [Phase4概要](#phase4概要)
2. [WF13: KPI統合ダッシュボード](#wf13-kpi統合ダッシュボード)
3. [WF14: AIレポート自動生成](#wf14-aiレポート自動生成)
4. [WF15: 人気記事再配信](#wf15-人気記事再配信)
5. [WF16: トピック再学習](#wf16-トピック再学習)
6. [AI自走の証明](#ai自走の証明)

---

## Phase4概要

### ビジネス目標

**定量目標**:
- 分析工数: 週5時間 → 0時間（年260時間削減）
- PDCA速度: 週1回 → 日次（7倍高速化）
- 改善提案精度: 経験則 → データ駆動

**定性目標**:
- **AI自走改善ループ稼働**: 人間の介入なしでデータ収集→分析→提案→実行のサイクルが回る
- 人間は戦略思考に集中可能
- データに基づく意思決定文化の確立

### 全体アーキテクチャ

```
[Phase1-3の全データ]
   ↓
[WF13: KPI統合ダッシュボード]
   ↓ KPIデータAPI
[WF14: AIレポート自動生成]
   ↓ 改善提案（優先度付き）
   ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
[WF15:        [WF16:        [手動施策]
 人気記事      トピック      （承認後実行）
 再配信]       再学習]
   ↓              ↓              ↓
[自動実行]    [自動実行]    [人間判断]
```

### AI自走の定義

**Phase4完了 = AI自走が証明される**:

1. **7日間連続、人間が何もしなくてもレポートが生成され続ける**
2. **その間に自動実行された施策が3つ以上ある**
3. **KPIが改善傾向にある（CVR +0.5%以上）**

### ワークフロー一覧

| WF | 名称 | 工数 | 優先度 | 依存 | 主要技術 |
|----|------|------|--------|------|----------|
| **WF13** | KPI統合ダッシュボード | 18🍅 | P0 | 全Phase | Google Sheets, Notion API |
| **WF14** | AIレポート自動生成 | 18🍅 | P0 | WF13 | GPT-4 Turbo |
| **WF15** | 人気記事再配信 | 12🍅 | P1 | WF14, WF6 | LINE API, Notion |
| **WF16** | トピック再学習 | 12🍅 | P1 | WF14, WF5 | GPT-4, Notion |

---

## WF13: KPI統合ダッシュボード

### 基本情報

- **工数**: 18🍅（6ユニット）
- **目的**: Phase1-3の全データソースを統合し、KPIデータを提供するAPIを構築
- **トリガー**: Schedule（毎日 08:30）
- **実行頻度**: 毎日1回

### 設計意図

**なぜこのワークフローが必要か**:
- Phase1-3のデータがGoogle Sheets/Notionに分散している
- WF14（AIレポート）が参照する統一データソースが必要
- リアルタイムKPI可視化でビジネス判断を迅速化

### ワークフロー構成

```
[1] Schedule Trigger（毎日 08:30）
     ↓
[2] Google Sheets: LINE友だち数取得
     ↓ シート「LINE友だち追加」の行数
[3] Notion: note記事データ取得
     ↓ 記事数、総PV、総いいね数
[4] Notion: SNS投稿ログ取得
     ↓ 投稿数、エンゲージメント
[5] Notion: デモ予約データ取得
     ↓ 予約数、完了数
[6] Notion: 営業資料データ取得
     ↓ 送信数、開封数
[7] Function: KPI計算
     ↓ PV達成率、CVR、成約率、ROI
[8] Google Sheets: KPI履歴保存
     ↓ 日次KPIシート
[9] Notion: KPI統合DBに登録
     ↓ 日付、各KPI値
[10] HTTP Response: KPI API提供
     ↓ JSON形式でKPIデータ返却
```

### KPI計算ロジック

```javascript
// Function ノード
const lineFriends = $('Google Sheets: LINE友だち数').first().json.rowCount;
const noteData = $('Notion: note記事データ').all();
const snsData = $('Notion: SNS投稿ログ').all();
const demoData = $('Notion: デモ予約データ').all();
const salesData = $('Notion: 営業資料データ').all();

// PV集計
const totalPV = noteData.reduce((sum, article) => sum + (article.json.viewCount || 0), 0);
const targetPV = 22300;
const pvAchievementRate = (totalPV / targetPV * 100).toFixed(1);

// CVR計算
const demoReservations = demoData.filter(d => d.json.status === 'confirmed').length;
const demoCompleted = demoData.filter(d => d.json.status === 'completed').length;
const conversions = salesData.filter(s => s.json.opened).length;

const lineToDemoCVR = (demoReservations / lineFriends * 100).toFixed(1);
const demoToConversionCVR = (conversions / demoCompleted * 100).toFixed(1);

// 成約率
const closedDeals = 10; // 実際の成約数（外部CRMから取得）
const conversionRate = (closedDeals / demoCompleted * 100).toFixed(1);

return {
  json: {
    date: new Date().toISOString().split('T')[0],
    pv: {
      current: totalPV,
      target: targetPV,
      achievementRate: pvAchievementRate
    },
    lineFriends: lineFriends,
    note: {
      articles: noteData.length,
      totalPV: totalPV,
      avgPVPerArticle: (totalPV / noteData.length).toFixed(0)
    },
    sns: {
      posts: snsData.length,
      avgEngagement: (snsData.reduce((sum, p) => sum + (p.json.engagement || 0), 0) / snsData.length).toFixed(1)
    },
    demo: {
      reservations: demoReservations,
      completed: demoCompleted,
      conversionRate: demoToConversionCVR
    },
    cvr: {
      lineToDemo: lineToDemoCVR,
      demoToConversion: demoToConversionCVR,
      overall: ((demoReservations / lineFriends) * (conversions / demoCompleted) * 100).toFixed(2)
    },
    closedDeals: closedDeals,
    conversionRate: conversionRate
  }
};
```

### KPI API設計

**エンドポイント**: `GET /webhook/kpi-data`

**レスポンス例**:
```json
{
  "date": "2025-11-15",
  "pv": {
    "current": 18500,
    "target": 22300,
    "achievementRate": "83.0"
  },
  "lineFriends": 1200,
  "note": {
    "articles": 42,
    "totalPV": 18500,
    "avgPVPerArticle": "440"
  },
  "sns": {
    "posts": 45,
    "avgEngagement": "3.2"
  },
  "demo": {
    "reservations": 35,
    "completed": 30,
    "conversionRate": "28.5"
  },
  "cvr": {
    "lineToDemo": "2.9",
    "demoToConversion": "28.5",
    "overall": "0.83"
  },
  "closedDeals": 10,
  "conversionRate": "33.3"
}
```

---

## WF14: AIレポート自動生成

### 基本情報

- **工数**: 18🍅（6ユニット）
- **目的**: GPT-4でKPIデータを分析し、改善提案を自動生成
- **トリガー**: Schedule（毎日 09:00）
- **実行頻度**: 日次（+週次+月次）

**詳細要件**: [[タスクV_AIレポート自動生成_要件定義書]] を参照

### ワークフロー構成

```
[1] Schedule Trigger（毎日 09:00）
     ↓
[2] HTTP Request: KPIデータ取得
     ↓ WF13のKPI API呼び出し
[3] Function: データ整形
     ↓ GPT-4プロンプト用に整形
[4] GPT-4: AI分析・レポート生成
     ↓ KPI達成度、トレンド分析、問題点、改善提案
[5] Function: レポート構造化
     ↓ 改善提案を自動実行可能/手動確認に分類
[6] Notion: レポート保存
     ↓ 日次レポートDB
[7] LINE Notify: サマリー通知
     ↓ 「📊 日次レポート完了」
[8] IF: 自動実行判定
     ├→ YES: WF15/WF16トリガー
     └→ NO: Slack通知（手動確認依頼）
[9] HTTP Request: WF15/WF16連携
     ↓ 自動実行可能な提案を送信
```

### GPT-4プロンプト（詳細版）

```
あなたはMEO集客自動化プロジェクトのデータアナリストです。
以下のKPIデータを分析し、改善提案を行ってください。

【KPIデータ】
- PV: {current_pv} / 目標22,300 ({achievement_rate}%)
- CVR: {current_cvr}% / 目標30%
- LINE友だち: {line_friends}人
- note記事: {note_articles}本
- SNS投稿: {sns_posts}本
- デモ予約: {demo_reservations}件
- 成約率: {conversion_rate}%

【前日比データ】
- PV: {pv_change}% ({pv_change_abs})
- CVR: {cvr_change}% ({cvr_change_abs})
- LINE友だち: +{line_friends_change}人

【分析観点】
1. 目標達成度の評価（現状 vs 目標）
2. 前日比・前週比のトレンド分析
3. 問題点・ボトルネックの特定
4. 改善提案（優先度順、Top 5）

【出力形式】
以下の構造化されたMarkdown形式で出力してください：

## 📊 KPI達成度サマリー
| KPI | 現在値 | 目標 | 達成率 | 前日比 | 評価 |
|-----|--------|------|--------|--------|------|
...

## 📈 トレンド分析
### PV推移
- 週次: ...
- 月次: ...
- 傾向: ...

## ⚠️ 問題点・ボトルネック
### 1. [問題タイトル]
- 原因: ...
- 影響: ...

## 💡 改善提案（優先度順）
### 🔥 提案1: [タイトル]
- 期待効果: ...
- 実行難易度: 低/中/高
- 推奨実施時期: 即時/3日以内/1週間以内
- 具体的アクション: ...
- **自動実行可能**: YES/NO

...（提案2-5も同様）

## 🤖 自動実行予定
以下の施策は自動実行可能なため、本レポート生成後に実行されます：
✅ 提案X: ...

## 📌 手動確認が必要な施策
以下は人間の判断が必要です：
⚠️ 提案Y: ...
```

### 自動実行判定ロジック

```javascript
// Function ノード: レポート構造化
const report = $('GPT-4: AI分析').first().json.choices[0].message.content;

// 改善提案を抽出
const proposalRegex = /### 🔥 提案(\d+): (.+?)\n[\s\S]*?自動実行可能: (YES|NO)/g;
const proposals = [];
let match;

while ((match = proposalRegex.exec(report)) !== null) {
  const proposalNumber = parseInt(match[1]);
  const proposalTitle = match[2];
  const autoExecutable = match[3] === 'YES';

  proposals.push({
    number: proposalNumber,
    title: proposalTitle,
    autoExecutable: autoExecutable
  });
}

// 自動実行可能な提案を抽出
const autoProposals = proposals.filter(p => p.autoExecutable);

return {
  json: {
    report_markdown: report,
    proposals: proposals,
    autoProposals: autoProposals,
    hasAutoProposals: autoProposals.length > 0,
    generated_at: new Date().toISOString()
  }
};
```

---

## WF15: 人気記事再配信

### 基本情報

- **工数**: 12🍅（4ユニット）
- **目的**: WF14の改善提案に基づき、人気記事をSNS/LINEで自動再配信
- **トリガー**: Webhook（WF14からの自動実行指示）
- **実行頻度**: イベント駆動

### 設計意図

**なぜこのワークフローが必要か**:
- 人気記事の再活用でPV底上げ
- AI判断で最適な記事・タイミングで再配信
- 完全自動化によりPDCAサイクル高速化

### ワークフロー構成

```
[1] Webhook Trigger（WF14からの自動実行指示）
     ↓ proposalDetails: {articleId, platform, timing}
[2] Notion: 記事データ取得
     ↓ title, url, bodyPreview
[3] GPT-4: 再配信用投稿文生成
     ↓ 「再掲: {タイトル}」形式
[4] Function: プラットフォーム判定
     ↓ X/Instagram/LINE
[5] IF: プラットフォーム別分岐
     ├→ X: HTTP Request (X API)
     ├→ Instagram: HTTP Request (Instagram API)
     └→ LINE: HTTP Request (LINE Messaging API)
[6] Notion: 再配信ログ保存
     ↓ articleId, platform, redistributedAt
[7] Slack: 再配信完了通知
     ↓ 「🔥 人気記事再配信: {タイトル} → {プラットフォーム}」
```

### 再配信戦略

**頻度制限**:
- 同じ記事は週1回まで
- 同じプラットフォームは日1回まで

**最適タイミング**:
- X: 20:00-21:00（エンゲージメント最高時間帯）
- Instagram: 22:00-23:00
- LINE: 19:00（金曜夜）

---

## WF16: トピック再学習

### 基本情報

- **工数**: 12🍅（4ユニット）
- **目的**: WF14の改善提案に基づき、トピックマスタを更新
- **トリガー**: Webhook（WF14からの自動実行指示）
- **実行頻度**: イベント駆動

### 設計意図

**なぜこのワークフローが必要か**:
- トレンド変化に自動追従
- 人気トピックの自動発見・追加
- 不人気トピックの自動アーカイブ

### ワークフロー構成

```
[1] Webhook Trigger（WF14からの自動実行指示）
     ↓ proposalDetails: {newTopics, archiveTopics}
[2] Notion: トピックマスタ取得
     ↓ 現在のトピックリスト
[3] Function: トピック差分計算
     ↓ 追加すべきトピック、削除すべきトピック
[4] Loop: 新規トピックごと処理
     ├→ [5] GPT-4: トピック詳細生成
     ├→ [6] Notion: トピックマスタに追加
     └→ [7] Function: 関連キーワード抽出
[8] Loop: アーカイブトピックごと処理
     └→ [9] Notion: Status='archived'に更新
[10] Slack: トピック更新通知
     ↓ 「📚 トピック更新: +{N}件, -{M}件」
```

---

## AI自走の証明

### Phase4完了判定基準

**必須条件**:
1. **7日間連続、人間が何もしなくてもレポートが生成され続ける**
   - [ ] 日次レポート: 7件生成
   - [ ] レポート生成成功率: 100%

2. **その間に自動実行された施策が3つ以上ある**
   - [ ] WF15（人気記事再配信）: 最低2回実行
   - [ ] WF16（トピック再学習）: 最低1回実行

3. **KPIが改善傾向にある（CVR +0.5%以上）**
   - [ ] CVR: {開始時}% → {7日後}% (+0.5%以上)
   - [ ] PV: 横ばいor増加傾向

### AI自走の定義

**完全自動PDCAサイクル**:

```
[P: Plan] WF14 - AIレポート
   ↓ データ分析 → 改善提案生成
[D: Do] WF15/WF16 - 自動実行
   ↓ 提案を実行 → 施策実施
[C: Check] WF13 - KPI計測
   ↓ 翌日KPI取得 → 効果測定
[A: Action] WF14 - 次の提案
   ↓ 新たな改善提案 → サイクル継続
```

**人間の役割**:
- 自動実行不可の施策の承認
- 戦略レベルの意思決定
- システム異常時の介入
- 新機能の企画

---

## 関連ドキュメント

- [[MEO集客自動化_n8nワークフロー全体構成]]
- [[Phase1_n8nワークフロー詳細設計書]]
- [[Phase2_n8nワークフロー詳細設計書]]
- [[Phase3_n8nワークフロー詳細設計書]]
- [[タスクV_AIレポート自動生成_要件定義書]] ← WF14の詳細要件

---

## 更新履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|----------|--------|
| 1.0 | 2025-10-27 | 初版作成 - Phase4全ワークフロー設計 | Claude + User |

---

**次のステップ**: Phase3完了後にWF13から順次実装し、AI自走を実現
