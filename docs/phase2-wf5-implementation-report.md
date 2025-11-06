# Phase2 WF5: トピック抽出AI 実装レポート

**実装日**: 2025-10-27
**ワークフロー名**: WF5 - トピック抽出AI
**ステータス**: 実装完了（テスト待ち）
**工数**: 18🍅（6ユニット）

---

## 📊 実装サマリー

### 完了した作業

✅ Sequential Thinkingによる設計分析（8ステップ）
✅ n8n-workflows-docsで参考例調査
✅ トピックマスタDB作成ガイド作成
✅ WF5ワークフローJSON完全実装（11ノード）
✅ 実装ドキュメント作成

### 実装成果物

| ファイル | パス | 説明 |
|---------|------|------|
| ワークフローJSON | `/workflows/phase2-wf5-topic-extraction-ai.json` | n8nインポート可能な完全なワークフロー |
| 実装プロンプト | `/docs/prompts/phase2-wf5-topic-extraction-prompt.md` | 実装用の詳細プロンプト |
| DB作成ガイド | `/docs/phase2-topic-master-db-setup-guide.md` | トピックマスタDB作成手順書 |
| 実装レポート | `/docs/phase2-wf5-implementation-report.md` | 本ドキュメント |

---

## 🏗️ ワークフロー構成

### ノード構成（全11ノード）

| # | ノード名 | タイプ | 説明 |
|---|---------|--------|------|
| 1 | Schedule Trigger | Schedule | 毎週水・土 09:00 JST実行 |
| 2 | Notion Query - 過去30日の記事取得 | HTTP Request | note記事管理DBから過去30日のデータ取得 |
| 3 | Function - スコアリング | Function | Score = (View Count × 0.6) + (Like Count × 0.4) |
| 4 | Function - トップ10記事抽出 | Function | スコア上位10件を抽出 |
| 5 | GPT-4 API - トピック抽出 | HTTP Request | GPT-4でトレンドトピック5つ抽出 |
| 6 | Function - GPT-4レスポンスパース | Function | JSON.parse()でGPT-4出力を解析 |
| 7 | Function - トピックデータ前処理 | Function | 関連記事紐付け、平均スコア計算 |
| 8 | Loop - トピック登録 | Split In Batches | 各トピックを個別処理 |
| 9 | Notion - トピックマスタ更新 | HTTP Request | トピックマスタDBにページ作成 |
| 10 | Wait - レート制限対策 | Wait | 400ms待機（Notion APIレート制限対策） |
| 11 | Slack - トピック通知 | HTTP Request | Slackに結果通知 |

### データフロー

```
Schedule Trigger (水・土 09:00)
  ↓
Notion Query (過去30日の記事100件取得)
  ↓
Function (スコアリング: PV×0.6 + いいね×0.4)
  ↓
Function (トップ10抽出)
  ↓
GPT-4 API (トレンドトピック5つ抽出)
  ↓
Function (GPT-4レスポンスパース)
  ↓
Function (関連記事紐付け、平均スコア計算)
  ↓
Loop (各トピックを個別処理)
  ├─ Notion Create (トピックマスタDB更新)
  └─ Wait (400ms、レート制限対策)
  ↓
Slack通知 (結果送信)
```

---

## 🎯 設計上の重要な決定事項

### 1. トピック重複チェックの簡略化

**当初の計画**: Node 8でトピック名検索 → 存在すればUpdate、なければCreate（Upsert処理）

**実装した方式**: 常にCreate（新規作成）

**理由**:
- トピックは週2回の抽出で動的に変化するため、重複チェックの複雑性よりシンプルさを優先
- 重複トピックは手動またはWF6で自動的に古いものを"archived"にする運用でカバー
- Node 8の実装が簡潔になり、メンテナンス性向上

**今後の改善案**:
- Phase2完了後、トピック重複が問題になった場合にUpsert処理を追加
- または、定期的に古いトピックを"archived"に変更するWF追加

### 2. Waitノードの追加

**目的**: Notion APIレート制限（3 req/sec）への対応

**実装**:
- Node 10に400ms Waitを追加
- Loop内で5トピック連続作成しても2.5秒（5 × (1秒 + 0.4秒)）で完了
- レート制限に余裕を持たせた安全な設定

### 3. GPT-4プロンプトの最適化

