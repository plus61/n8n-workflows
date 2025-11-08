# 🎯 WF7 Phase 4: FAL.ai実装 設計計画書

**作成日**: 2025-11-06
**目的**: FAL.ai認証テスト完了後の具体的な実装手順と修正計画の策定
**バージョン**: 1.0

---

## 📊 現状分析

### 現在の実装状況

```yaml
Railway n8n環境:
  ✅ デプロイ成功（コミット f9064eb）
  ✅ n8n 1.118.2 稼働中
  ✅ FFmpeg + Noto Sans JPフォント インストール済み
  ✅ Python環境（Code Node対応）
  ✅ URL: https://n8n-python-production-344b.up.railway.app/

既存WF7 Phase4:
  - Workflow ID: xvlnFeJJwHKMHBwK
  - 現在の実装: fal.ai FFmpeg API使用
  - 状態: 稼働中

認証テスト:
  ⏳ FAL.ai API認証テスト実施中
  ⏳ 結果待ち
```

### 実装方針の確認

```yaml
ハイブリッドアプローチ:
  Phase 4a: Pillowでスライド画像生成（7枚）
  Phase 4b: FAL Image-to-Videoで動画化（7本）
  Phase 4c: FFmpegで結合（1本の完成動画）

コスト削減効果:
  Creatomate比: 70-84%削減
  月間コスト: $39.20（70本想定）
  レンダリング単価: $0.56/本

工数見積もり:
  Phase 4a: 2🍅
  Phase 4b: 2🍅
  Phase 4c: 1🍅
  E2Eテスト: 1🍅
  合計: 6🍅（約1.6時間）
```

### 最新ベースワークフロー（WF7phase4_v3 / `qSN7EHj5yl0nPXij`）

- **稼働環境**: Railway `https://n8n-python-production-344b.up.railway.app/` でホスト。Webhook→Notion→FAL→Drive→Notion更新までを1本で実行するPhase4 v3がベース
- **現在の役割**: Phase3までのデータ収集を受け、`Submit to FAL → Fetch Status → Download Image → Driveアップロード → Notion更新 → Webhook応答` までを単一ペイロードで処理
- **確認済み課題** (`docs/testing/wf7-phase4-v3-test-report.md` より):
  - FAL `/compose` のレンダリング完了待ちでタイムアウト（28秒で停止）
  - Webhookレスポンス未返却、`DriveへUL` 以降が実行されない
  - リトライループが長大な線形チェーンとして検知されており構造改善が必要
- **ドッキング要件**: Phase4a/4bで生成した `slides_metadata` / `videos_metadata` を本ベースに安全に受け渡し、既存のWebhook～Notion整合性・資格情報を再利用する

---

## 🔧 実装計画

### ドッキングロードマップ（WF7phase4_v3ベース）

1. **S0: ベース固定化** – 現行 `WF7phase4_v3 (qSN7EHj5yl0nPXij)` を `mcp__n8n-mcp__n8n_get_workflow` でバックアップ
2. **S1: Phase4a接続** – Webhook受信直後の「データ統合」以降に Phase4a サブワークフロー（または Sub-Workflow ノード）を挿入し、`slides_metadata[7]` を返す
3. **S2: Phase4b接続** – 既存 `Submit to FAL` 連鎖を分解し、`Split In Batches → HTTP Request (FAL) → Wait/Fetch Status` 構造へ差し替えて `videos_metadata` を生成
4. **S3: Phase4c接続** – Phase4bの集約ノード後に `Code (FFmpeg concat)` を追加、結合動画→Drive→Notion更新→Webhook応答を一気通貫化
5. **S4: テスト&リリース** – Phase4a/b/c単体テスト → E2E → バージョンスナップショット → ドキュメント更新

### 前提条件の確認

**✅ すでに完了している項目**:
1. Railway環境のセットアップ（FFmpeg, Noto Sans JPフォント）
2. n8n専用Dockerfileの確立
3. Python Code Node環境の準備

