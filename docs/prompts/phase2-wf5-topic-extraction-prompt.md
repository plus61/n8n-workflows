# Phase2 WF5: トピック抽出AI 実装プロンプト

**作成日**: 2025-10-27
**対象ワークフロー**: WF5 - トピック抽出AI
**カテゴリー**: 新規ワークフロー作成
**優先度**: P0（高）
**工数見積**: 18🍅（6ユニット）

---

## 実装用プロンプト

```markdown
@mcp-sequential-thinking
@n8n-workflows-docs
@n8n-mcp

Phase2のトピック抽出AIワークフロー（WF5）を作成したいです。段階的に設計して実装してください。

【背景・現状】
- Phase1完了: note記事管理DBに記事データ蓄積済み（Database ID: 29968d5c-2986-81ad-90d0-c24ed710503e）
- 手動でトピック選定すると属人的になり、PV最大化の機会を逃す
- 過去記事の人気度を定量評価できていない
- Google Sheetsは使用しない（Phase1でNotion単独管理に変更）
- Phase1のWF4で記事データが継続的に蓄積されている

【目標・要件】
目的: note記事管理DBから人気記事を分析し、データ駆動でトレンドトピックを抽出

トリガー: Schedule（週2回：水曜・土曜 09:00 JST）
実行頻度: 週2回

入力データ:
- ソース: Notion note記事管理DB（過去30日間のデータ）
- Database ID: 29968d5c-2986-81ad-90d0-c24ed710503e
- フィルター条件:
  - Status = "検知済み" OR "分析済み"
  - Published Date: 過去30日以内
- 取得プロパティ: Title, URL, Article ID, View Count, Like Count, Description, Category, Published Date

処理内容:
1. Notion APIでnote記事管理DBから過去30日のデータ取得（最大100件）
2. スコアリング処理: Score = (View Count × 0.6) + (Like Count × 0.4)
3. スコア上位10件を抽出
4. GPT-4 APIでトピック抽出（共通キーワード、ユーザーニーズ、次のトピック5つ）
5. トピックマスタDB更新（Relation設定で関連記事リンク）
6. Slack通知: #トレンド分析チャネルに結果送信

出力:
- 保存先: Notion トピックマスタDB（新規作成必要）
- 通知先: Slack #トレンド分析
- エラー時: Slack #エラー通知に詳細送信

【トピックマスタDB設計】
Database名: トピックマスタ
作成タイミング: WF5実装前に作成必要

プロパティ:
```yaml
Topic Name (title): トピック名
Score (number): 人気度スコア（計算式: avg_view_count * 0.6 + avg_like_count * 0.4）
Keywords (multi_select): 関連キーワード（例: ["MEO", "Googleマップ", "集客"]）
Related Articles (relation): 関連記事リスト（Relation先: note記事管理DB 29968d5c-2986-81ad-90d0-c24ed710503e）
Extracted At (date): 抽出日時
Status (select): active（緑）/ archived（灰）
```

【制約条件】
使用サービス:
- Notion API（認証済み: Bearer Token YOUR_NOTION_API_TOKEN）
- GPT-4 API（model: gpt-4-turbo-preview, temperature: 0.7）
- Slack Webhook API

使用禁止:
- Google Sheets（Phase1で廃止済み）
- note記事管理DB以外のデータソース

パフォーマンス:
- Notion API レート制限: 3 requests/sec
- 実行時間制限: 5分以内推奨
- GPT-4 max_tokens: 1500

データ整合性:
- Relation設定で記事とトピックを正しく紐付け
- トピック重複チェック必須
- エラー時はロールバック不要（次回実行時に再処理）

【詳細ノード構成】
1. Schedule Trigger
   - Cron: 0 9 * * 3,6 （毎週水・土 09:00 JST）
   - Timezone: Asia/Tokyo

2. HTTP Request: Notion Query（過去30日の記事取得）
   - URL: https://api.notion.com/v1/databases/29968d5c-2986-81ad-90d0-c24ed710503e/query
   - Headers: Authorization, Notion-Version: 2022-06-28
   - Body: filter（Status OR条件 + Published Date after条件）, sorts（View Count descending）
   - page_size: 100

3. Function Node: スコアリング
   - Notion APIレスポンス構造に対応
   - props.Title?.title[0]?.text?.content 形式でプロパティ抽出
   - スコア計算: (viewCount * 0.6) + (likeCount * 0.4)
   - 降順ソート

4. Function Node: トップ10記事抽出
   - スコア上位10件を slice(0, 10)
   - 配列を1つのJSONオブジェクトにまとめる

5. HTTP Request: GPT-4 API（トピック抽出）
   - model: gpt-4-turbo-preview
   - system role: "あなたはコンテンツストラテジストです"
   - user prompt:
     - 人気note記事データから共通キーワード抽出
     - ユーザーニーズ推定
     - 次に書くべきトピック5つ（優先度順、理由付き）
   - JSON形式出力: {trendKeywords: [], userNeeds: "", nextTopics: [{topic, priority, reason}]}
   - temperature: 0.7, max_tokens: 1500

6. Function Node: GPT-4レスポンスパース
   - JSON.parse()でGPT-4出力を解析
   - パースエラー時はthrow Error（Slack通知へ）

7. Function Node: トピックデータ前処理
   - 各トピックに関連記事を紐付け（キーワードマッチング）
   - 関連記事のNotion Page IDを抽出
   - 平均スコア計算: relatedArticles.reduce((sum, a) => sum + a.score, 0) / length
   - 配列で返す: [{topic, priority, reason, trendKeywords, relatedArticleIds, avgScore}]

8. Loop: Notion トピックマスタ更新（各トピックごと）
   - HTTP Request: POST https://api.notion.com/v1/pages
   - parent.database_id: {{TOPIC_MASTER_DB_ID}}（事前作成必要）
   - properties:
     - Topic Name: title
     - Score: number
     - Keywords: multi_select
     - Related Articles: relation（page id配列）
     - Extracted At: date（$now.toISO()）
     - Status: select（"active"）

9. HTTP Request: Slack通知
   - URL: {{SLACK_WEBHOOK_URL}}
   - Body:
     - header: "🔥 トレンドトピック Top 5"
     - section: 各トピック（番号、タイトル、スコア、関連記事数、理由）
     - section: トレンドキーワード一覧

【エラーハンドリング】
Notion API失敗（記事取得）:
- Retry: 3回（指数バックオフ 1s, 2s, 4s）
- Fallback: Slack警告通知 + 処理中断
- 重大度: High

GPT-4 API失敗（トピック抽出）:
- Retry: 2回（1s間隔）
- Fallback: 前回のトピックデータ使用 + Slack通知
- 重大度: Medium

JSON Parse失敗:
- Retry: なし
- Fallback: Slack緊急通知（エラー詳細 + GPT-4生レスポンス） + 手動確認要求
- 重大度: High

Notion API失敗（トピック登録）:
- Retry: 3回
- Fallback: 次回実行時に再処理（べき等性考慮）
- 重大度: Medium

【依頼内容】
1. Sequential Thinkingで設計を段階的に考える
   - Zie619から類似のNotion Query + GPT-4統合ワークフローを探す
   - エラーハンドリング戦略の最適化
   - Notion Relation設定のベストプラクティス確認
   - トピック重複チェックの実装方針

2. n8n-workflows-docsで参考例を探す
   - Notion API Queryの実装パターン
   - GPT-4 API統合のベストプラクティス
   - Schedule Triggerの設定例
   - Slack通知のリッチフォーマット

3. トピックマスタDBの作成支援
   - Notion API経由での作成が可能か確認
   - 手動作成の場合は詳細な手順提示
   - Relation設定の注意点を明示

4. n8n-mcpで実装
   - 全9ノードを作成・接続
   - エラーハンドリング設定
   - リトライポリシー設定
   - テスト用データでの動作確認

5. バリデーションと最適化
   - continueOnFail設定の確認
   - Notion APIレート制限への対応
   - GPT-4 token使用量の最適化
   - 実行時間の測定と改善提案

【参考情報】
Phase1設計書: Phase1_n8nワークフロー詳細設計書
Phase2設計書: Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md
既存Database ID: 29968d5c-2986-81ad-90d0-c24ed710503e
Notion API Token: YOUR_NOTION_API_TOKEN

【成功の基準】
- ワークフローが正常に実行される（エラー率 <1%）
- トピックマスタDBに5件のトピックが登録される
- 各トピックに正しく関連記事がRelation設定される
- Slack通知が見やすい形式で送信される
- 実行時間が5分以内
- 次週のWF6（記事自動生成）で使用可能な状態
```