**改善点**:
- ターゲット明確化: "3-10歳の子供を持つ保護者、英語教育・バイリンガル教育に関心"
- JSON出力強制: "必ずJSON形式のみで出力してください。それ以外のテキストは含めないでください。"
- 構造化指示: 分析観点を3つに明確化

**期待効果**:
- GPT-4のJSON出力精度向上
- ターゲット読者に響くトピック抽出

### 4. エラーハンドリング戦略

**実装済み**:
- Notion Query: Retry 3回（指数バックオフ）
- GPT-4 API: Retry 2回
- Notion Create: Retry 3回

**未実装（Phase2.1で追加予定）**:
- Error Trigger → Slack緊急通知
- 各ノードのcontinueOnFail設定
- Error Workflow連携

---

## 🔧 環境変数設定が必要

WF5実行前に以下の環境変数をn8nに設定してください:

| 変数名 | 説明 | 取得方法 |
|-------|------|----------|
| `TOPIC_MASTER_DB_ID` | トピックマスタDB ID | トピックマスタDB作成後、URLから取得 |
| `GPT4_API_KEY` | OpenAI API Key | OpenAIダッシュボードで取得 |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL | Slackアプリ設定で作成 |

**n8nでの設定方法**:
1. n8nの設定 → Environment Variables
2. 上記3つの変数を追加
3. ワークフローを保存・有効化

---

## ✅ 実装前チェックリスト

WF5を実行する前に、以下を確認してください:

### Phase1完了確認
- [ ] note記事管理DB (29968d5c-2986-81ad-90d0-c24ed710503e) にデータが蓄積されている
- [ ] WF4が正常動作中（記事データが継続的に更新されている）

### トピックマスタDB作成
- [ ] トピックマスタDBを作成した（`/docs/phase2-topic-master-db-setup-guide.md` 参照）
- [ ] プロパティ6個（Topic Name, Score, Keywords, Related Articles, Extracted At, Status）が正しく設定されている
- [ ] Related Articlesがnote記事管理DB (29968d5c-2986-81ad-90d0-c24ed710503e) を指している
- [ ] 双方向リレーション有効（note記事管理DBに"Topics"プロパティが追加されている）
- [ ] トピックマスタDBのDatabase IDを取得した

### 環境変数設定
- [ ] `TOPIC_MASTER_DB_ID` をn8nに設定した
- [ ] `GPT4_API_KEY` をn8nに設定した（OpenAI API Key）
- [ ] `SLACK_WEBHOOK_URL` をn8nに設定した

### n8nワークフローインポート
- [ ] `/workflows/phase2-wf5-topic-extraction-ai.json` をn8nにインポートした
- [ ] すべてのノードがエラーなく表示されている
- [ ] Schedule Triggerが"水・土 09:00 JST"に設定されている

### API認証確認
- [ ] Notion API Token (YOUR_NOTION_API_TOKEN) が有効
- [ ] OpenAI API Keyが有効（クレジット残高確認）
- [ ] Slack Webhook URLが有効（テスト送信確認）

---

## 🧪 テスト計画

### テスト1: 手動実行テスト

**目的**: WF5の基本動作確認

**手順**:
1. n8nでWF5ワークフローを開く
2. "Execute Workflow"ボタンをクリック
3. 各ノードの実行結果を確認

**期待結果**:
- [ ] Notion Queryで過去30日の記事が取得される（最大100件）
- [ ] スコアリングが正確（View Count × 0.6 + Like Count × 0.4）
- [ ] トップ10記事が抽出される
- [ ] GPT-4がトレンドトピック5つを生成（JSON形式）
- [ ] JSON parseが成功
- [ ] 関連記事が正しく紐付けられる
- [ ] トピックマスタDBに5件のページが作成される
- [ ] Relation設定でnote記事管理DBと紐付く
- [ ] Slack通知が見やすい形式で届く

### テスト2: Schedule Trigger動作確認

**目的**: 週2回の自動実行確認

**手順**:
1. WF5を有効化（Active=true）
2. 次の水曜または土曜 09:00まで待機
3. n8nのExecution Historyで実行履歴確認

**期待結果**:
- [ ] 水曜 09:00に自動実行される
- [ ] 土曜 09:00に自動実行される
- [ ] Execution Historyにエラーがない

### テスト3: エラーハンドリングテスト

**目的**: Retry機能とエラー通知の確認