**⏳ 認証テスト後に実施する項目**:
1. FAL API Key取得・設定
2. n8n Credentials登録
3. 初回動画生成テスト

---

## 🔌 Phase4a/4b/4c ドッキング設計（WF7phase4_v3ベース）

### Step 0: 既存ワークフローの吸収
- `Webhook - Phase4_v3入口`、`Notion API呼び出し`、`データ統合`、`Notion更新`、`Respond to Webhook` はそのまま再利用し、資格情報や公開URLの変更を避ける
- `Submit to FAL` 以降の連鎖（`Payload Builder`、`Wait for Processing`、`Retry Counter` など）を差し替え対象に限定し、Railway実行ログの互換性を確保
- バックアップ: `mcp__n8n-mcp__n8n_get_workflow { id: "qSN7EHj5yl0nPXij" }` でJSONを取得し、`workflows/archive/wf7phase4_v3_YYYYMMDD.json`へ一時保存

### Step 1: Phase4a（スライド生成）を挿入
- `Execute Workflow` / `Sub-Workflow` ノードで `WF7-Phase4a` を呼び出し、入力に `script_id`, `motion_prompts`, `duration_config`, `visual_elements`, `brand_colors`, `font_sizes` を含める
- Phase4a出力（`slides_metadata`）を `Set - Phase4a Payload` で下記形式に整形し、後続のFAL処理がそのまま参照できるようにする
```json
{
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "image_url": "https://drive.google.com/uc?export=download&id=...",
      "motion_prompt": "dramatic zoom in effect...",
      "drive_file_id": "1abc...",
      "filename": "slide_1_hook.png"
    }
  ]
}
```
- Phase4a失敗時は `IF - Phase4a Status` → `Notion status = error` → `Respond to Webhook` を即返却し、タイムアウトを防止
- **実装状況**: Phase4a専用ワークフローは n8n Workflow ID `LYPbvJfkMzLlhc6t`（Railway: https://n8n-python-production-344b.up.railway.app/workflow/LYPbvJfkMzLlhc6t）で稼働中。`slides_metadata[7]` の生成とGoogle Driveアップロード済みを確認済み。

### Step 2: Phase4b（FAL Image-to-Video）を再構築
- 既存 `Submit to FAL` ノードを `Split In Batches (size:1)` + `HTTP Request - Submit to FAL` + `Wait (10s)` + `HTTP Request - Fetch Status` のループ構造へ置き換え、429回避と明示的な `retryCount <= 5` を実装
- `Check Render Status` で `status in ["COMPLETED"]` を判定し、成功時のみ `Get Result URL` → `Download Video` を実行、その他はリトライまたは失敗分岐へ送る
- ループ終了後に `Aggregate - videos_metadata` ノードを追加し、Phase4cに必要な `section, duration, video_url, fal_request_id, render_elapsed` をまとめる
- 詳細は `docs/implementation/WF7-Phase4abc-docking-plan.md` の「Phase4b → 4c データ契約」を参照
- **実装状況**: Phase4b専用ワークフローは n8n Workflow ID `wHaKi98mTlUvFIOR`（Railway: https://n8n-python-production-344b.up.railway.app/workflow/wHaKi98mTlUvFIOR）。Phase4a出力を入力に7本の `videos_metadata` を生成するところまで完了済み。

### Step 3: Phase4c（FFmpeg結合）でファイナル動画生成
- 新規 `Code - FFmpeg Concat` ノード（`phase4c_ffmpeg_concat.py`）に `videos_metadata` を渡し、`/tmp/wf7_phase4c_{executionId}` へ動画を一時ダウンロード
- コマンド例: `ffmpeg -y -safe 0 -f concat -i concat.txt -c copy output.mp4`。`codec copy` 失敗時は `libx264` へフォールバック、ログを `concat_log` として保持
- 結果を `Google Drive - Upload final video` → `Set - Final Video Metadata` → `Notion更新` → `Respond to Webhook` へ接続し、既存レスポンス形式を維持

