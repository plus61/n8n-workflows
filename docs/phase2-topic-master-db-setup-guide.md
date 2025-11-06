# トピックマスタDB作成ガイド

**作成日**: 2025-10-27
**用途**: Phase2 WF5（トピック抽出AI）で使用
**作成タイミング**: WF5実装前に必須

---

## 📋 概要

WF5トピック抽出AIワークフローで使用する「トピックマスタ」データベースを手動で作成する手順です。

---

## 🎯 データベース仕様

### 基本情報
- **Database名**: `トピックマスタ`
- **親ページ**: note記事管理DBと同じ親ページ推奨
- **用途**: GPT-4で抽出したトレンドトピックを保存

### プロパティ設計（全6個）

| プロパティ名 | タイプ | 設定 | 説明 |
|------------|--------|------|------|
| Topic Name | title | - | トピック名（例: "MEO対策の基礎"） |
| Score | number | format: number | 人気度スコア（計算式: avg_view_count × 0.6 + avg_like_count × 0.4） |
| Keywords | multi_select | - | 関連キーワード（例: ["MEO", "Googleマップ", "集客"]） |
| Related Articles | relation | database: note記事管理DB<br>type: two-way (dual_property)<br>synced_property_name: "Topics" | 関連記事リスト（Relation先: note記事管理DB 29968d5c-2986-81ad-90d0-c24ed710503e） |
| Extracted At | date | - | 抽出日時 |
| Status | select | options:<br>- active（緑）<br>- archived（灰） | トピックのステータス |

---

## 📝 作成手順（Notion GUI）

### ステップ1: 新規データベース作成

1. Notionで note記事管理DB のページを開く
   - URL: https://www.notion.so/29968d5c298681ad90d0c24ed710503e

2. 同じ親ページ（またはワークスペースのトップ）に新規ページ作成
   - ページタイトル: `トピックマスタ`

3. ページ内で `/database` と入力 → 「テーブル - インライン」を選択

### ステップ2: プロパティ設定

#### 2-1. Topic Name（title）
- デフォルトの「Name」列をクリック
- 「名前を変更」→ `Topic Name`
- タイプ: title（変更不要）

#### 2-2. Score（number）
1. 右上の「+」ボタンをクリック
2. プロパティ名: `Score`
3. タイプ: `数値`
4. 形式: `数値`（デフォルト）

#### 2-3. Keywords（multi_select）
1. 右上の「+」ボタンをクリック
2. プロパティ名: `Keywords`
3. タイプ: `マルチセレクト`
4. オプション: 空（後でWF5が自動的にキーワードを追加）

#### 2-4. Related Articles（relation）⚠️ 重要
1. 右上の「+」ボタンをクリック
2. プロパティ名: `Related Articles`
3. タイプ: `リレーション`
4. **設定（重要）**:
   - 「データベースを選択」→ `note記事管理` を選択
     - Database ID: 29968d5c-2986-81ad-90d0-c24ed710503e
   - **双方向リレーションを有効化**: ✅ チェックを入れる
   - 逆参照プロパティ名: `Topics`（note記事管理DB側に自動作成される）

**確認**: note記事管理DBに `Topics` プロパティが自動追加されているか確認

#### 2-5. Extracted At（date）
1. 右上の「+」ボタンをクリック
2. プロパティ名: `Extracted At`
3. タイプ: `日付`
4. 日付形式: `YYYY-MM-DD HH:mm`（デフォルト）

#### 2-6. Status（select）
1. 右上の「+」ボタンをクリック
2. プロパティ名: `Status`
3. タイプ: `セレクト`
4. オプション追加:
   - オプション1: `active`（色: 緑）
   - オプション2: `archived`（色: 灰色）

### ステップ3: データベースID取得

1. トピックマスタDBのページを開く
2. ブラウザのアドレスバーからURLをコピー
   - 形式: `https://www.notion.so/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX?v=...`
