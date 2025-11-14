# Railway FastAPI Deployment Issue

**作成日時**: 2025-11-14 12:29:55 JST

## 問題概要

FastAPIサービス（fastapi-server）のデプロイが完了せず、ヘルスチェックエンドポイントが404エラーを返す。

## 現在の状況

### ✅ 成功している項目
1. **サービス作成**: fastapi-serverサービスが存在
   - Service ID: `574b0f3b-43a8-42eb-bdb6-d00061b63156`
   - Service Name: `fastapi-server`

2. **ドメイン取得**: 公開URLが割り当て済み
   - URL: `https://fastapi-server-production-dc2b.up.railway.app`

3. **設定ファイル読み込み**: railway.tomlが正しく認識されている
   ```json
   "configFile": "railway.toml",
   "dockerfilePath": "Dockerfile.fastapi"
   ```

4. **デプロイメント作成**: 最新デプロイメントID
   - ID: `65fe8af2-6489-40ca-b9fd-893efe41a6fd`
   - Reason: "deploy"
   - Runtime: "V2"

### ❌ 失敗している項目

1. **ヘルスチェック404エラー**:
   ```bash
   $ curl https://fastapi-server-production-dc2b.up.railway.app/health
   {"status":"error","code":404,"message":"Application not found"}
   ```

2. **ログアクセス不可**:
   ```bash
   $ railway logs -s fastapi-server
   No deployments found
   ```

3. **デプロイメントID認識失敗**:
   ```bash
   $ railway logs --deployment 65fe8af2-6489-40ca-b9fd-893efe41a6fd
   Deployment id does not exist
   ```

## 根本原因分析

### JSONステータスから判明した問題

`railway status --json`の出力から、**GitHubリポジトリが接続されていない**ことが判明：

```json
"source": {
  "repo": null,
  "image": null
}
```

**比較**: n8n-pythonサービス（正常動作中）:
```json
"source": {
  "repo": "plus61/n8n-workflows",
  "image": null
}
```

### 試行した解決策

| 試行 | コマンド | 結果 |
|------|----------|------|
| 1 | `railway up` (1回目) | Build logs URLのみ生成、デプロイ未完了 |
| 2 | `railway up` (2回目) | 同上 |
| 3 | Git push (commit 5cfecc5) | GitHubリポジトリ未接続のため効果なし |
| 4 | `railway up --service fastapi-server` | "Indexing... Uploading..." 表示、ローカルファイルアップロード |
| 5 | 60秒待機後ヘルスチェック | まだ404 |
| 6 | 120秒追加待機後ヘルスチェック | まだ404 |

## 技術的詳細

### railway.toml設定（確認済み）

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile.fastapi"

[deploy]
startCommand = "python3 /app/render_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Dockerfile.fastapi（確認済み）

- Base Image: `python:3.11-slim`
- ffmpeg, libmagic1, curl インストール済み
- FastAPI依存関係インストール済み
- ヘルスチェック実装: `CMD curl -f http://localhost:8000/health`
- ENTRYPOINT: `["python3", "/app/render_server.py"]`

### render_server.py（確認済み）

- `/health` エンドポイント実装済み:
  ```python
  @app.get("/health")
  async def health():
      return {"status": "healthy", "service": "wf7-ffmpeg-renderer"}
  ```

- `/generate-single-video` エンドポイント実装済み（Phase4b用）

## 次のステップ

### ✅ 推奨アプローチ: Railway UIでGitHubリポジトリを接続

Railway CLIではGitHubリポジトリの接続を設定できないため、**Railway UIで手動設定が必要**：

1. **Railway UIにアクセス**:
   - Project: n8n-python
   - Service: fastapi-server
   - URL構成: `https://railway.app/project/75226584-188f-4dc9-8032-1bc2a3e7260b/service/574b0f3b-43a8-42eb-bdb6-d00061b63156`

2. **GitHubリポジトリを接続**:
   - Service Settings → Connect Repo
   - Repository: `plus61/n8n-workflows`
   - Branch: `project`

3. **自動デプロイを確認**:
   - GitHub接続後、自動的にデプロイがトリガーされる
   - railway.tomlが自動的に適用される

4. **ヘルスチェック確認**:
   ```bash
   curl https://fastapi-server-production-dc2b.up.railway.app/health
   # Expected: {"status": "healthy", "service": "wf7-ffmpeg-renderer"}
   ```

### 🔄 代替アプローチ: ローカルデプロイを継続

`railway up --service fastapi-server`で最新のデプロイメントが作成されたため、追加で待機すれば成功する可能性もあります。

**ただし、GitHubリポジトリ接続なしでは**:
- ❌ 自動デプロイが機能しない
- ❌ Git pushでの更新が反映されない
- ❌ 継続的インテグレーションが困難

## 関連ファイル

- railway.toml: `/Users/yuichiroooosuger/Desktop/n8n-workflows/railway.toml`
- Dockerfile.fastapi: `/Users/yuichiroooosuger/Desktop/n8n-workflows/Dockerfile.fastapi`
- render_server.py: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/render_server.py`
- 設計書: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-01-14_11-45_Phase4b-FastAPI-Endpoint-Design.md`

## 影響を受けるタスク

### ブロックされているタスク

1. **Phase4bワークフロー修正**（Task 10）
   - HTTP RequestノードでFastAPI呼び出し
   - Target URL: `https://fastapi-server-production-dc2b.up.railway.app/generate-single-video`
   - **ブロック理由**: FastAPIサービスが404を返す

2. **Phase4b単体テスト実行**（Task 11）
   - テストペイロード準備済み
   - **ブロック理由**: ワークフロー修正が未完了

3. **Phase4a→Phase4b→Phase4c完全E2Eテスト**（Task 12）
   - テストペイロード: `{"script_id": "2aa68d5c-2986-81b0-b488-e2d7ee8026b7"}`
   - **ブロック理由**: Phase4bが未完了

## まとめ

FastAPIサービスの構成ファイルとコードはすべて正しく準備されていますが、**Railway CLIの制限により、GitHubリポジトリ接続は手動で行う必要があります**。

Railway UIでGitHub接続を完了すれば、すべての設定が自動的に適用され、デプロイが成功するはずです。
