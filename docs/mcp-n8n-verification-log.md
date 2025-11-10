# n8n MCP 動作確認ログ

**目的**: MCPの動作状態を記録し、問題発生時の原因特定を支援

---

## 📅 動作確認記録

### 2025-11-09 03:41:15 UTC

#### 確認項目

- [x] **ヘルスチェック**: ✅ 成功
  - Status: `ok`
  - API URL: `https://n8n-python-production-344b.up.railway.app`
  - レスポンス時間: 637ms
  - MCP Version: 2.22.6

- [x] **詳細診断**: ✅ 成功
  - API接続状態: `connected: true`
  - 設定状態: `configured: true`
  - 利用可能ツール数: 38個
  - 管理ツール: 有効

- [x] **ワークフロー一覧取得**: ✅ 成功
  - 取得件数: 5件
  - サンプルID: `4Oo5LL3KMKVn8gUJ`

- [x] **ワークフロー取得**: ✅ 成功
  - ワークフローID: `4Oo5LL3KMKVn8gUJ`
  - ワークフロー名: `WF7 Phase3: 音声・字幕生成(オプション)`
  - ステータス: `active: true`

#### 環境情報

- **Node.js**: v24.1.0
- **プラットフォーム**: darwin (macOS)
- **npxパス**: `/opt/homebrew/bin/npx`
- **設定ファイル**: `.mcp/config.json`
- **n8n-mcp設定バージョン**: 2.22.11
- **実行バージョン**: 2.22.6

#### 環境変数

- **N8N_API_URL**: ✅ 設定済み
- **N8N_API_KEY**: ✅ 設定済み（先頭: `eyJhbGciOiJIUzI1NiIs`）

#### 動作確認コマンド

```javascript
// 1. ヘルスチェック
mcp_n8n-mcp_n8n_health_check()
// 結果: ✅ 成功

// 2. 詳細診断
mcp_n8n-mcp_n8n_diagnostic({verbose: true})
// 結果: ✅ 成功

// 3. ワークフロー一覧
mcp_n8n-mcp_n8n_list_workflows({limit: 5})
// 結果: ✅ 成功（5件取得）

// 4. ワークフロー取得
mcp_n8n-mcp_n8n_get_workflow_minimal({id: "4Oo5LL3KMKVn8gUJ"})
// 結果: ✅ 成功
```

#### 確認結果サマリー

| 項目 | 状態 | 詳細 |
|------|------|------|
| MCPサーバー起動 | ✅ | 正常 |
| API接続 | ✅ | 接続成功 |
| ワークフロー取得 | ✅ | 正常 |
| ツール利用 | ✅ | 38個利用可能 |
| 設定ファイル | ✅ | 正しく読み込まれている |
| 環境変数 | ✅ | 設定済み |

---

## 🔍 問題発生時の記録テンプレート

### 問題発生日時
- **日時**: YYYY-MM-DD HH:MM:SS UTC
- **症状**: 
- **エラーメッセージ**: 

### 確認項目

- [ ] **ヘルスチェック**: 
  - Status: 
  - エラー: 

- [ ] **詳細診断**: 
  - API接続状態: 
  - エラー: 

- [ ] **設定ファイル**: 
  - 存在: 
  - パス: 
  - JSON形式: 

- [ ] **環境変数**: 
  - N8N_API_URL: 
  - N8N_API_KEY: 

- [ ] **npx/npm**: 
  - npxパス: 
  - Node.jsバージョン: 

### 実施した対策

1. 
2. 
3. 

### 解決結果

- [ ] ✅ 解決
- [ ] ❌ 未解決
- [ ] ⚠️ 部分解決

### 備考

---

## 📝 定期的な動作確認

### 推奨頻度
- **毎日**: ヘルスチェックのみ
- **週1回**: 詳細診断
- **月1回**: 全項目確認

### 確認コマンド

```javascript
// 毎日の確認（30秒）
mcp_n8n-mcp_n8n_health_check()

// 週1回の確認（1分）
mcp_n8n-mcp_n8n_diagnostic({verbose: true})
mcp_n8n-mcp_n8n_list_workflows({limit: 1})

// 月1回の確認（5分）
// 上記すべて + ワークフロー操作のテスト
```

---

**最終更新**: 2025-11-09  
**次回確認予定**: 2025-11-10