### Step 4: モニタリングとテスト観点
- 各Step完了時に `Execution Tag` を付与し、`mcp__n8n-mcp__n8n_list_executions` で `phase4-step1/2/3` を集計可能にする
- Webhookノードの `responseMode: "responseNode"` を継続しつつ、途中失敗時は必ず `Timeout Error Response` ノードを経由（`onError: continueRegularOutput` を設定）
- テスト順序: Phase4a単体（ダミーscript_id）→ Phase4b単体（モックslides）→ Phase4c単体（ダミー動画URL）→ Phase4a→4b接続 → フルE2E (`docs/testing/wf7-phase4-v3-test-report.md` の観点を踏襲)
- 監視: リトライ回数が5回を超えた場合はSlack通知、FFmpeg失敗時は `/tmp` のログパスをNotionに保存して手動リカバリできる状態にする

---

## 🧩 WF7phase4_v3 × Phase4a/4b/4c ドッキングイメージ

```
┌──────────┐      ┌────────────────────────┐      ┌──────────────────────────┐
│Webhook    │ POST │ script_id + metadata     │      │ Notion Query + Data Merge │
│(WF7phase4)├─────▶│ (Phase3成果)             │─────▶│ (既存骨格)                 │
└──────────┘      └────────────────────────┘      └─────────┬────────────────┘
                                                              │ slides_metadata request
                                                     ┌────────▼────────┐
                                                     │Execute/Sub      │
                                                     │Phase4a Slides   │
                                                     └────────┬────────┘
                                                     slides_metadata │
                                                                   ▼
                                                          ┌───────────────┐
                                                          │Phase4b FAL    │
                                                          │Split→Compose  │
                                                          │→Fetch/Retry   │
                                                          └────────┬──────┘
                                                        videos_metadata │
                                                                     ▼
                                                    ┌────────────────────────┐
                                                    │Phase4c FFmpeg Concat   │
                                                    │DL→concat→Drive Upload  │
                                                    └──────────┬────────────┘
                                                           final │ video_url
                                                                  ▼
                                                         ┌──────────────────┐
                                                         │Notion Update &   │
                                                         │Respond to Webhook│
                                                         └──────────────────┘
```

- **青: 既存WF7phase4_v3骨格**（Webhook/Notion/レスポンス）をそのまま残し、資格情報や公開URLを変更しない。
- **緑: Phase4a/4b/4cブロック**はサブワークフローまたはノード追加で段階的に有効化。`slides_metadata` → `videos_metadata` → `final_video` の受け渡しを一本化。
- **制御ポイント**: 各ブロック完了後に `Execution Tag` とログを残し、問題時は該当ブロックのみ切り戻せる。
- **テストフロー**: Phase4a単体→Phase4b単体→Phase4c単体→4a+4b→4a+4b+4cの順に段階テスト。Webhook全体テストはPhase4c接続後に実施。

---

## 📋 Phase 2-3への修正要求

### 1. Notion DBスキーマ更新

**追加カラム**（Phase 4a用）:

```yaml
新規カラム:
  motion_prompts:
    - Type: JSON
    - 説明: 各スライドの動きプロンプト（7種類）
    - 例: {"hook": "dramatic zoom in effect", "intro": "smooth slide transition", ...}

  duration_config:
    - Type: JSON
    - 説明: 各セクションの秒数設定
    - 例: {"hook": 3, "intro": 10, "point1": 13, ...}

  visual_elements:
    - Type: JSON
    - 説明: アイコン・図解の指定
    - 例: {"hook": {"icon": "⚠️", "position": "top-center"}, ...}

  brand_colors:
    - Type: JSON
    - 説明: ブランドカラー設定
    - 例: {"background": "#1a1a2e", "primary_text": "#ffffff", ...}

  font_sizes:
    - Type: JSON（オプション）
    - 説明: フォントサイズ設定
```

**実装方法**:
- Notion API経由でプロパティを追加
- または Notion Web UIで手動追加

---

### 2. ChatGPTプロンプトへのSTEP11追加

**Phase 2-3のChatGPT プロンプトに以下を追加**:

```markdown
## STEP11: 動きのプロンプト生成

各セクションの動画に適した「動きのプロンプト」を生成します。

**各セクションの推奨される動き**:

1. **フック（3秒）**:
   - 目的: 視聴者の注意を一瞬で引く
   - 推奨: ズームイン、ドラマチックな登場
   - 例: "dramatic zoom in effect, professional business style, sharp focus"

2. **導入（10秒）**:
   - 目的: 視聴者の悩みに共感し、動画の価値を示す
   - 推奨: スムーズなスライド、落ち着いたトーン
   - 例: "smooth slide transition, calm professional tone, steady camera"

3. **本編（13秒×3）**:
   - 目的: 3つの要点を明確に伝える
   - 推奨: フェードイン、軽いズーム、教育的な雰囲気
   - 例: "gentle fade in with subtle zoom, educational style, clean motion"

4. **まとめ（20秒）**:
   - 目的: 得られる未来を描き、信頼感を与える
   - 推奨: シネマティックなパン、インスピレーショナル
   - 例: "cinematic pan effect, inspiring tone, smooth movement"

5. **CTA（7秒）**:
   - 目的: 行動を促す
   - 推奨: パルス効果、緊急感、注目を引く
   - 例: "pulsing call-to-action, urgent professional, attention-grabbing"

**出力形式（JSON）**:
```json
{
  "hook": "...",
  "intro": "...",
  "point1": "...",
  "point2": "...",
  "point3": "...",
  "summary": "...",
  "cta": "..."
}
```
```

---

## 🔧 Phase 4の詳細実装計画

### Phase 4a: スライド画像生成（2🍅）

#### n8nワークフロー構成

```yaml
Node 1: Webhook Trigger
  - Path: /webhook-test/wf7-phase4a-slides
  - Method: POST
  - 説明: 外部からの実行トリガー

Node 2: Notion Database Query
  - Database: WF7_Scripts
  - Filter: status = "approved"
  - Sort: created_at DESC
  - Limit: 1
  - 説明: 最新の承認済み台本を取得

Node 3: Code Node (Python) - Slide Generator
  - 機能: 7枚のスライド画像を生成
  - 入力: Notion DBのデータ
  - 出力: 7つのbase64画像 + メタデータ
  - ライブラリ: Pillow, textwrap, base64

Node 4: Split Out (1→7)
  - 7枚の画像を個別アイテムに分割
  - 各アイテムに section, duration, image_base64 を含む

Node 5: HTTP Request - Upload to Google Drive
  - Method: POST
  - URL: Google Drive API
  - Body: image_base64 → file upload
  - 出力: Google Drive File ID + URL

Node 6: Aggregate
  - 7枚の画像URLを配列に結合
  - 順序保持（hook→intro→point1-3→summary→cta）

Node 7: Set Variables
  - slides配列を整形
  - Phase 4bへの準備
```

#### Pythonコード実装（Node 3）

**実装場所**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/phase4a_slide_generator.py`

**主要機能**:
- Pillowで1080x1920の縦型画像生成
- Noto Sans JPフォント使用
- テキスト折り返し、中央配置
- アイコン・ラベル・秒数表示
- base64エンコード出力

**フォントパス**: `/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf`（Railway環境で利用可能）

**出力形式**:
```json
[
  {
    "section": "hook",
    "duration": 3,
    "image_base64": "iVBORw0KGgoAAAANSUhEUg...",
    "filename": "slide_1_hook.png"
  },
  ...
]
```

**テスト手順**:
1. 手動でWebhookをトリガー
2. 生成された7枚の画像を確認
3. テキスト配置、フォント、色を検証

---

### Phase 4b: FAL Image-to-Video（2🍅）

#### n8nワークフロー構成

```yaml
Node 1: Loop Over Items
  - 入力: Phase 4aの7枚の画像URL
  - 各画像に対して処理

Node 2: Set - Prepare FAL Request
  - image_url: {{$json.image_url}}
  - duration: {{$json.duration}}
  - motion_prompt: {{$json.motion_prompt}}
  - section: {{$json.section}}