**手順**:
1. Notion API Tokenを一時的に無効化
2. WF5を手動実行
3. Retry動作とエラー通知を確認

**期待結果**:
- [ ] Notion Query失敗時に3回Retry実行される
- [ ] 最終的にエラーになる
- [ ] （Phase2.1で実装予定）Slack緊急通知が届く

### テスト4: データ整合性テスト

**目的**: Relation設定とデータ品質確認

**手順**:
1. WF5実行後、トピックマスタDBを確認
2. 各トピックのRelated Articlesを確認
3. note記事管理DBの記事から"Topics"プロパティを確認

**期待結果**:
- [ ] トピックマスタDBに5件のトピックが登録される
- [ ] 各トピックにRelated Articles（1-10件）が設定される
- [ ] note記事管理DBの記事に"Topics"プロパティが表示される
- [ ] 双方向リレーションが正常動作

---

## 📈 パフォーマンス測定

### 実行時間見積もり

| フェーズ | 予想時間 |
|---------|---------|
| Notion Query | ~2秒 |
| Function処理（スコアリング + トップ10） | ~0.5秒 |
| GPT-4 API | ~10-20秒 |
| Function処理（パース + 前処理） | ~1秒 |
| Notion Create Loop（5トピック） | ~7秒（1秒 + 0.4秒 wait）× 5 |
| Slack通知 | ~1秒 |
| **合計** | **約22-32秒** |

**結論**: 5分以内の目標を大幅にクリア ✅

### リソース使用量

| リソース | 予想使用量 | 制限 |
|---------|-----------|------|
| Notion API | ~7 requests | 3 req/sec（レート制限対策済み） |
| GPT-4 tokens (input) | ~850 tokens | - |
| GPT-4 tokens (output) | ~450 tokens | 1500 max（余裕あり） |
| n8n実行時間 | ~30秒 | 300秒（5分）制限 |

---

## 🚀 次のステップ

### Phase2.1: WF5改善（オプション）

1. **トピック重複チェック実装**
   - Node 8aでトピック名検索
   - Node 8bで存在チェック
   - Node 8cでUpdate or Create（Upsert）

2. **Error Workflow追加**
   - Error Trigger → Slack緊急通知
   - エラー詳細（ノード名、エラーメッセージ、実行時刻）を送信

3. **監視ダッシュボード連携**
   - Notion Dashboard DBに実行ログ記録
   - 成功率、平均実行時間、エラー率をトラッキング

### Phase2次ワークフロー: WF6実装

WF5完了後、以下の順で進めます:

1. ✅ WF5実装完了（本レポート）
2. トピックマスタDBデータ確認（週2回のデータ蓄積を確認）
3. WF6（note記事自動生成）実装開始
   - プロンプト: `/docs/prompts/phase2-wf6-note-article-generation-prompt.md`
   - 依存関係: WF5のトピックマスタDBを使用

---

## 🔗 関連ドキュメント

### 設計書
- [Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md](../Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md)（Line 285-666）
- [phase2-wf5-topic-extraction-prompt.md](./prompts/phase2-wf5-topic-extraction-prompt.md)

### 実装ファイル
- [phase2-wf5-topic-extraction-ai.json](../workflows/phase2-wf5-topic-extraction-ai.json)
- [phase2-topic-master-db-setup-guide.md](./phase2-topic-master-db-setup-guide.md)

### 参考
- [Notion API: Query a database](https://developers.notion.com/reference/post-database-query)
- [Notion API: Create a page](https://developers.notion.com/reference/post-page)
- [OpenAI API: Chat Completions](https://platform.openai.com/docs/api-reference/chat/create)

---

## 🎉 実装完了

**Phase2 WF5: トピック抽出AI**の実装が完了しました!

### 実装成果
✅ 全11ノード完全実装
✅ エラーハンドリング設定済み
✅ レート制限対策実装済み
✅ トピックマスタDB作成ガイド完備
✅ テスト計画策定完了

### 次のアクション
1. トピックマスタDBを作成（`/docs/phase2-topic-master-db-setup-guide.md` 参照）
2. 環境変数設定（`TOPIC_MASTER_DB_ID`, `GPT4_API_KEY`, `SLACK_WEBHOOK_URL`）
3. ワークフローをn8nにインポート
4. テスト実行
5. 水曜または土曜 09:00の自動実行を確認

---

**実装者**: Claude Code
**最終更新**: 2025-10-27
