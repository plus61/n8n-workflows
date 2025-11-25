# コンテンツ自動運用システム  
## WF-A / WF-B 目的と要件定義書（v0.1）

---

# 🎯 1. 本ドキュメントの目的

本ドキキュメントは、現在開発中の **WF-A（記事生成ワークフロー）** および  
**WF-B（記事改善・次アクション提示ワークフロー）** の目的・要件・仕様を正式にまとめた  
**要件定義書** である。

この .md ファイルは Claude Code MCP や Cursor プロジェクトにそのまま利用できる。

---

# 🚀 2. システム全体像（概要）

このシステムは下記 2 本のワークフローで構成される：

---

## ⭐ WF-A：Generate Note Drafts from Editorial Ideas  
Google Sheets に登録された「status=idea」のレコードを元に  
**DMMmodel（思想）を反映した note 記事ドラフトを自動生成**する。

---

## ⭐ WF-B：Analyze Note Performance & Suggest Next Actions  
公開済み記事（status=published）を元に  
**記事パフォーマンスの分析と “次に取るべき行動” をAIが自動生成**する。

---

これらにより、  
**コンテンツ生成 → 投稿 → 分析 → 改善 → 再生成**  
のループを自動化できる。

---

# 🎯 3. WF-A：記事生成ワークフローの目的

## 3-1. ゴール

1. Google Sheets の `status=idea` を材料に **記事ドラフトを完全自動生成**する  
2. 生成物に **プロジェクト思想（mdc）を100%適用**する  
3. 生成したドラフトを **Google Sheets に記録**  
4. Slack に通知し、次のアクション（note投稿）を人間が判断できる状態にする  

---

## 3-2. 成果物

- generated_title  
- generated_body  
- generated_segment  
- Google Sheets 更新  
- Slack 通知  

---

## 3-3. 完了条件

- idea 行がすべて draft-generated に更新されている  
- タイトル／本文が Sheets に格納されている  
- Slack に通知が届いている  
- JSONパースがエラーなく完了している  

---

# 📌 4. WF-A：要件定義

## 4-1. 入力データ

Google Sheets（Editorial）：

| カラム名 | 説明 |
|---------|------|
| status | idea の行のみ処理対象 |
| trending_keyword | AI生成の中心になるキーワード |
| abstract | ニュースの要約（外部WF生成） |
| segment | 初回は空でOK（default_segment を適用） |
| rowNumber | シート更新キー |

---

## 4-2. 使用AIモデル

- OpenAI Chat Completions  
- GPT-4.1-mini  
- system に `.mdc_content` を全文渡す  

---

## 4-3. 機能要件

1. `status=idea` をフィルタ  
2. mdc_content の付与  
3. 記事ドラフトを JSON形式でAI生成  
4. Google Sheets 更新  
5. Slack 通知  

---

## 4-4. 非機能要件

- JSON整形保持（壊れないこと）  
- 1300〜2500字の本文安定生成  
- Slack通知に本文冒頭300字を含める  

---

# 🎯 5. WF-B：記事改善ワークフローの目的

## 5-1. ゴール

1. 公開済み（published）記事のパフォーマンスをAIが分析  
2. 記事の「keep / improve / stop」を自動判定  
3. 次のキーワード・次のセグメントなど“次アクション”を提案  
4. Google Sheets に書き戻し  
5. Slack にレポート通知  

---

## 5-2. 成果物

- next_decision  
- next_action  
- next_segment  
- next_keyword_idea  
- Slack レポート  

---

## 5-3. 完了条件

- 全 published 行に next_* が記録されている  
- Slack にレポートが届いている  
- 分析内容が DMMmodel に沿っている  
- JSONパースが正常に完了  

---

# 📌 6. WF-B：要件定義

## 6-1. 入力データ

Google Sheets（Editorial）：

| カラム名 | 説明 |
|---------|------|
| status | published の行が対象 |
| note_title | 公開済み記事タイトル |
| note_url | URL |
| note_pv | PV数 |
| note_likes | Like数 |
| note_conversion | CV |
| segment | セグメント情報 |

---

## 6-2. 使用AIモデル

- OpenAI Chat Completions  
- GPT-4.1-mini  
- system に `.mdc_content` を渡す（思想ベース分析）  

---

## 6-3. 機能要件

1. `status=published` 行の抽出  
2. mdc_content の付与  
3. パフォーマンス分析（JSON出力）  
4. Google Sheets に書き戻し  
5. Slack 通知  

---

## 6-4. 非機能要件

- DMMmodel 思想に従った分析・提案  
- keep / improve / stop の理由を JSON内に明記  
- Slack テキストはそのまま人間の意思決定に使える品質  

---

# 🔧 7. 今後の拡張予定

- note 自動投稿の自動化  
- GA4 / Search Console の自動収集連携  
- WF-A/B の完全ループ化  
- セグメント自動推定器の導入  
- Slack ボタン承認の導入  

---

# 📎 8. 本ドキュメントの用途

- Claude Code MCP への仕様渡し  
- n8nワークフロー改修の基礎資料  
- プロジェクト内の思想・ルールの共有  
- `.mdc` のバージョン管理の基準

---

# ✔️ ファイル情報
- ファイル名：`WF-A_B_requirement_v0_1.md`
- バージョン：v0.1
- 作者：ChatGPT生成（あなたの指示に基づく）
