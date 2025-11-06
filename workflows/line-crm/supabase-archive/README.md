# LINE CRM - Supabase版（アーカイブ）

**ステータス**: 🗄️ **アーカイブ済み** - 学習・参考用  
**移行日**: 2025-10-26  
**移行先**: [Notion版](../README.md)  
**理由**: Notionの方がCRM管理に適しているため

---

## 📋 概要

このディレクトリには、LINE友だち追加イベントをSupabase PostgreSQLに保存するワークフローのアーカイブが含まれています。

**主な機能:**
- LINE Webhookでfollowイベントを受信
- データ検証・変換処理
- Supabase `line_leads`テーブルへの自動挿入
- エラーハンドリング

---

## 🗂️ ファイル構成

```
supabase-archive/
├── README.md              # このファイル
├── schema.sql             # line_leadsテーブルのスキーマ定義
├── workflow.json          # n8nワークフロー定義
├── setup-guide.md         # セットアップガイド
└── migration-notes.md     # Notion移行の学びと理由
```

---

## 🔄 Notion版への移行理由

### Supabase版の課題
1. **RLS（Row Level Security）設定の複雑さ**
   - n8nからのアクセス制御が煩雑
   - サービスロールキーの管理が必要

2. **データベーススキーマ管理**
   - マイグレーション管理が必要
   - スキーマ変更時の慎重な対応が必要

3. **CRM機能の不足**
   - ビュー機能が限定的
   - フィルタリング・ソート機能をSQL で実装が必要
   - UIでの直感的なデータ管理が困難

### Notion版の利点
1. **直感的なUI**
   - ドラッグ&ドロップでステータス変更
   - 複数のビュー（ボード、テーブル、カレンダー）
   - リアルタイムでのデータ確認

2. **柔軟なデータ管理**
   - プロパティの追加・変更が簡単
   - リレーション機能
   - テンプレート機能

3. **コラボレーション機能**
   - チーム共有が容易
   - コメント機能
   - 変更履歴の追跡

4. **n8n統合の容易さ**
   - 公式Notionノード
   - APIキーのみで接続可能
   - RLS設定不要

---

## 📊 テーブルスキーマ

### `line_leads` テーブル

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| `id` | BIGINT | PRIMARY KEY, AUTO INCREMENT | 主キー |
| `lead_id` | VARCHAR | UNIQUE, NOT NULL | n8n実行ID + タイムスタンプのユニークキー |
| `user_id` | VARCHAR | NOT NULL | LINE ユーザーID |
| `display_name` | VARCHAR | DEFAULT '' | LINE表示名 |
| `picture_url` | TEXT | DEFAULT '' | LINEプロフィール画像URL |
| `timestamp_jst` | TIMESTAMPTZ | NOT NULL | イベント発生時刻（JST） |
| `processed_at` | TIMESTAMPTZ | NOT NULL | n8n処理時刻（JST） |
| `source` | VARCHAR | DEFAULT 'webhook' | データソース |
| `status` | VARCHAR | DEFAULT 'pending' | ステータス |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | レコード作成日時 |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | レコード更新日時 |
| `deleted_at` | TIMESTAMPTZ | NULLABLE | 論理削除日時 |

詳細は [`schema.sql`](./schema.sql) を参照してください。

---

## 🚀 ワークフロー構成

### ノード構成

1. **LINE Webhook Trigger**
   - LINE Platformからのイベント受信
   - Path: `line-lead`

2. **Data Validation & Transform**
   - LINE検証リクエストの検出とスキップ
   - followイベントのみ処理
   - lead_id生成（n8n実行ID + タイムスタンプ）

3. **Supabase Insert**
   - PostgreSQL INSERT操作
   - テーブル: `line_leads`

4. **Success Log**
   - 成功ログの記録

5. **Error Handler**
   - エラーハンドリング

詳細は [`workflow.json`](./workflow.json) と [`setup-guide.md`](./setup-guide.md) を参照してください。

---

## 💾 バックアップデータ

移行時のデータバックアップ（17件）は以下に保存されています：

**Obsidianローカル:**
```
/Users/yuichiroooosuger/Desktop/2rd_brain/Projects/LINE_CRM_line_leads_backup.json
```

---

## 📚 学びと推奨事項

詳細は [`migration-notes.md`](./migration-notes.md) を参照してください。

### 主な学び

1. **データベース選択の重要性**
   - CRM用途ではNotionの方が適している
   - Supabaseは大規模データ処理に最適

2. **n8n統合の考慮点**
   - 認証情報の管理
   - エラーハンドリング
   - ログ記録

3. **スキーマ設計**
   - ユニークキーの設計
   - タイムスタンプ管理
   - ソフトデリート実装

---

## 🔗 関連リンク

- [LINE CRM Notion版](../README.md)
- [n8nワークフローリポジトリ](https://github.com/plus61/n8n-workflows)
- [Supabase公式ドキュメント](https://supabase.com/docs)
- [n8n PostgreSQLノード](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.postgres/)

---

## ⚠️ 注意事項

このアーカイブは**参考・学習用**です。実際の運用には[Notion版](../README.md)を使用してください。

---

**アーカイブ日**: 2025-10-26  
**最終動作確認**: 2025-10-25  
**データ削除日**: 2025-10-26