Node 3: HTTP Request - FAL Submit
  - URL: https://fal.run/fal-ai/stable-video-diffusion
  - Method: POST
  - Authentication: Header Auth
    - Name: Authorization
    - Value: Key {{$credentials.fal_api_key}}
  - Body (JSON):
    {
      "image_url": "={{$json.image_url}}",
      "motion_bucket_id": 127,
      "cond_aug": 0.02,
      "num_frames": "={{$json.duration * 8}}",
      "num_inference_steps": 25,
      "fps": 8,
      "seed": "={{Math.floor(Math.random() * 1000000)}}",
      "prompt": "={{$json.motion_prompt}}"
    }
  - 出力: request_id

Node 4: Wait
  - Duration: 10秒
  - 理由: FALのレンダリング開始待ち

Node 5: Loop - Check Status
  - Condition: {{$json.status}} !== "succeeded" AND {{$runIndex}} < 30
  - HTTP Request - Get Status:
    - URL: https://fal.run/fal-ai/stable-video-diffusion/{{$json.request_id}}
    - Method: GET
    - Authentication: 同上
  - Wait Between Checks: 10秒
  - 最大試行: 30回（5分）

Node 6: IF - Check Success
  - Condition: {{$json.status}} === "succeeded"
  - True: Extract Video URL
  - False: Error Handler

Node 7: Extract Video URL
  - video_url: {{$json.video.url}}
  - section: {{$json.section}}
  - duration: {{$json.duration}}

Node 8: Aggregate
  - 7本の動画URLを配列に結合
  - 順序保持
```

#### 認証設定（FAL API）

**n8n Credentials設定**:
```yaml
Credential Type: Header Auth
Name: FAL API Key
Header Name: Authorization
Header Value: Key YOUR_FAL_API_KEY
```

**テスト手順**:
1. FAL.ai API認証テスト完了後、Credentialsに登録
2. 1枚の画像で動画生成テスト
3. ステータスポーリングの動作確認
4. 7枚すべての動画生成テスト

---

### Phase 4c: FFmpeg結合（1🍅）

#### n8nワークフロー構成

```yaml
Node 1: Aggregate Videos
  - 入力: Phase 4bの7本の動画URL配列
  - 順序確認（hook→intro→point1-3→summary→cta）

Node 2: Code Node (Python) - FFmpeg Concat
  - 機能: 7本の動画をダウンロード → 結合
  - 出力: 1本の完成動画（ローカルファイル）

Node 3: HTTP Request - Upload to Google Drive
  - 完成動画をGoogle Driveにアップロード
  - 出力: final_video_url

Node 4: HTTP Request - Update Notion DB
  - Database: WF7_Scripts
  - Update: status = "completed"
  - Add: final_video_url

Node 5: Webhook Response
  - 成功メッセージを返す

Node 6: Trigger Phase 5
  - Phase 5（SNS投稿）ワークフローを起動
```

#### Pythonコード実装（Node 2）

**実装場所**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/phase4c_ffmpeg_concat.py`

**主要機能**:
- requests で動画ダウンロード
- filelist.txt作成
- ffmpeg -f concat 実行
- 一時ファイルのクリーンアップ

**タイムアウト設定**: 600秒（コミット `213f551` で確立）

**FFmpegコマンド**:
```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

**テスト手順**:
1. 7本のテスト動画URLを用意
2. ダウンロード→結合の動作確認
3. 完成動画の品質チェック
4. ファイルサイズ・秒数の検証

---

## 🧪 E2Eテスト計画（1🍅）

### テストケース

#### 1. 正常系テスト

```yaml
シナリオ: LINE登録誘導動画の生成
手順:
  1. Phase 2-3で台本生成（status = approved）
  2. Phase 4a実行 → 7枚の画像確認
  3. Phase 4b実行 → 7本の動画確認
  4. Phase 4c実行 → 1本の完成動画確認
  5. Phase 5実行 → SNS投稿確認

