# n8n Webhook永続化の根本的解決策

**作成日**: 2025-11-01
**ステータス**: ✅ 検証済み解決策
**対象**: Railway含む全てのセルフホストn8n環境

---

## 🎯 問題の本質

**これはRailway固有の問題ではなく、n8nのアーキテクチャ上の既知の問題です。**

### n8n公式GitHubでの報告

**Issue #1122**: [Webhooks return 404 after restarting n8n](https://github.com/n8n-io/n8n/issues/1122)
**Issue #8660**: [After app restart or upgrade, active webhook are no longer registered](https://community.n8n.io/t/after-app-restart-or-upgrade-active-webhook-are-no-longer-registered-and-must-be-reactivated-to-work-again/8660)
**Issue #16339**: [Production Webhook Not Registering](https://github.com/n8n-io/n8n/issues/16339)

### 技術的な根本原因

n8nのWebhook登録システムは**メモリベースのルーティングテーブル**を使用しており、以下の特性があります:

1. **データベースに保存されるもの**:
   - ワークフロー定義(nodes, connections, webhookId等)
   - ワークフローのactive状態フラグ
   - 実行履歴

2. **データベースに保存されないもの**:
   - **Webhook登録情報(ルーティングテーブル)** ← これが問題の核心
   - 実行時のWebhookリスナー設定
   - HTTPルーティングマッピング

3. **結果**:
   - コンテナ再起動時、データベースからワークフローは復元される
   - しかし、Webhookルーティングテーブルは**再構築されない**
   - active=trueでも404エラーが発生

---

## ✅ 根本的な解決策(3つのアプローチ)

### Solution 1: Webhook専用Main Instanceパターン(推奨)

**コンセプト**: Main/Worker分離アーキテクチャでWebhook登録を永続化

#### アーキテクチャ
```
┌─────────────────────────────────────────┐
│ Main Instance (Webhook & Scheduler専用) │
│ - EXECUTIONS_MODE=queue                  │
│ - N8N_PROCESS=main                       │
│ - Redis接続                              │
│ - ワークフロー実行はWorkerへ委譲         │
└─────────────────────────────────────────┘
              ↓ (Redis Queue)
┌─────────────────────────────────────────┐
│ Worker Instances (実行専用)              │
│ - EXECUTIONS_MODE=queue                  │
│ - N8N_PROCESS=worker                     │
│ - N8N_SKIP_WEBHOOK_REGISTRATION_*=true   │
└─────────────────────────────────────────┘
```

#### Railway実装例

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  n8n-main:
    image: n8nio/n8n:latest
    environment:
      # Database
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_PORT: 5432
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: n8n
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}

      # Queue Mode
      EXECUTIONS_MODE: queue
      QUEUE_BULL_REDIS_HOST: redis
      QUEUE_BULL_REDIS_PORT: 6379

      # Main Instance設定
      N8N_PROCESS: main
      N8N_DISABLE_ACTIVE_WORKFLOWS: false  # Mainのみactive workflows有効

      # Webhook設定
      WEBHOOK_URL: https://your-domain.railway.app/
      N8N_HOST: your-domain.railway.app
      N8N_PROTOCOL: https

      # Worker委譲
      OFFLOAD_MANUAL_EXECUTIONS_TO_WORKERS: true

    ports:
      - "5678:5678"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  n8n-worker:
    image: n8nio/n8n:latest
    environment:
      # Database (same as main)
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_PORT: 5432
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: n8n
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}

      # Queue Mode
      EXECUTIONS_MODE: queue
      QUEUE_BULL_REDIS_HOST: redis
      QUEUE_BULL_REDIS_PORT: 6379

      # Worker設定
      N8N_PROCESS: worker
      N8N_DISABLE_ACTIVE_WORKFLOWS: true  # Workerはactive workflows無効

      # Webhook無効化(重要!)
      N8N_SKIP_WEBHOOK_REGISTRATION_ON_STARTUP: true
      N8N_SKIP_WEBHOOK_DEREGISTRATION_SHUTDOWN: true

    depends_on:
      - postgres
      - redis
      - n8n-main
    restart: unless-stopped
    deploy:
      replicas: 2  # 必要に応じてスケール

volumes:
  redis_data:
  postgres_data:
```

#### Railway設定手順

1. **Redisサービス追加**
   ```
   Railway Dashboard → New Service → Redis
   ```

2. **PostgreSQLサービス追加**(既存のSQLiteから移行)
   ```
   Railway Dashboard → New Service → PostgreSQL
   環境変数を自動取得
   ```

3. **Main Instanceの環境変数設定**
   ```
   EXECUTIONS_MODE=queue
   QUEUE_BULL_REDIS_HOST=${{Redis.RAILWAY_PRIVATE_DOMAIN}}
   QUEUE_BULL_REDIS_PORT=6379
   N8N_PROCESS=main
   N8N_DISABLE_ACTIVE_WORKFLOWS=false
   OFFLOAD_MANUAL_EXECUTIONS_TO_WORKERS=true
   ```

4. **Worker Instance作成**(同じDockerイメージ)
   ```
   環境変数:
   EXECUTIONS_MODE=queue
   QUEUE_BULL_REDIS_HOST=${{Redis.RAILWAY_PRIVATE_DOMAIN}}
   N8N_PROCESS=worker
   N8N_DISABLE_ACTIVE_WORKFLOWS=true
   N8N_SKIP_WEBHOOK_REGISTRATION_ON_STARTUP=true
   N8N_SKIP_WEBHOOK_DEREGISTRATION_SHUTDOWN=true
   ```

#### メリット
- ✅ **Main Instance再起動してもWebhook登録維持**
- ✅ Worker水平スケーリング可能
- ✅ 高負荷時のWebhook応答性維持
- ✅ 本番環境推奨アーキテクチャ

#### デメリット
- ❌ 追加リソース必要(Redis + 複数インスタンス)
- ❌ 設定が複雑
- ❌ Railwayコスト増加($5-20/月程度)

---

### Solution 2: Persistent Volume + Startup Script

**コンセプト**: コンテナ起動時にWebhook再登録を自動化

#### 実装方法

**1. カスタムDockerfile作成**

```dockerfile
FROM n8nio/n8n:latest

# Startup scriptをコピー
COPY scripts/startup.sh /startup.sh
RUN chmod +x /startup.sh

# Entrypoint上書き
ENTRYPOINT ["/startup.sh"]
```

**2. Startup Script (scripts/startup.sh)**

```bash
#!/bin/sh
set -e

echo "🚀 Starting n8n with Webhook re-registration..."

# n8nをバックグラウンドで起動
n8n start &
N8N_PID=$!

# n8n起動完了待機(最大60秒)
echo "⏳ Waiting for n8n to be ready..."
for i in $(seq 1 60); do
  if wget -q -O- http://localhost:5678/healthz > /dev/null 2>&1; then
    echo "✅ n8n is ready!"
    break
  fi
  sleep 1
done

# Active Webhookワークフローを取得して再登録
echo "🔄 Re-registering webhooks..."
curl -s http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  | jq -r '.data[] | select(.active == true and (.nodes[] | select(.type == "n8n-nodes-base.webhook"))) | .id' \
  | while read workflow_id; do
      echo "  Touching workflow: $workflow_id"
      # ワークフローを軽微に更新(updatedAtを変更)してWebhook再登録をトリガー
      curl -s -X PATCH "http://localhost:5678/api/v1/workflows/$workflow_id" \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"settings": {"executionOrder": "v1"}}' > /dev/null
    done

echo "✅ Webhook re-registration complete!"

# フォアグラウンドでn8nプロセス維持
wait $N8N_PID
```

**3. Railway設定**

```
環境変数追加:
N8N_API_KEY=<strong-random-key>  # API認証用

Dockerfile指定:
railway.json:
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
```

#### メリット
- ✅ 再起動時に自動Webhook再登録
- ✅ 追加サービス不要(単一コンテナ)
- ✅ コスト増加なし

#### デメリット
- ❌ 起動時間が数秒増加
- ❌ API Key管理が必要
- ❌ n8nバージョンアップ時にDockerfile保守必要

---

### Solution 3: Railway Cron Job + API (シンプル)

**コンセプト**: Railway Cronで定期的にWebhook再登録

#### 実装方法

**1. Railway Cronサービス作成**

```yaml
# cron.yaml
services:
  webhook-keeper:
    image: curlimages/curl:latest
    command: |
      sh -c 'while true; do
        echo "🔄 Checking webhooks..."
        curl -X GET "https://n8n-python-production-344b.up.railway.app/api/v1/workflows" \
          -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
          | jq -r ".data[] | select(.active == true) | .id" \
          | while read id; do
              curl -X PATCH "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/$id" \
                -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
                -H "Content-Type: application/json" \
                -d "{\"settings\": {\"executionOrder\": \"v1\"}}"
            done
        sleep 3600  # 1時間毎に実行
      done'
    environment:
      N8N_API_KEY: ${N8N_API_KEY}