3. `?v=` の前の32文字（ハイフン含む36文字）がDatabase ID
   - 例: `abc12345-def6-78gh-ijkl-9mnopqrstuv0`
4. このIDをWF5実装時に使用（`TOPIC_MASTER_DB_ID`として設定）

---

## ✅ 作成完了チェックリスト

データベース作成後、以下を確認:

- [ ] データベース名が `トピックマスタ` である
- [ ] プロパティが全6個作成されている
  - [ ] Topic Name (title)
  - [ ] Score (number)
  - [ ] Keywords (multi_select)
  - [ ] Related Articles (relation)
  - [ ] Extracted At (date)
  - [ ] Status (select)
- [ ] Related Articles が note記事管理DB (29968d5c-2986-81ad-90d0-c24ed710503e) を指している
- [ ] 双方向リレーションが有効（note記事管理DBに `Topics` プロパティが追加されている）
- [ ] Status に `active`（緑）と `archived`（灰）のオプションが設定されている
- [ ] Database IDを取得・記録した

---

## 🔧 WF5への組み込み

### Database ID設定

WF5ワークフロー実装時に、以下の箇所でDatabase IDを使用:

**Node 8: Notion トピックマスタ更新（Loop）**
```json
{
  "parent": {
    "database_id": "{{TOPIC_MASTER_DB_ID}}"
  }
}
```

**n8nでの設定方法**:
1. n8nのワークフロー画面でHTTP Requestノードを開く
2. Body（JSON）で `{{TOPIC_MASTER_DB_ID}}` をトピックマスタのDatabase IDに置換
3. または、n8nのワークフロー変数として `TOPIC_MASTER_DB_ID` を設定

---

## 🧪 テストデータ作成（オプション）

WF5実装前に、トピックマスタDBに手動でテストデータを1件作成して動作確認可能:

| プロパティ | テスト値 |
|-----------|---------|
| Topic Name | "テスト用トピック" |
| Score | 100 |
| Keywords | ["テスト", "キーワード"] |
| Related Articles | （note記事管理DBから1件選択） |
| Extracted At | 2025-10-27 |
| Status | active |

**確認**: note記事管理DB側の選択した記事に `Topics` プロパティで「テスト用トピック」が表示されるか確認

---

## 📊 データベース構造図

```
トピックマスタDB
├── Topic Name (title): トピック名
├── Score (number): 人気度スコア
├── Keywords (multi_select): ["キーワード1", "キーワード2", ...]
├── Related Articles (relation): [記事1, 記事2, ...] → note記事管理DB
├── Extracted At (date): 2025-10-27T09:00:00.000Z
└── Status (select): active / archived

↓ Relation（双方向）

note記事管理DB
├── Title
├── URL
├── Article ID
├── ... (他のプロパティ)
└── Topics (relation): [トピック1, トピック2, ...] → トピックマスタDB
```

---

## 🔗 関連ドキュメント

- [Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md](../Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md)（Line 163-199）
- [phase2-wf5-topic-extraction-prompt.md](./prompts/phase2-wf5-topic-extraction-prompt.md)
- [Notion API: Create a database](https://developers.notion.com/reference/create-a-database)
- [Notion API: Relation property](https://developers.notion.com/reference/property-object#relation)

---

## 🚨 トラブルシューティング

### Q1: Related Articlesリレーションでnote記事管理DBが見つからない

**A**: Database IDを確認してください。note記事管理DBの正しいID: `29968d5c-2986-81ad-90d0-c24ed710503e`

### Q2: 双方向リレーションが設定できない

**A**: note記事管理DBとトピックマスタDBの両方にアクセス権限があるか確認してください。

### Q3: WF5でトピック登録時にエラーが発生する

**A**: 以下を確認:
1. Database IDが正しいか
2. Notion API Tokenに書き込み権限があるか
3. すべてのプロパティが正しく作成されているか
4. Relation設定が双方向になっているか

---

**作成者**: Claude Code
**最終更新**: 2025-10-27