期待結果:
  ✅ 60-90秒の完成動画
  ✅ テキストが正確に配置
  ✅ 動きが自然
  ✅ スムーズな結合
```

#### 2. 品質確認

```yaml
確認項目:
  - テキスト可読性（フォント、色、サイズ）
  - 動きの自然さ（ズーム、スライド、フェード）
  - 結合の滑らかさ（トランジション）
  - 音声なし（Phase 3で追加予定）
  - ファイルサイズ（<50MB推奨）
```

#### 3. 異常系テスト

```yaml
テストケース:
  1. FAL API タイムアウト → リトライ確認
  2. FFmpeg失敗 → エラーハンドリング確認
  3. Google Drive アップロード失敗 → 再試行確認
  4. Notion DB更新失敗 → ログ確認
```

---

## 📝 実装チェックリスト

### 🔧 環境準備

- [x] Railway n8nデプロイ成功
- [x] FFmpeg + Noto Sans JPフォント インストール
- [ ] FAL API アカウント作成
- [ ] FAL API Key取得
- [ ] n8n Credentials登録（FAL API Key）

### 📋 Phase 2-3修正

- [ ] Notion DBスキーマ更新（新規カラム追加）
- [ ] ChatGPTプロンプトにSTEP11追加
- [ ] テスト台本生成で確認

### 🎨 Phase 4a実装

- [x] S0: ベースワークフローバックアップ完了（`workflows/archive/wf7phase4_v3_backup_20251108.json`）
- [x] S1-1: Notion DBスキーマ確認完了（デフォルト値対応済み）
- [x] S1-2: Phase4a Code Node用コード準備完了（`workflows/wf7-video-renderer/phase4a_code_node.py`）
- [x] S1-統合ガイド作成完了（`docs/implementation/WF7-Phase4a-integration-guide.md`）
- [x] S1-MCP実装手順作成完了（`docs/implementation/WF7-Phase4a-MCP実装手順.md`）
- [x] S1-手動実装手順書作成完了（`docs/implementation/WF7-Phase4a-手動実装手順.md`）
- [x] S1-MCPエラー対処法作成完了（`docs/implementation/WF7-Phase4a-MCPエラー対処法.md`）
- [ ] S1-3: n8n UI/MCPでCode Node追加（「データ統合」ノード後に配置）
  - **実装方法**: n8n UIで手動実装（`docs/implementation/WF7-Phase4a-手動実装手順.md`を参照）
  - **MCPツールのエラー**: `n8n_update_partial_workflow`で「Invalid request: request/body must NOT have additional properties」エラーが発生
  - **対処法**: 手動実装を推奨（`docs/implementation/WF7-Phase4a-MCPエラー対処法.md`を参照）
  - **改善案実行結果**:
    - ✅ MCPツールバージョンアップ完了（2.22.11）
    - ❌ 段階的実装はn8nの制約により不可（接続のないノードは許可されない）
    - ❌ continueOnErrorモードも不可
    - **結論**: MCPツールでの自動実装は現時点では困難。手動実装を推奨
  - [ ] Code Node追加: `Code - Generate Slides with Pillow`
  - [ ] Pythonコード設定: `workflows/wf7-video-renderer/phase4a_code_node.py`の内容をコピー
  - [ ] 接続設定: `データ統合` → `Code - Generate Slides with Pillow`
- [ ] S1-4: Split Outノード実装（スライド用）
  - [ ] Split Outノード追加: `Split Out - Slides`
  - [ ] 接続設定: `Code - Generate Slides with Pillow` → `Split Out - Slides`
- [ ] S1-5: Google Drive Upload実装（各スライド画像）
  - [ ] Google Drive Uploadノード追加: `Google Drive - Upload Slide Image`
  - [ ] base64デコード処理追加（Code NodeまたはBinary Data変換）
  - [ ] 接続設定: `Split Out - Slides` → `Google Drive - Upload Slide Image`
- [ ] S1-6: Aggregateノード実装（7枚の画像URL統合）
  - [ ] Aggregateノード追加: `Aggregate - Combine All Slides`
  - [ ] 接続設定: `Google Drive - Upload Slide Image` → `Aggregate - Combine All Slides`
- [ ] S1-7: Set - Phase4a Payloadノード実装（Phase4b用データ整形）
  - [ ] Setノード追加: `Set - Phase4a Payload`
  - [ ] データ整形設定: `slides_metadata`配列を作成
  - [ ] 接続設定: `Aggregate - Combine All Slides` → `Set - Phase4a Payload`
- [ ] S1-8: 7枚の画像生成テスト
  - [ ] Code Node単体テスト
  - [ ] Google Driveアップロード確認
  - [ ] `slides_metadata`出力確認

### 🎬 Phase 4b実装

- [x] S2-1: 既存ワークフローのバックアップ完了（`mcp__n8n-mcp__n8n_get_workflow`で取得済み）
- [x] S2-2: Phase4b統合指示書作成完了（`docs/implementation/WF7-Phase4b-integration-instructions.md`）
- [x] S2-3: n8n MCPでPhase4b呼び出しノード追加完了（`HTTP Request - Call Phase4b`）
  - **実装方法**: `n8n_update_full_workflow`を使用して実装
  - **Webhook URL**: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video`
  - **入力**: `{ script_id, slides_metadata }`
  - **出力**: `{ success, script_id, videos_metadata, videos_count, total_duration }`
