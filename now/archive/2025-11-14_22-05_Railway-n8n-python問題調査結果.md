# Railway n8n-python サービス問題調査結果

**作成日時**: 2025-11-14 22:06:15 JST
**問題**: n8n-python-production-344b.up.railway.app にアクセスできない

---

## 🚨 問題の症状

### アクセス不可
- **URL**: https://n8n-python-production-344b.up.railway.app
- **エラー**: 接続できない、または404 Not Found
- **影響範囲**: すべてのn8nワークフローWebhook（Phase4a, Phase4c等）

---

## 🔍 調査結果

### 1. Railwayログ分析

**n8n-pythonサービスのログ**:
```
🚀 Starting WF7 FFmpeg Video Renderer Server on port 5678...
INFO:     Uvicorn running on http://0.0.0.0:5678 (Press CTRL+C to quit)
```

**問題点**:
- ✅ サーバーは起動している
- ❌ **n8nではなく、FastAPIサーバー（render_server.py）が起動している**
- ❌ WebSocket接続が403 Forbiddenで拒否されている

### 2. Dockerfile確認

**プロジェクトルートのDockerfile**（正しいn8n用設定）:
```dockerfile
FROM n8nio/n8n:latest
CMD ["/usr/local/bin/node", "/usr/local/bin/n8n", "start"]
```

**使用すべきDockerfile**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/Dockerfile`

### 3. Railway設定確認

**railway.json**:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
```

**環境変数** (n8n-pythonサービス):
- ✅ DB_TYPE=postgresdb
- ✅ DB_POSTGRESDB_HOST=postgres.railway.internal
- ✅ N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
- ✅ EXECUTIONS_MODE=regular

→ **n8n用の環境変数は正しく設定されている**

### 4. 現在のRailway状態

```bash
$ railway status
Project: n8n-python
Environment: production
Service: fastapi-server  ← 注目：fastapi-serverサービスに接続
```

---

## 💡 根本原因の推定

### 可能性1: サービスの混同（最も可能性が高い）

Railwayプロジェクトには複数のサービスが存在するはずです：
1. **n8n-pythonサービス** → n8nサーバーを起動すべき
2. **fastapi-serverサービス** → FastAPIサーバーを起動

**問題**:
- n8n-pythonサービスのDockerfile設定が間違っている可能性
- または、n8n-pythonサービスが削除/無効化されている

### 可能性2: Dockerfileパスの誤設定

Railway UIでサービス設定を確認すると、以下のいずれかの問題がある可能性：
- Dockerfile.fastapiを指定している
- ビルドコンテキストが間違っている
- ビルドキャッシュが古い

### 可能性3: 複数サービスの設定ミス

本来の構成:
```
n8n-python project/
├── n8n-pythonサービス
│   ├── Dockerfile (n8n用)
│   └── URL: n8n-python-production-344b.up.railway.app
└── fastapi-serverサービス
    ├── Dockerfile.fastapi (FastAPI用)
    └── URL: fastapi-server-production-dc2b.up.railway.app
```

現在の状態:
```
n8n-python project/
└── fastapi-serverサービスのみ（n8n-pythonサービスが存在しない？）
```

---

## ✅ 推奨対応手順

### 🔴 優先度1: Railway UIで設定確認（必須）

Railway UIにアクセスして、以下を確認:
```
https://railway.app/project/<project-id>
```

**確認項目**:
1. ✅ サービス一覧に「n8n-python」サービスが存在するか
2. ✅ n8n-pythonサービスのDockerfile設定
3. ✅ n8n-pythonサービスのビルド状態（成功/失敗）
4. ✅ n8n-pythonサービスのデプロイ状態（Active/Inactive）

### 🟡 優先度2: サービス設定の修正

**n8n-pythonサービスが存在する場合**:

1. **Settings** → **Build** タブを開く
2. **Dockerfile Path** を確認:
   - 現在: `Dockerfile.fastapi` または間違ったパス
   - 修正後: `Dockerfile`