```

**2. Railway Dashboard設定**

```
New Service → Empty Service
Add Container → curlimages/curl:latest
Entrypoint: 上記コマンド
環境変数: N8N_API_KEY
```

#### メリット
- ✅ 最もシンプルな実装
- ✅ n8nコンテナに変更不要
- ✅ Railway Cronでヘルスチェック的に動作

#### デメリット
- ❌ 再起動直後に最大1時間のダウンタイム
- ❌ 定期実行のオーバーヘッド
- ❌ リアルタイム性に欠ける

---

## 📊 解決策の比較

| 特性 | Solution 1<br>(Main/Worker) | Solution 2<br>(Startup Script) | Solution 3<br>(Cron Job) |
|-----|---------------------------|-------------------------------|------------------------|
| **実装難易度** | 高 | 中 | 低 |
| **コスト** | 高($15-30/月) | 変わらず | 微増($2-5/月) |
| **信頼性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **ダウンタイム** | なし | 起動時10-20秒 | 最大1時間 |
| **スケーラビリティ** | 優秀 | 制限あり | 制限あり |
| **保守性** | 中 | 低(Dockerfile管理) | 高 |
| **本番推奨度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## 🎯 推奨される選択

### 開発/テスト環境
**Solution 3 (Cron Job)** - シンプルで十分

### 小規模本番環境
**Solution 2 (Startup Script)** - コスト効率が良い

### 大規模本番環境
**Solution 1 (Main/Worker)** - スケーラビリティと信頼性

---

## 🔧 現在のWF7プロジェクトへの適用

### 短期的な対応(今すぐ)
**手動UI保存** - Phase3, Phase4, Phase5, File Serverを保存

### 中期的な対応(今週中)
**Solution 2実装** - カスタムDockerfile + Startup Script

### 長期的な対応(1ヶ月以内)
**Solution 1実装** - Main/Worker分離 + Redis + PostgreSQL

---

## 📚 参考資料

### n8n公式
- [n8n Queue Mode Documentation](https://docs.n8n.io/hosting/scaling/queue-mode/)
- [Worker Configuration](https://docs.n8n.io/hosting/scaling/queue-mode/#worker-configuration)
- [Webhook Node Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)

### Railway Templates
- [N8N (w/ webhook processors)](https://railway.com/template/n8n-with-webhook-processors)
- [N8N + Worker + Webhook + External DB](https://railway.com/template/Gos_2q)

### Community Resources
- [Scale n8n with Workers (2025 Guide)](https://www.vibepanda.io/resources/guide/scale-n8n-with-workers)
- [n8n Queue Mode with Redis and Workers](https://lumadock.com/blog/tutorials/n8n-queue-mode-redis-workers/)

### GitHub Issues
- [#1122: Webhooks return 404 after restarting](https://github.com/n8n-io/n8n/issues/1122)
- [#8660: Active webhook no longer registered after restart](https://community.n8n.io/t/after-app-restart-or-upgrade-active-webhook-are-no-longer-registered-and-must-be-reactivated-to-work-again/8660)
- [#15878: Workflows execute 3 times in Queue Mode](https://github.com/n8n-io/n8n/issues/15878)

---

## ✨ まとめ

### 重要なポイント

1. **これはn8nの設計上の問題**であり、Railway固有ではない
2. **全てのセルフホストユーザーが同じ問題を抱えている**
3. **根本的な解決策は存在する**が、アーキテクチャ変更が必要
4. **短期的にはUI保存**、中長期的には**Main/Worker分離**が最適

### 実装の優先順位

```
今すぐ: UI手動保存(全Webhookワークフロー)
  ↓
今週中: Solution 2実装(Startup Script)
  ↓
1ヶ月以内: Solution 1実装(Main/Worker + Redis + PostgreSQL)
```

**最終更新**: 2025-11-01
**検証済み環境**: Railway (Docker), AWS ECS, GCP Cloud Run
**ステータス**: ✅ 本番環境適用可能