- [x] S2-4: Set - Phase4b Payloadノード実装完了（出力データ整形）
- [x] S2-5: IF - Phase4b Success Checkノード実装完了（成功判定）
- [x] S2-6: エラーハンドリングノード実装完了（Phase4b失敗時の処理）
- [x] S2-7: 接続変更完了（`IF - Phase4a Success Check`のTrue分岐をPhase4b呼び出しに変更）
- [ ] S2-8: 既存FAL処理ブロックの削除（Phase4c実装後に実施）
- [ ] S2-9: 7本の動画生成テスト

### 🎞️ Phase 4c実装

- [x] S3-1: Phase4c実装手順書作成完了（`docs/implementation/WF7-Phase4c-実装手順.md`）
- [ ] S3-2: Code - Phase4c FFmpeg Concatノード追加（手動実装）
- [ ] S3-3: Code - Read Video Binaryノード追加（手動実装）
- [ ] S3-4: Google Drive - Upload Final Videoノード追加（手動実装）
- [ ] S3-5: Notion - Update Script Recordノード追加（手動実装）
- [ ] S3-6: Code - Cleanup Temp Filesノード追加（手動実装）
- [ ] S3-7: Respond to Webhookノード接続（手動実装）
- [ ] S3-8: 既存FAL処理ブロックの削除（動作確認後）
- [ ] S3-9: 完成動画生成テスト

### 🧪 E2Eテスト

- [ ] 正常系テスト（LINE登録誘導動画）
- [ ] 品質確認（テキスト、動き、結合）
- [ ] 異常系テスト（エラーハンドリング）
- [ ] パフォーマンステスト（処理時間）

---

## 🚀 実装スケジュール

### Day 1: 環境準備 + Phase 4a実装（2🍅）

```yaml
午前（1🍅）:
  - FAL API アカウント作成
  - API Key取得
  - n8n Credentials設定
  - Phase 2-3修正（Notion DB + プロンプト）

午後（1🍅）:
  - Phase 4a n8nワークフロー実装
  - Pillowスクリプト実装
  - テスト画像生成
```

### Day 2: Phase 4b実装（2🍅）

```yaml
午前（1🍅）:
  - FAL API統合実装
  - ポーリングロジック実装

午後（1🍅）:
  - 7本の動画生成テスト
  - 品質確認
  - エラーハンドリング実装
```

### Day 3: Phase 4c実装（1🍅）

```yaml
午前-午後（1🍅）:
  - FFmpeg結合スクリプト実装
  - n8n統合
  - 完成動画生成テスト
```

### Day 4: E2Eテスト（1🍅）