3. **Save** → **Redeploy** をクリック

**n8n-pythonサービスが存在しない場合**:

1. **New Service** をクリック
2. **Deploy from GitHub** を選択
3. リポジトリを選択（または既存のGitHub接続を使用）
4. **Settings** で以下を設定:
   - Service Name: `n8n-python`
   - Dockerfile Path: `Dockerfile`
   - Start Command: （空白、DockerfileのCMDを使用）
5. 環境変数を設定（既存のfastapi-serverから参照）:
   ```
   DB_TYPE=postgresdb
   DB_POSTGRESDB_HOST=postgres.railway.internal
   DB_POSTGRESDB_DATABASE=railway
   N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
   EXECUTIONS_MODE=regular
   ```
6. **Deploy** をクリック

### 🟢 優先度3: 既存サービスの確認と整理

**fastapi-serverサービス**:
- ✅ 正常に動作中（https://fastapi-server-production-dc2b.up.railway.app）
- ✅ Dockerfile.fastapiを使用
- ✅ Phase4b、Phase4aのエンドポイントを提供

**n8n-pythonサービス**（修正後）:
- ✅ Dockerfileを使用（n8n:latest）
- ✅ n8nサーバーを起動
- ✅ すべてのワークフローWebhookを提供

---

## 🔧 CLIでの対応（制限あり）

Railway CLIでは以下の操作が制限されています：
- ❌ サービスの切り替え（インタラクティブモードのみ）
- ❌ Dockerfile設定の変更
- ❌ 新しいサービスの作成

**可能な操作**:
- ✅ ログ確認: `railway logs --service n8n-python`
- ✅ 環境変数確認: `railway variables --service n8n-python`
- ✅ 再デプロイ: `railway up --service n8n-python`（サービスが存在する場合）

---

## 📊 次のアクション（優先順位順）

### Step 1: Railway UIにアクセス
```
https://railway.app/
→ プロジェクト「n8n-python」を開く
→ サービス一覧を確認
```

### Step 2: n8n-pythonサービスの設定確認
- Dockerfile Path: `Dockerfile`（正しいか確認）
- Build状態とログを確認
- デプロイ状態を確認

### Step 3: 修正とデプロイ
- Dockerfile Pathが間違っている場合 → 修正して Redeploy
- サービスが存在しない場合 → 新規作成
- ビルドに失敗している場合 → エラーログを確認して修正

### Step 4: 動作確認
```bash
# n8nサーバーが起動したことを確認
curl https://n8n-python-production-344b.up.railway.app/healthz

# Phase4a Webhookが動作することを確認
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2aa68d5c-2986-815c-aba4-da72d9830bf3"}'
```

---

## 🔗 関連ファイル

- **正しいDockerfile**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/Dockerfile`
- **FastAPI用Dockerfile**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/Dockerfile.fastapi`
- **Railway設定**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/data/railway.json`
- **調査ログ**: `/tmp/phase4a-test-result.log`

---

## 🎯 期待される最終状態

### サービス構成
```
Railway Project: n8n-python
├── Service: n8n-python
│   ├── Dockerfile: Dockerfile (n8n:latest)
│   ├── URL: n8n-python-production-344b.up.railway.app
│   ├── Port: 5678
│   └── 役割: n8nサーバー、すべてのワークフローWebhook
│
└── Service: fastapi-server
    ├── Dockerfile: Dockerfile.fastapi
    ├── URL: fastapi-server-production-dc2b.up.railway.app
    ├── Port: 8080
    └── 役割: スライド生成、動画生成エンドポイント
```

### 動作確認
- ✅ n8n UI: https://n8n-python-production-344b.up.railway.app/
- ✅ Phase4a Webhook: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator`
- ✅ Phase4c Webhook: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-video-concatenator`
- ✅ FastAPI /health: `https://fastapi-server-production-dc2b.up.railway.app/health`

---

**結論**: Railway UIで直接サービス設定を確認・修正する必要があります。CLIだけでは根本的な修正はできません。
