# Contains Studio Agents - n8nプロジェクト活用ガイド（完全版）

**作成日時**: 2025-11-15 08:49:26 JST
**対象プロジェクト**: n8n-workflows（WF7 SNS動画自動生成パイプライン）
**バージョン**: 1.0
**Contains Studio Agents**: 37エージェント（8部門）

---

## 📋 目次

1. [概要](#概要)
2. [n8nプロジェクトに最適なエージェント Top 10](#n8nプロジェクトに最適なエージェント-top-10)
3. [エージェント詳細ガイド](#エージェント詳細ガイド)
4. [実践的ユースケース](#実践的ユースケース)
5. [ワークフローとエージェントのマッピング](#ワークフローとエージェントのマッピング)
6. [ベストプラクティス](#ベストプラクティス)
7. [トラブルシューティング](#トラブルシューティング)

---

## 概要

### Contains Studio Agentsとは

- **グローバルインストール**: `~/.claude/agents/` に配置
- **自動トリガー機能**: タスク説明だけで適切なエージェントが起動
- **専門性**: 40+の専門エージェントが8部門に分類
- **併用可能**: SuperClaudeペルソナシステムと同時使用可能

### インストール確認

```bash
# インストール状況確認
ls -la ~/.claude/agents/

# エージェント数確認
find ~/.claude/agents -name "*.md" -type f | wc -l
# 期待値: 37
```

### 基本的な使い方

#### 自動トリガー（推奨）
```
「WF7のPhase4b動画生成エンドポイントを最適化して」
→ performance-benchmarker または backend-architect が自動起動
```

#### 明示的呼び出し
```
「@rapid-prototyper で新しいPhase5ワークフローのプロトタイプを作成」
→ rapid-prototyper が起動
```

---

## n8nプロジェクトに最適なエージェント Top 10

| # | エージェント名 | 用途 | 優先度 | 部門 |
|---|--------------|------|--------|------|
| 1 | `workflow-optimizer` | n8nワークフロー効率化、ボトルネック分析 | ⭐⭐⭐⭐⭐ | testing |
| 2 | `api-tester` | Webhook・APIテスト、負荷テスト | ⭐⭐⭐⭐⭐ | testing |
| 3 | `backend-architect` | FastAPIエンドポイント設計、DB最適化 | ⭐⭐⭐⭐⭐ | engineering |
| 4 | `devops-automator` | Railway CI/CD、Docker最適化 | ⭐⭐⭐⭐⭐ | engineering |
| 5 | `rapid-prototyper` | 新フェーズのプロトタイプ作成 | ⭐⭐⭐⭐ | engineering |
| 6 | `test-writer-fixer` | テストスクリプト作成・修正 | ⭐⭐⭐⭐ | engineering |
| 7 | `performance-benchmarker` | Phase4パイプライン性能測定 | ⭐⭐⭐⭐ | testing |
| 8 | `experiment-tracker` | WF7改善実験の追跡 | ⭐⭐⭐ | project-management |
| 9 | `project-shipper` | Phase5デプロイ管理 | ⭐⭐⭐ | project-management |
| 10 | `tool-evaluator` | MCP/外部ツール評価 | ⭐⭐⭐ | testing |

---

## エージェント詳細ガイド

### 1. workflow-optimizer 🔧⚡

**専門分野**: n8nワークフロー効率化、ボトルネック分析、人間-AI協働

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「Phase4a→4b→4cのパイプライン処理時間を短縮したい」
→ workflow-optimizer が自動起動
```

##### 明示的呼び出し例
```
「@workflow-optimizer でWF7全体のボトルネックを分析して」
```

#### 具体的な活用シナリオ

**シナリオ1: Phase4パイプライン最適化**
```
タスク: 「WF7 Phase4a→4b→4cの処理時間（現在49秒）を30秒以下に短縮」

workflow-optimizerの分析内容:
1. 各フェーズの処理時間計測
   - Phase4a: 7スライド生成（~15秒）
   - Phase4b: 7動画生成（~28秒、各4秒）
   - Phase4c: 動画結合（~23秒）

2. ボトルネック特定
   - Phase4b: 7回のシリアル処理（28秒）
   - Phase4c: FAL API待機時間（~20秒）

3. 最適化提案
   - Phase4bの並列化（7回→3回バッチ、推定15秒）
   - Phase4c: FAL API polling間隔短縮（10秒→5秒）
   - 予想改善: 49秒 → 28秒（43%削減）

4. 実装ステップ
   - n8nワークフロー: Split In Batches node追加
   - FastAPI: バッチ処理エンドポイント追加
   - テスト: 統合テストスクリプト更新
```

**シナリオ2: Webhook応答時間改善**
```
タスク: 「Phase4a webhookの応答時間を改善したい」

workflow-optimizerの分析:
1. 現在のフロー
   - Webhook受信 → Notion API → スライド生成 → Phase4b呼び出し
   - 同期処理: ~15秒（ユーザー待機時間）

2. 改善提案
   - 非同期処理化: Webhook即座応答（200ms以下）
   - バックグラウンド処理: Queue + Worker pattern
   - 進捗通知: Webhook callback or polling endpoint

3. 実装アプローチ
   - n8n: Execute Workflow node（async mode）
   - FastAPI: Celery + Redis導入
   - 通知: LINE/Slack webhook統合
```

#### 実行コマンド例
```bash
# ワークフロー実行時間計測
time ./test-phase4a-phase4b-integration.sh

# ボトルネック分析
@workflow-optimizer で以下を実行:
- n8n execution logs分析
- 各nodeの処理時間抽出
- 並列化可能部分の特定
```

---

### 2. api-tester 🧪📊

**専門分野**: Webhook/API負荷テスト、パフォーマンス測定、契約テスト

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「Phase4a webhookが1000リクエスト/分に耐えられるかテストして」
→ api-tester が自動起動
```

##### 明示的呼び出し例
```
「@api-tester でFastAPI /generate-single-video エンドポイントの負荷テストを実行」
```

#### 具体的な活用シナリオ

**シナリオ1: Phase4a Webhook負荷テスト**
```bash
タスク: 「Phase4a webhookがバイラル時（100同時リクエスト）に対応できるか検証」

api-testerの実行:
1. テスト設計
   - シナリオ: 100ユーザーが同時にスライド生成リクエスト
   - 期待値: すべて60秒以内に完了、エラー率<1%
   - ツール: k6 または Apache JMeter

2. テストスクリプト生成
   ```javascript
   // k6-load-test-phase4a.js
   import http from 'k6/http';
   import { check, sleep } from 'k6';

   export let options = {
     stages: [
       { duration: '30s', target: 20 },  // Ramp-up
       { duration: '1m', target: 100 },  // Peak load
       { duration: '30s', target: 0 },   // Ramp-down
     ],
     thresholds: {
       http_req_duration: ['p(95)<60000'], // 95% < 60s
       http_req_failed: ['rate<0.01'],     // Error rate < 1%
     },
   };

   export default function () {
     const payload = JSON.stringify({
       notion_page_id: '2aa68d5c-2986-815c-aba4-da72d9830bf3'
     });

     const params = {
       headers: {
         'Content-Type': 'application/json',
       },
     };

     let res = http.post(
       'https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator',
       payload,
       params
     );

     check(res, {
       'status is 200': (r) => r.status === 200,
       'response time < 60s': (r) => r.timings.duration < 60000,
     });

     sleep(1);
   }
   ```

3. テスト実行
   ```bash
   k6 run k6-load-test-phase4a.js
   ```

4. 結果分析
   - 平均応答時間: 18.5秒
   - p95応答時間: 52秒
   - p99応答時間: 58秒
   - エラー率: 0.5%
   - ボトルネック: Notion API rate limiting（3 req/s）

5. 改善提案
   - Notion API呼び出しキャッシュ（15分TTL）
   - Rate limiter実装（client-side）
   - Queue system導入（Redis + Bull）
```

**シナリオ2: FastAPI エンドポイント性能テスト**
```bash
タスク: 「/generate-single-video エンドポイントの性能ベンチマーク」

api-testerの分析:
1. 性能ターゲット
   - 応答時間: p95 < 10秒（duration=7sの場合）
   - スループット: > 5 RPS（同時処理）
   - エラー率: < 0.1%

2. テスト実行
   ```bash
   # Apache Bench
   ab -n 100 -c 10 \
      -p payload.json \
      -T application/json \
      https://fastapi-server-production-dc2b.up.railway.app/generate-single-video

   # payload.json
   {
     "section": "hook",
     "duration": 7,
     "image_url": "https://res.cloudinary.com/.../test.png",
     "motion_prompt": "subtle zoom",
     "text": "テスト",
     "script_id": "test-001"
   }
   ```

3. 結果
   - 平均応答時間: 8.2秒
   - p95: 9.5秒 ✅
   - p99: 11.2秒 ⚠️
   - スループット: 1.2 RPS ❌（ターゲット5 RPS未達）

4. ボトルネック特定
   - FFmpeg処理: CPU bound（シングルスレッド）
   - 画像ダウンロード: ネットワークI/O
   - Base64エンコード: メモリコピー

5. 最適化提案
   - FFmpeg並列処理: 複数workerプロセス
   - 画像キャッシュ: Redis（同一画像の再利用）
   - レスポンス最適化: streaming response
```

#### 実行コマンド例
```bash
# Webhook負荷テスト
k6 run --vus 100 --duration 2m k6-phase4a-load-test.js

# API性能テスト
ab -n 1000 -c 50 -p payload.json -T application/json \
   https://fastapi-server-production-dc2b.up.railway.app/generate-single-video

# 契約テスト（OpenAPI validation）
dredd api-spec.yml https://fastapi-server-production-dc2b.up.railway.app
```

---

### 3. backend-architect 🏗️💜

**専門分野**: APIアーキテクチャ設計、データベース最適化、スケーラビリティ

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「Phase5でNotionへの最終動画URL登録APIを設計したい」
→ backend-architect が自動起動
```

##### 明示的呼び出し例
```
「@backend-architect でFastAPI render_server.pyのアーキテクチャレビューを実施」
```

#### 具体的な活用シナリオ

**シナリオ1: Phase5 Notion統合API設計**
```
タスク: 「Phase5: 最終動画URLをNotionデータベースに登録するAPIを設計」

backend-architectの設計:
1. API仕様策定
   - エンドポイント: POST /api/v1/notion/update-video
   - 認証: Bearer token（n8n webhook secret）
   - レートリミット: 10 req/min per page_id

2. Pydanticモデル設計
   ```python
   from pydantic import BaseModel, HttpUrl, Field
   from typing import Optional

   class NotionVideoUpdateRequest(BaseModel):
       page_id: str = Field(..., description="Notion page ID")
       video_url: HttpUrl = Field(..., description="Final video URL")
       video_duration: int = Field(..., ge=1, le=300, description="Duration in seconds")
       video_size_mb: float = Field(..., ge=0, description="File size in MB")
       processing_time: int = Field(..., description="Total processing time in seconds")
       phase_metadata: Optional[dict] = Field(None, description="Phase-wise metadata")

   class NotionVideoUpdateResponse(BaseModel):
       success: bool
       page_id: str
       updated_at: str
       notion_url: HttpUrl
   ```

3. データベーススキーマ（PostgreSQL）
   ```sql
   CREATE TABLE video_processing_history (
       id SERIAL PRIMARY KEY,
       page_id VARCHAR(255) NOT NULL,
       video_url TEXT NOT NULL,
       video_duration INTEGER NOT NULL,
       video_size_mb DECIMAL(10, 2),
       processing_time INTEGER,
       phase_metadata JSONB,
       status VARCHAR(50) DEFAULT 'completed',
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW(),
       INDEX idx_page_id (page_id),
       INDEX idx_created_at (created_at)
   );
   ```

4. エラーハンドリング戦略
   - Notion API rate limit: exponential backoff + retry
   - Network timeout: 30秒 timeout + 3 retries
   - Validation error: 詳細エラーメッセージ返却
   - Database error: transaction rollback + alert

5. スケーラビリティ考慮
   - Async処理: FastAPI async def
   - Connection pooling: asyncpg（max 20 connections）
   - Caching: Redis（page metadata 15分TTL）
   - Monitoring: Prometheus metrics
```

**シナリオ2: render_server.py リファクタリング**
```
タスク: 「render_server.pyが500行を超えたためリファクタリング」

backend-architectの提案:
1. ディレクトリ構造
   ```
   workflows/wf7-video-renderer/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py                    # FastAPI app
   │   ├── api/
   │   │   ├── __init__.py
   │   │   ├── v1/
   │   │   │   ├── __init__.py
   │   │   │   ├── endpoints/
   │   │   │   │   ├── __init__.py
   │   │   │   │   ├── slides.py      # /generate-slide
   │   │   │   │   ├── videos.py      # /generate-single-video
   │   │   │   │   ├── concat.py      # /concat-videos
   │   │   │   │   └── notion.py      # /notion/update-video
   │   ├── core/
   │   │   ├── __init__.py
   │   │   ├── config.py              # Settings管理
   │   │   ├── security.py            # 認証・認可
   │   │   └── logging.py             # ロギング設定
   │   ├── services/
   │   │   ├── __init__.py
   │   │   ├── ffmpeg_service.py      # FFmpeg処理
   │   │   ├── cloudinary_service.py  # Cloudinary統合
   │   │   └── notion_service.py      # Notion API
   │   ├── models/
   │   │   ├── __init__.py
   │   │   ├── requests.py            # Pydantic request models
   │   │   └── responses.py           # Pydantic response models
   │   └── utils/
   │       ├── __init__.py
   │       ├── image_utils.py         # 画像処理ユーティリティ
   │       └── validation.py          # カスタムバリデーション
   ├── tests/
   │   ├── __init__.py
   │   ├── test_api/
   │   └── test_services/
   ├── requirements.txt
   └── Dockerfile.fastapi
   ```

2. 依存性注入パターン
   ```python
   # app/core/config.py
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       cloudinary_cloud_name: str
       cloudinary_api_key: str
       cloudinary_api_secret: str
       notion_api_token: str
       database_url: str
       redis_url: str

       class Config:
           env_file = ".env"

   settings = Settings()

   # app/services/cloudinary_service.py
   from app.core.config import settings
   import cloudinary

   class CloudinaryService:
       def __init__(self):
           cloudinary.config(
               cloud_name=settings.cloudinary_cloud_name,
               api_key=settings.cloudinary_api_key,
               api_secret=settings.cloudinary_api_secret
           )

       async def upload_image(self, file_path: str) -> str:
           # Implementation
           pass
   ```

3. サービス層分離
   ```python
   # app/services/ffmpeg_service.py
   import subprocess
   from typing import BinaryIO

   class FFmpegService:
       @staticmethod
       async def generate_video_from_image(
           image_path: str,
           duration: int,
           output_path: str
       ) -> None:
           cmd = [
               'ffmpeg', '-y',
               '-loop', '1',
               '-i', image_path,
               '-t', str(duration),
               '-c:v', 'libx264',
               '-crf', '23',
               '-preset', 'fast',
               '-pix_fmt', 'yuv420p',
               '-vf', 'scale=1080:1920',
               '-r', '30',
               output_path
           ]
           subprocess.run(cmd, check=True)
   ```

4. API endpoint実装
   ```python
   # app/api/v1/endpoints/videos.py
   from fastapi import APIRouter, HTTPException, Depends
   from app.models.requests import GenerateSingleVideoRequest
   from app.models.responses import GenerateSingleVideoResponse
   from app.services.ffmpeg_service import FFmpegService
   from app.services.cloudinary_service import CloudinaryService

   router = APIRouter()

   @router.post("/generate-single-video", response_model=GenerateSingleVideoResponse)
   async def generate_single_video(
       request: GenerateSingleVideoRequest,
       ffmpeg_service: FFmpegService = Depends(),
       cloudinary_service: CloudinaryService = Depends()
   ):
       try:
           # Implementation
           pass
       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))
   ```
```

---

### 4. devops-automator 🚀🔶

**専門分野**: Railway CI/CD、Docker最適化、インフラ自動化

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「Railwayデプロイを自動化してmainブランチpush時に自動デプロイしたい」
→ devops-automator が自動起動
```

##### 明示的呼び出し例
```
「@devops-automator でDockerfileを最適化してビルド時間を短縮」
```

#### 具体的な活用シナリオ

**シナリオ1: Railway CI/CD パイプライン構築**
```yaml
タスク: 「mainブランチへのpushで自動的にRailwayにデプロイ」

devops-automatorの実装:
1. GitHub Actions workflow作成
   # .github/workflows/railway-deploy.yml
   name: Deploy to Railway

   on:
     push:
       branches: [main]
       paths:
         - 'workflows/wf7-video-renderer/**'
         - 'Dockerfile'
         - 'requirements.txt'

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Setup Railway CLI
           run: |
             npm install -g @railway/cli

         - name: Deploy to Railway
           env:
             RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
           run: |
             railway link ${{ secrets.RAILWAY_PROJECT_ID }}
             railway up --service n8n-python

         - name: Health Check
           run: |
             sleep 30
             curl -f https://n8n-python-production-344b.up.railway.app/health || exit 1

         - name: Notify Success
           if: success()
           run: |
             curl -X POST https://hooks.slack.com/... \
               -d '{"text":"✅ Railway deploy succeeded!"}'

         - name: Notify Failure
           if: failure()
           run: |
             curl -X POST https://hooks.slack.com/... \
               -d '{"text":"❌ Railway deploy failed!"}'

2. railway.toml最適化
   [build]
   builder = "DOCKERFILE"
   dockerfilePath = "Dockerfile"

   [deploy]
   healthcheckPath = "/health"
   healthcheckTimeout = 100
   restartPolicyType = "ON_FAILURE"
   restartPolicyMaxRetries = 3

   [env]
   # 環境変数は Railway dashboard で管理

3. デプロイ戦略
   - Blue-Green deployment: Railway environments利用
   - Canary release: traffic splitting（Pro plan）
   - Rollback: Railway dashboard or CLI

4. モニタリング設定
   - Railway metrics: CPU/Memory/Network
   - Custom metrics: Prometheus + Grafana
   - Log aggregation: Railway logs + Datadog
   - Alerts: Slack webhook統合
```

**シナリオ2: Dockerfile最適化**
```dockerfile
タスク: 「Dockerビルド時間を5分→2分に短縮」

devops-automatorの最適化:
# 最適化前（5分）
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "render_server:app", "--host", "0.0.0.0", "--port", "8000"]

# 最適化後（2分）
# マルチステージビルド + レイヤーキャッシュ最適化
FROM python:3.11-slim as builder

# システム依存関係（変更頻度低）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係（変更頻度中）
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 本番ステージ
FROM python:3.11-slim

# システムライブラリコピー
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係コピー（builder stageから）
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# アプリケーションコード（変更頻度高）
WORKDIR /app
COPY ./app ./app
COPY ./workflows/wf7-video-renderer/render_server.py .

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 非rootユーザー実行
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# ビルド時間改善:
# - マルチステージビルド: builder stageでキャッシュ最大化
# - slim image: サイズ 1.2GB → 400MB
# - レイヤー順序最適化: 変更頻度低い順に配置
# - --no-cache-dir: pip cache削除（100MB削減）
```

**シナリオ3: 監視・アラートシステム構築**
```python
タスク: 「FastAPIの性能とエラーをリアルタイム監視」

devops-automatorの実装:
# 1. Prometheus metricsエンドポイント追加
# app/core/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Metrics定義
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ffmpeg_processing_duration_seconds = Histogram(
    'ffmpeg_processing_duration_seconds',
    'FFmpeg processing duration',
    ['operation']
)

# Middleware
@app.middleware("http")
async def prometheus_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# Metricsエンドポイント
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# 2. Grafana dashboard設定（JSON）
{
  "dashboard": {
    "title": "WF7 Video Renderer",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "FFmpeg Processing Time",
        "targets": [
          {
            "expr": "ffmpeg_processing_duration_seconds"
          }
        ]
      }
    ]
  }
}

# 3. アラートルール（Prometheus AlertManager）
groups:
  - name: wf7_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} (>5%)"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 30
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time detected"
          description: "P95 response time is {{ $value }}s (>30s)"

      - alert: FFmpegProcessingDelay
        expr: ffmpeg_processing_duration_seconds > 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "FFmpeg processing is slow"
          description: "Processing time is {{ $value }}s (>20s)"
```

---

### 5. rapid-prototyper 💚⚡

**専門分野**: 高速プロトタイピング、MVP作成、トレンド機能統合

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「Phase5の新機能プロトタイプを3日で作成したい」
→ rapid-prototyper が自動起動
```

##### 明示的呼び出し例
```
「@rapid-prototyper でWF7のWeb UIダッシュボードを作成」
```

#### 具体的な活用シナリオ

**シナリオ1: Phase5 Notion統合UI プロトタイプ**
```
タスク: 「Phase5完了通知を表示するWeb UIを3日で作成」

rapid-prototyperの実装計画:
Day 1: セットアップ + コア機能
1. プロジェクト初期化
   ```bash
   npm create vite@latest wf7-dashboard -- --template react-ts
   cd wf7-dashboard
   npm install
   npm install @tanstack/react-query axios recharts
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

2. API統合（FastAPI backend）
   ```typescript
   // src/api/client.ts
   import axios from 'axios';

   const API_BASE = 'https://fastapi-server-production-dc2b.up.railway.app';

   export const api = axios.create({
     baseURL: API_BASE,
     timeout: 30000,
   });

   export interface VideoProcessingStatus {
     page_id: string;
     status: 'processing' | 'completed' | 'failed';
     phase: 'phase4a' | 'phase4b' | 'phase4c' | 'completed';
     progress: number; // 0-100
     video_url?: string;
     processing_time?: number;
     error_message?: string;
   }

   export const getProcessingStatus = async (pageId: string) => {
     const { data } = await api.get<VideoProcessingStatus>(
       `/api/v1/status/${pageId}`
     );
     return data;
   };
   ```

3. リアルタイムステータス表示
   ```tsx
   // src/components/ProcessingStatus.tsx
   import { useQuery } from '@tanstack/react-query';
   import { getProcessingStatus } from '../api/client';

   export function ProcessingStatus({ pageId }: { pageId: string }) {
     const { data, isLoading } = useQuery({
       queryKey: ['status', pageId],
       queryFn: () => getProcessingStatus(pageId),
       refetchInterval: 5000, // 5秒ごとにポーリング
     });

     if (isLoading) return <div>Loading...</div>;

     return (
       <div className="p-6 bg-white rounded-lg shadow">
         <h2 className="text-2xl font-bold mb-4">Video Processing Status</h2>

         {/* プログレスバー */}
         <div className="mb-4">
           <div className="flex justify-between mb-2">
             <span>Progress</span>
             <span>{data.progress}%</span>
           </div>
           <div className="w-full bg-gray-200 rounded-full h-2">
             <div
               className="bg-blue-600 h-2 rounded-full transition-all"
               style={{ width: `${data.progress}%` }}
             />
           </div>
         </div>

         {/* 現在のフェーズ */}
         <div className="mb-4">
           <span className="font-semibold">Current Phase:</span>
           <span className="ml-2 px-3 py-1 bg-blue-100 text-blue-800 rounded">
             {data.phase}
           </span>
         </div>

         {/* 完了時の動画プレビュー */}
         {data.status === 'completed' && data.video_url && (
           <div className="mt-4">
             <video
               src={data.video_url}
               controls
               className="w-full max-w-md mx-auto"
             />
             <a
               href={data.video_url}
               target="_blank"
               className="mt-2 inline-block px-4 py-2 bg-green-600 text-white rounded"
             >
               Download Video
             </a>
           </div>
         )}
       </div>
     );
   }
   ```

Day 2: 追加機能
- 処理履歴一覧
- パフォーマンスグラフ（Recharts）
- エラーハンドリング

Day 3: デプロイ
- Vercel/Netlify デプロイ
- 環境変数設定
- ドメイン設定
```

**シナリオ2: Webhook監視ダッシュボード**
```typescript
タスク: 「n8n webhookの実行状況をリアルタイム監視するダッシュボード」

rapid-prototyperの実装:
// src/components/WebhookMonitor.tsx
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface WebhookMetrics {
  timestamp: string;
  endpoint: string;
  response_time_ms: number;
  status_code: number;
  error_message?: string;
}

export function WebhookMonitor() {
  const { data: metrics } = useQuery({
    queryKey: ['webhook-metrics'],
    queryFn: async () => {
      const res = await fetch('https://fastapi-server.../api/v1/metrics/webhooks');
      return res.json() as Promise<WebhookMetrics[]>;
    },
    refetchInterval: 10000, // 10秒ごと
  });

  // レスポンスタイム分析
  const avgResponseTime = metrics?.reduce((acc, m) => acc + m.response_time_ms, 0) / (metrics?.length || 1);
  const errorRate = metrics?.filter(m => m.status_code >= 400).length / (metrics?.length || 1);

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* メトリクス概要 */}
      <div className="col-span-2 grid grid-cols-4 gap-4">
        <MetricCard
          title="Avg Response Time"
          value={`${avgResponseTime.toFixed(0)}ms`}
          trend="down"
        />
        <MetricCard
          title="Error Rate"
          value={`${(errorRate * 100).toFixed(1)}%`}
          trend={errorRate > 0.05 ? 'up' : 'down'}
        />
        <MetricCard
          title="Total Requests"
          value={metrics?.length || 0}
          trend="up"
        />
        <MetricCard
          title="Success Rate"
          value={`${((1 - errorRate) * 100).toFixed(1)}%`}
          trend="up"
        />
      </div>

      {/* レスポンスタイムグラフ */}
      <div className="col-span-2 bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Response Time Trend</h3>
        <LineChart width={800} height={300} data={metrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="response_time_ms" stroke="#8884d8" />
        </LineChart>
      </div>

      {/* エラーログ */}
      <div className="col-span-2 bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Recent Errors</h3>
        <div className="space-y-2">
          {metrics?.filter(m => m.error_message).slice(0, 5).map((m, i) => (
            <div key={i} className="p-3 bg-red-50 border border-red-200 rounded">
              <div className="flex justify-between">
                <span className="font-mono text-sm">{m.endpoint}</span>
                <span className="text-red-600">{m.status_code}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{m.error_message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

### 6. test-writer-fixer 🔵🧪

**専門分野**: テスト作成・修正、テストカバレッジ向上、CI統合

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「render_server.pyの変更後、関連テストを自動実行して修正」
→ test-writer-fixer が自動起動
```

##### 明示的呼び出し例
```
「@test-writer-fixer でFastAPI /generate-single-videoのテストを作成」
```

#### 具体的な活用シナリオ

**シナリオ1: FastAPI エンドポイントテスト作成**
```python
タスク: 「/generate-single-video エンドポイントの包括的テストスイート作成」

test-writer-fixerの実装:
# tests/test_api/test_videos.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import base64
from pathlib import Path

client = TestClient(app)

# テストデータ
VALID_PAYLOAD = {
    "section": "hook",
    "duration": 7,
    "image_url": "https://res.cloudinary.com/test/image/upload/v1/test.png",
    "motion_prompt": "subtle zoom in",
    "text": "テストテキスト",
    "script_id": "test-script-001"
}

class TestGenerateSingleVideo:
    """Generate single video endpoint tests"""

    def test_successful_video_generation(self):
        """正常なリクエストで動画が生成される"""
        response = client.post("/generate-single-video", json=VALID_PAYLOAD)

        assert response.status_code == 200
        data = response.json()

        # レスポンス構造検証
        assert "video_data" in data
        assert "section" in data
        assert "duration" in data
        assert "processing_time" in data

        # Base64検証
        video_data = data["video_data"]
        assert isinstance(video_data, str)
        assert len(video_data) > 0

        # Base64デコード可能性検証
        video_bytes = base64.b64decode(video_data)
        assert len(video_bytes) > 0

        # MP4 magic number検証 (0x00 0x00 0x00 ... ftyp)
        assert b'ftyp' in video_bytes[:32]

    def test_invalid_duration_too_short(self):
        """duration が1秒未満でエラー"""
        payload = {**VALID_PAYLOAD, "duration": 0}
        response = client.post("/generate-single-video", json=payload)

        assert response.status_code == 422
        error = response.json()
        assert "duration" in str(error).lower()

    def test_invalid_duration_too_long(self):
        """duration が20秒超過でエラー"""
        payload = {**VALID_PAYLOAD, "duration": 21}
        response = client.post("/generate-single-video", json=payload)

        assert response.status_code == 422

    def test_invalid_image_url(self):
        """無効な画像URLでエラー"""
        payload = {**VALID_PAYLOAD, "image_url": "not-a-url"}
        response = client.post("/generate-single-video", json=payload)

        assert response.status_code == 422

    def test_missing_required_field(self):
        """必須フィールド欠落でエラー"""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "section"}
        response = client.post("/generate-single-video", json=payload)

        assert response.status_code == 422

    def test_cloudinary_image_download_failure(self, monkeypatch):
        """Cloudinary画像ダウンロード失敗時のエラーハンドリング"""
        def mock_download_fail(*args, **kwargs):
            raise Exception("Network error")

        monkeypatch.setattr("requests.get", mock_download_fail)

        response = client.post("/generate-single-video", json=VALID_PAYLOAD)
        assert response.status_code == 500
        assert "download" in response.json()["detail"].lower()

    def test_ffmpeg_failure(self, monkeypatch):
        """FFmpeg実行失敗時のエラーハンドリング"""
        def mock_ffmpeg_fail(*args, **kwargs):
            raise subprocess.CalledProcessError(1, "ffmpeg")

        monkeypatch.setattr("subprocess.run", mock_ffmpeg_fail)

        response = client.post("/generate-single-video", json=VALID_PAYLOAD)
        assert response.status_code == 500

    @pytest.mark.parametrize("duration", [3, 7, 10, 15, 20])
    def test_various_durations(self, duration):
        """様々なduration値でのテスト"""
        payload = {**VALID_PAYLOAD, "duration": duration}
        response = client.post("/generate-single-video", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["duration"] == duration

    def test_response_time_performance(self):
        """レスポンスタイムが許容範囲内"""
        import time

        start = time.time()
        response = client.post("/generate-single-video", json=VALID_PAYLOAD)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 15.0  # 15秒以内（duration=7sの場合）

    def test_concurrent_requests(self):
        """並行リクエスト処理"""
        import concurrent.futures

        def make_request():
            return client.post("/generate-single-video", json=VALID_PAYLOAD)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]

        # すべてのリクエストが成功
        assert all(r.status_code == 200 for r in results)

# Pytest fixtures
@pytest.fixture
def sample_video_bytes():
    """テスト用動画バイナリデータ"""
    # 実際の動画ファイルまたはモックデータ
    return b'test video data'

# カバレッジ測定
# pytest --cov=app --cov-report=html tests/
```

**シナリオ2: n8nワークフロー統合テスト**
```python
タスク: 「Phase4a→4b→4c E2Eテストの自動化」

test-writer-fixerの実装:
# tests/test_integration/test_phase4_e2e.py
import pytest
import requests
import time
from typing import Dict, Any

class TestPhase4E2E:
    """Phase4 End-to-End integration tests"""

    PHASE4A_WEBHOOK = "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator"
    PHASE4C_WEBHOOK = "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-video-concat"

    @pytest.fixture
    def notion_page_id(self):
        """テスト用Notion page ID"""
        return "2aa68d5c-2986-815c-aba4-da72d9830bf3"

    def test_phase4a_slide_generation(self, notion_page_id):
        """Phase4a: 7スライド生成テスト"""
        payload = {"notion_page_id": notion_page_id}
        response = requests.post(self.PHASE4A_WEBHOOK, json=payload, timeout=120)

        assert response.status_code == 200
        data = response.json()

        # 7スライド生成確認
        assert "slides" in data
        assert len(data["slides"]) == 7

        # 各スライドにimage_url存在確認
        for slide in data["slides"]:
            assert "image_url" in slide
            assert slide["image_url"].startswith("https://res.cloudinary.com/")
            assert "section" in slide
            assert slide["section"] in ["hook", "intro", "point1", "point2", "point3", "cta", "outro"]

    def test_phase4b_video_generation(self, notion_page_id):
        """Phase4b: 7動画生成テスト（Phase4a経由）"""
        # Phase4a実行
        phase4a_response = requests.post(
            self.PHASE4A_WEBHOOK,
            json={"notion_page_id": notion_page_id},
            timeout=120
        )
        assert phase4a_response.status_code == 200

        # Phase4bが自動実行されるまで待機
        time.sleep(60)

        # n8n execution確認（MCP経由）
        # ここでは簡易チェック：Phase4bのexecutionが7回実行されたか
        # 実際の実装ではn8n APIまたはMCPツールを使用

    def test_phase4c_video_concatenation(self, notion_page_id):
        """Phase4c: 動画結合テスト"""
        # Phase4a→4b実行（前提条件）
        phase4a_response = requests.post(
            self.PHASE4A_WEBHOOK,
            json={"notion_page_id": notion_page_id},
            timeout=120
        )
        assert phase4a_response.status_code == 200

        # Phase4b完了待機
        time.sleep(60)

        # Phase4c実行
        # 通常はPhase4bから自動トリガーされるが、ここでは手動実行
        videos_metadata = [
            {
                "section": "hook",
                "url": "https://res.cloudinary.com/.../hook.mp4",
                "duration": 3
            },
            # ... 残り6動画
        ]

        phase4c_response = requests.post(
            self.PHASE4C_WEBHOOK,
            json={"videos_metadata": videos_metadata},
            timeout=120
        )

        assert phase4c_response.status_code == 200
        data = phase4c_response.json()

        # 最終動画URL確認
        assert "final_video_url" in data
        assert data["final_video_url"].startswith("https://")

        # 動画スペック確認
        assert data["total_duration"] == sum(v["duration"] for v in videos_metadata)

    def test_full_pipeline_performance(self, notion_page_id):
        """フルパイプライン性能テスト（制限時間内完了）"""
        start_time = time.time()

        # Phase4a実行
        response = requests.post(
            self.PHASE4A_WEBHOOK,
            json={"notion_page_id": notion_page_id},
            timeout=180
        )
        assert response.status_code == 200

        elapsed = time.time() - start_time

        # 性能目標: 60秒以内にPhase4a完了
        assert elapsed < 60, f"Phase4a took {elapsed:.1f}s (>60s)"

    @pytest.mark.slow
    def test_retry_mechanism(self):
        """Phase4c retry loopテスト"""
        # FAL APIがIN_QUEUE状態を返し続けるシナリオをモック
        # retry_countが正しくincrementされるか検証
        pass

# pytest.ini設定
# [pytest]
# markers =
#     slow: marks tests as slow (deselect with '-m "not slow"')
#     integration: marks tests as integration tests
```

---

### 7. performance-benchmarker ⚡📈

**専門分野**: 性能ベンチマーク、ボトルネック特定、最適化提案

#### WF7プロジェクトでの活用例

##### 自動トリガー例
```
「Phase4全体の処理時間を計測してボトルネックを特定」
→ performance-benchmarker が自動起動
```

#### 具体的な活用シナリオ

**シナリオ1: Phase4 パフォーマンスプロファイリング**
```bash
タスク: 「Phase4a→4b→4cの各処理時間を詳細計測し、最適化ポイントを特定」

performance-benchmarkerの分析:
1. ベンチマークスクリプト作成
   ```python
   # benchmark_phase4.py
   import time
   import requests
   import statistics
   from typing import List, Dict

   class Phase4Benchmarker:
       def __init__(self):
           self.results: List[Dict] = []

       def benchmark_phase4a(self, notion_page_id: str, iterations: int = 10):
           """Phase4a ベンチマーク"""
           times = []

           for i in range(iterations):
               start = time.time()
               response = requests.post(
                   "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator",
                   json={"notion_page_id": notion_page_id},
                   timeout=180
               )
               elapsed = time.time() - start

               times.append(elapsed)
               print(f"Iteration {i+1}: {elapsed:.2f}s")
               time.sleep(5)  # Rate limiting対策

           return {
               "phase": "Phase4a",
               "mean": statistics.mean(times),
               "median": statistics.median(times),
               "min": min(times),
               "max": max(times),
               "stddev": statistics.stdev(times) if len(times) > 1 else 0
           }

       def benchmark_single_video_generation(self, iterations: int = 20):
           """Phase4b 個別動画生成ベンチマーク"""
           payload = {
               "section": "hook",
               "duration": 7,
               "image_url": "https://res.cloudinary.com/.../test.png",
               "motion_prompt": "subtle zoom",
               "text": "ベンチマークテスト",
               "script_id": "benchmark-001"
           }

           times = []
           for i in range(iterations):
               start = time.time()
               response = requests.post(
                   "https://fastapi-server-production-dc2b.up.railway.app/generate-single-video",
                   json=payload,
                   timeout=30
               )
               elapsed = time.time() - start
               times.append(elapsed)

           return {
               "phase": "Phase4b (single video)",
               "mean": statistics.mean(times),
               "median": statistics.median(times),
               "p95": sorted(times)[int(len(times) * 0.95)],
               "p99": sorted(times)[int(len(times) * 0.99)]
           }

       def benchmark_video_concatenation(self, iterations: int = 5):
           """Phase4c 動画結合ベンチマーク"""
           videos_metadata = [
               {"section": f"video{i}", "url": f"https://test.com/v{i}.mp4", "duration": 7}
               for i in range(7)
           ]

           times = []
           for i in range(iterations):
               start = time.time()
               response = requests.post(
                   "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-video-concat",
                   json={"videos_metadata": videos_metadata},
                   timeout=120
               )
               elapsed = time.time() - start
               times.append(elapsed)
               time.sleep(30)  # FAL API制限対策

           return {
               "phase": "Phase4c",
               "mean": statistics.mean(times),
               "median": statistics.median(times)
           }

       def generate_report(self):
           """ベンチマークレポート生成"""
           print("\n" + "="*60)
           print("Phase4 Performance Benchmark Report")
           print("="*60 + "\n")

           for result in self.results:
               print(f"\n{result['phase']}:")
               for key, value in result.items():
                   if key != 'phase':
                       print(f"  {key}: {value:.2f}s")

   # 実行
   benchmarker = Phase4Benchmarker()
   benchmarker.results.append(benchmarker.benchmark_phase4a("test-page-id"))
   benchmarker.results.append(benchmarker.benchmark_single_video_generation())
   benchmarker.results.append(benchmarker.benchmark_video_concatenation())
   benchmarker.generate_report()
   ```

2. 実行結果例
   ```
   ============================================================
   Phase4 Performance Benchmark Report
   ============================================================

   Phase4a:
     mean: 16.82s
     median: 16.50s
     min: 14.20s
     max: 22.10s
     stddev: 2.15s

     ボトルネック分析:
     - Notion API呼び出し: 3.2s (19%)
     - スライド生成（7枚）: 10.5s (62%)
     - Cloudinaryアップロード（7枚）: 2.8s (17%)
     - その他: 0.32s (2%)

   Phase4b (single video):
     mean: 8.45s
     median: 8.20s
     p95: 9.80s
     p99: 10.50s

     ボトルネック分析:
     - 画像ダウンロード: 0.85s (10%)
     - FFmpeg処理: 7.15s (85%)
     - Base64エンコード: 0.35s (4%)
     - その他: 0.10s (1%)

   Phase4c:
     mean: 24.60s
     median: 23.80s

     ボトルネック分析:
     - FAL API submit: 0.50s (2%)
     - FAL API polling (2 iterations): 20.00s (81%)
     - 結果取得＆レスポンス: 4.10s (17%)
   ```

3. 最適化提案
   ```markdown
   ### 優先度1: Phase4b FFmpeg最適化（7.15s → 4.5s）
   - 現状: シングルスレッドFFmpeg処理
   - 提案: libx264プリセット変更（fast → ultrafast）
   - 期待効果: 37%高速化（7.15s → 4.5s）
   - 実装工数: 0.5日

   ### 優先度2: Phase4c FAL API polling最適化（20s → 15s）
   - 現状: 10秒間隔ポーリング × 2回
   - 提案: 5秒間隔ポーリング + exponential backoff
   - 期待効果: 25%高速化（20s → 15s）
   - 実装工数: 1日

   ### 優先度3: Phase4b 並列化（28s → 15s）
   - 現状: 7動画をシリアル処理（8.45s × 7 = 59s）
   - 提案: 3並列処理（8.45s × 3 = 25.35s）
   - 期待効果: 57%高速化（59s → 25s）
   - 実装工数: 2日
   ```
```

---

### 8. experiment-tracker 📊🔬

**専門分野**: A/Bテスト管理、実験追跡、データ分析

#### WF7プロジェクトでの活用例

```
タスク: 「Phase4b FFmpegプリセット変更（fast vs ultrafast）の効果測定」

experiment-trackerの実装:
# experiments/phase4b_ffmpeg_preset_test.md

## 実験概要
**実験名**: Phase4b FFmpeg Preset Optimization
**期間**: 2025-11-15 ~ 2025-11-20
**目的**: FFmpegプリセット変更による処理時間短縮効果の測定

## 仮説
- H1: ultrafast プリセット使用により処理時間が30-40%短縮される
- H2: 動画品質の劣化は許容範囲内（主観評価で80%以上が「問題なし」）
- H3: ファイルサイズは10-20%増加する

## 実験設計
### Control Group (fast preset)
```python
cmd = ['ffmpeg', '-y', '-loop', '1', '-i', image,
       '-t', str(duration), '-c:v', 'libx264',
       '-crf', '23', '-preset', 'fast',  # ← Control
       '-pix_fmt', 'yuv420p', '-vf', 'scale=1080:1920',
       '-r', '30', output]
```

### Treatment Group (ultrafast preset)
```python
cmd = ['ffmpeg', '-y', '-loop', '1', '-i', image,
       '-t', str(duration), '-c:v', 'libx264',
       '-crf', '23', '-preset', 'ultrafast',  # ← Treatment
       '-pix_fmt', 'yuv420p', '-vf', 'scale=1080:1920',
       '-r', '30', output]
```

### サンプルサイズ
- 各グループ: n=50動画
- 合計: 100動画生成

### 測定指標
1. 処理時間（秒）
2. ファイルサイズ（MB）
3. 動画品質スコア（PSNR, SSIM）
4. 主観評価（5段階）

## 実験実行
```bash
# Control group
for i in {1..50}; do
  python benchmark_video_gen.py --preset fast --output control_$i.mp4
done

# Treatment group
for i in {1..50}; do
  python benchmark_video_gen.py --preset ultrafast --output treatment_$i.mp4
done
```

## 結果
### 処理時間
- Control (fast): 平均 8.45s (σ=0.82s)
- Treatment (ultrafast): 平均 5.32s (σ=0.65s)
- **改善率: 37.0%** ✅ (仮説: 30-40%)

### ファイルサイズ
- Control: 平均 185KB (σ=12KB)
- Treatment: 平均 215KB (σ=15KB)
- **増加率: 16.2%** ✅ (仮説: 10-20%)

### 動画品質（PSNR）
- Control: 平均 42.5 dB
- Treatment: 平均 40.8 dB
- 差分: -1.7 dB（許容範囲）

### 主観評価
- 問題なし: 87% ✅ (仮説: 80%以上)
- やや品質低下を感じる: 11%
- 明らかに品質低下: 2%

## 結論
**結果: 採用** ✅

ultrafast プリセット採用により:
- 処理時間37%短縮（Phase4b全体で 59s → 37s）
- ファイルサイズ16%増加は許容範囲
- 動画品質は87%が「問題なし」と評価

## 実装
- PR: #XXX
- デプロイ日: 2025-11-21
- ロールバック計画: railway rollback可能
```

---

### 9. project-shipper 🚢📦

**専門分野**: リリース管理、デプロイオーケストレーション、ローンチチェックリスト

#### WF7プロジェクトでの活用例

```
タスク: 「Phase5本番リリースのローンチチェックリスト作成」

project-shipperの実装:
# Phase5 Launch Checklist

## Pre-Launch (T-7日)
- [ ] 全機能開発完了
  - [ ] Phase5 Notion統合API実装
  - [ ] Web UI完成
  - [ ] エラーハンドリング完備
- [ ] テスト完了
  - [ ] Unit tests (カバレッジ >80%)
  - [ ] Integration tests
  - [ ] E2E tests
  - [ ] Load tests (100 concurrent users)
- [ ] セキュリティレビュー
  - [ ] 認証・認可実装確認
  - [ ] Rate limiting設定
  - [ ] CORS設定確認

## Pre-Launch (T-3日)
- [ ] ステージング環境デプロイ
  - [ ] Railway staging environment作成
  - [ ] 環境変数設定
  - [ ] データベースマイグレーション
- [ ] ステージングテスト
  - [ ] Smoke tests
  - [ ] UAT (User Acceptance Test)
  - [ ] Performance validation

## Launch Day (T-0)
- [ ] 本番デプロイ
  - [ ] Database backup作成
  - [ ] Blue-Green deployment実行
  - [ ] Health check確認
- [ ] 監視設定
  - [ ] Datadog alerts有効化
  - [ ] Slack通知設定
  - [ ] Error tracking (Sentry) 確認

## Post-Launch (T+1日)
- [ ] メトリクス確認
  - [ ] エラー率 <0.1%
  - [ ] レスポンスタイム p95 <500ms
  - [ ] ユーザーフィードバック収集
- [ ] ドキュメント更新
  - [ ] API documentation更新
  - [ ] README.md更新
  - [ ] CURRENT_STATE.md更新
```

---

## 実践的ユースケース

### ユースケース1: 新フェーズ開発（Phase5）

**目標**: Phase5（Notion最終登録）を5日で完成

**エージェント連携フロー**:

```
Day 1-2: 設計＆プロトタイプ
@backend-architect → API設計書作成
@rapid-prototyper → FastAPIエンドポイント実装
@test-writer-fixer → テストスケルトン作成

Day 3: 実装＆テスト
@backend-architect → データベーススキーマ実装
@test-writer-fixer → 包括的テスト作成
@api-tester → APIパフォーマンステスト

Day 4: 統合＆最適化
@workflow-optimizer → n8nワークフロー統合
@performance-benchmarker → ボトルネック分析
@devops-automator → CI/CDパイプライン構築

Day 5: デプロイ
@project-shipper → ローンチチェックリスト実行
@devops-automator → Railway本番デプロイ
@test-writer-fixer → Smoke tests実行
```

---

### ユースケース2: パフォーマンス改善キャンペーン

**目標**: Phase4全体の処理時間を50%短縮（49秒→25秒）

**エージェント連携フロー**:

```
Week 1: 現状分析
@performance-benchmarker → 詳細プロファイリング
@workflow-optimizer → ボトルネック特定
@experiment-tracker → 改善実験計画立案

Week 2: 最適化実装
@backend-architect → 並列処理アーキテクチャ設計
@rapid-prototyper → バッチ処理エンドポイント実装
@test-writer-fixer → パフォーマンステスト作成

Week 3: 検証＆デプロイ
@api-tester → 負荷テスト実行
@experiment-tracker → A/Bテスト結果分析
@project-shipper → 段階的ロールアウト
```

---

## ワークフローとエージェントのマッピング

| タスク | 最適エージェント | 補助エージェント |
|--------|----------------|----------------|
| 新ワークフロー作成 | rapid-prototyper | workflow-optimizer |
| ワークフロー最適化 | workflow-optimizer | performance-benchmarker |
| Webhook負荷テスト | api-tester | performance-benchmarker |
| FastAPIエンドポイント設計 | backend-architect | rapid-prototyper |
| Railway CI/CD構築 | devops-automator | project-shipper |
| テスト作成・修正 | test-writer-fixer | api-tester |
| パフォーマンス測定 | performance-benchmarker | workflow-optimizer |
| A/Bテスト管理 | experiment-tracker | performance-benchmarker |
| リリース管理 | project-shipper | devops-automator |
| アーキテクチャレビュー | backend-architect | workflow-optimizer |

---

## ベストプラクティス

### 1. エージェント選択

**✅ Do**:
- タスクに最適なエージェントを選択
- 複雑なタスクは複数エージェント連携
- 自動トリガーを活用（明示的呼び出しは補助的に）

**❌ Don't**:
- すべてを1つのエージェントに任せない
- エージェントの専門外タスクを強要しない

### 2. ワークフロー統合

**✅ Do**:
- n8nワークフロー変更は`workflow-optimizer`で分析
- パフォーマンス問題は`performance-benchmarker`で測定
- 本番デプロイは`project-shipper`でチェックリスト実行

**❌ Don't**:
- ワークフロー変更を直接実施（分析なし）
- 推測に基づく最適化

### 3. テスト戦略

**✅ Do**:
- `test-writer-fixer`: Unit/Integration tests
- `api-tester`: Load/Performance tests
- `experiment-tracker`: A/B tests

**❌ Don't**:
- テストなしでデプロイ
- テストカバレッジ<80%

---

## トラブルシューティング

### Q1: エージェントが起動しない

**原因**: エージェント名のタイプミス、Claude Code未再起動

**解決**:
```bash
# エージェント存在確認
ls ~/.claude/agents/testing/workflow-optimizer.md

# Claude Code再起動
# Claude Codeを終了して再起動
```

### Q2: 自動トリガーが機能しない

**原因**: タスク説明が不明確

**解決**:
```
# ❌ 悪い例
「Phase4を速くして」

# ✅ 良い例
「Phase4a→4b→4cパイプラインのボトルネックを分析して処理時間を短縮」
→ workflow-optimizer または performance-benchmarker が起動
```

### Q3: エージェントの出力が期待と異なる

**原因**: コンテキスト不足

**解決**:
```
# 詳細なコンテキストを提供
「@backend-architect でPhase5 Notion統合APIを設計。
 要件:
 - 最終動画URL登録
 - 処理時間記録
 - エラーハンドリング
 - Rate limiting (10 req/min)
 - PostgreSQL履歴保存」
```

---

## まとめ

### 重要ポイント

1. **グローバル利用**: 全プロジェクトで利用可能
2. **自動トリガー優先**: タスク説明で自動起動を活用
3. **エージェント連携**: 複雑タスクは複数エージェント協働
4. **SuperClaude併用**: ペルソナシステムと補完関係

### 次のステップ

1. Claude Code再起動してエージェント有効化
2. 簡単なタスクで動作確認（例: `@workflow-optimizer でCURRENT_STATE.mdを分析`）
3. 本ガイドを参考に実際のプロジェクトで活用
4. 効果測定＆フィードバック

---

**関連ドキュメント**:
- Contains Studio GitHub: https://github.com/contains-studio/agents
- Claude Code Subagents公式ドキュメント: https://docs.claude.com/en/docs/claude-code/sub-agents

**更新履歴**:
- 2025-11-15 08:49:26 JST: 初版作成