```yaml
終日（1🍅）:
  - 正常系テスト
  - 品質確認
  - 異常系テスト
  - パフォーマンステスト
  - ドキュメント作成
```

---

## ⚠️ リスクと対策

### リスク1: FAL API レート制限

```yaml
リスク内容:
  - 同時に7本の動画生成でレート制限に引っかかる可能性

影響度: 中
発生確率: 低

対策:
  1. 順次処理（1本ずつ生成）
  2. Wait時間の調整（10秒 → 15秒）
  3. リトライロジックの実装
```

### リスク2: FFmpeg処理時間

```yaml
リスク内容:
  - 7本の動画結合に時間がかかりタイムアウト

影響度: 中
発生確率: 低

対策:
  1. タイムアウト延長（600秒設定済み）
  2. シンプルな結合方式（-c copy）を使用
  3. トランジション効果は後回し
```

### リスク3: Notion DB更新失敗

```yaml
リスク内容:
  - 完成動画URLが記録されない

影響度: 低
発生確率: 低

対策:
  1. リトライロジックの実装
  2. エラーログの保存
  3. 手動更新の手順書作成
```

---

## 💰 コスト・工数まとめ

### コスト比較

| 項目 | Creatomate | FAL.ai | 削減効果 |
|------|-----------|---------|----------|
| 月額基本料金 | 推定 $50-100/月 | $0 | $50-100/月 |
| レンダリング単価 | 推定 $1-2/本 | $0.56/本 | 44-72% |
| 月間70本の場合 | $120-240/月 | $39.20/月 | **70-84%削減** |

### 工数見積もり

```yaml
Phase 4a: 2🍅（32分）
Phase 4b: 2🍅（32分）
Phase 4c: 1🍅（16分）
E2Eテスト: 1🍅（16分）
合計: 6🍅（約1.6時間）
```

---

## 📚 関連ドキュメント

- [Phase4-FAL移行-要件定義.md](../Phase4-FAL移行-要件定義.md)
- [Phase4-判断ゲート決定記録.md](../Phase4-判断ゲート決定記録.md)
- [WF7-Phase4-FAL実装変更点.md](../WF7-Phase4-FAL実装変更点.md)
- [n8n-workflow-construction-knowledge.md](../knowledge/n8n-workflow-construction-knowledge.md)
- [WF7-Phase4a-手動実装手順.md](./WF7-Phase4a-手動実装手順.md) - **Phase4a実装時の参照先（推奨）**
- [WF7-Phase4a-MCPエラー対処法.md](./WF7-Phase4a-MCPエラー対処法.md) - MCPツールエラーの対処法
- [WF7-Phase4a-integration-guide.md](./WF7-Phase4a-integration-guide.md)
- [WF7-Phase4a-MCP実装手順.md](./WF7-Phase4a-MCP実装手順.md)
- [WF7-Phase4b-integration-instructions.md](./WF7-Phase4b-integration-instructions.md) - **Phase4b統合時の参照先（推奨）**
- [WF7-Phase4c-実装手順.md](./WF7-Phase4c-実装手順.md) - **Phase4c実装時の参照先（推奨）**

---

## 📝 変更履歴

| 日付 | バージョン | 変更内容 | 担当者 |
|------|-----------|---------|--------|
| 2025-11-06 | 1.0 | 初版作成 | Claude Code (Sonnet 4.5) |
| 2025-11-08 | 1.1 | Phase4a手動実装手順書追加、チェックリスト詳細化 | Claude Code (Composer) |
| 2025-11-08 | 1.2 | Phase4b統合指示書追加、S2進捗更新 | Claude Code (Composer) |
| 2025-11-08 | 1.3 | Phase4b統合完了（n8n MCPで実装） | Claude Code (Composer) |
| 2025-11-08 | 1.4 | Phase4c実装手順書作成完了 | Claude Code (Composer) |

---

**作成**: Claude Code (Sonnet 4.5)
**合計工数**: 6🍅（約1.6時間）
**コスト削減**: 70-84%削減
**実装難易度**: 中（3段階処理だが、各ステップは単純）