---

## 実装後の検証項目

### 機能検証
- [ ] Schedule Triggerが水曜・土曜09:00に正常動作
- [ ] Notion APIから過去30日のデータ取得成功（フィルター正常）
- [ ] スコアリング計算が正確（View Count × 0.6 + Like Count × 0.4）
- [ ] トップ10記事が正しく抽出される
- [ ] GPT-4が適切なトピックを5つ生成
- [ ] トピックマスタDBに正しく登録される
- [ ] Relation設定で記事とトピックが正しく紐付く
- [ ] Slack通知が見やすい形式で届く

### エラーハンドリング検証
- [ ] Notion API障害時にリトライ3回実行
- [ ] GPT-4 API障害時にリトライ2回実行
- [ ] JSON Parse失敗時にSlack緊急通知送信
- [ ] 各エラーで適切なログが記録される

### パフォーマンス検証
- [ ] 実行時間が5分以内
- [ ] Notion APIレート制限に抵触しない
- [ ] GPT-4 token使用量が1500以内
- [ ] メモリ使用量が適切

### データ整合性検証
- [ ] トピック重複が発生しない
- [ ] Relation IDが正確
- [ ] Status = "active" が正しく設定される
- [ ] Extracted Atが正確なタイムスタンプ

---

## 次のステップ

WF5完了後:
1. トピックマスタDBのデータ確認
2. WF6（note記事自動生成）の実装準備
3. WF5とWF6の統合テスト計画作成

---

## 関連ドキュメント

- [Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md](../../Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md)
- [Phase1_実装変更点サマリー_Phase2への影響分析](../../Phase1_実装変更点サマリー_Phase2への影響分析.md)
- [プロンプト設計指針書](../prompt-design-guide.md)

---

**最終更新**: 2025-10-27
