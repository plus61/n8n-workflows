# WF7 SNS動画自動生成パイプライン - アーキテクチャマップ

**作成日**: 2025-11-13
**目的**: WF7の正しいフロー構成を明確化し、認識ギャップを解消する

---

## 📊 WF7 全体フロー概要

```
Phase1 (台本生成)
    ↓
Phase2 (画像素材取得)
    ↓
Phase3 (音声・字幕生成) [オプション]
    ↓
Phase4 (動画レンダリング)
    ↓ Phase4a (スライド生成)
    ↓ Phase4b (画像→動画変換)
    ↓ Phase4c (動画連結)
    ↓
Phase5 (メタデータ登録・連携)
```

---

## 🔹 Phase 1: AI台本生成

### ワークフロー情報
- **Workflow ID**: `pIj6S24Qg7O501PX`
- **名前**: "WF6: note記事自動生成（AI）" ※名前は誤解を招くが、実際はWF7 Phase1として機能
- **ステータス**: ✅ Active
- **ノード数**: 10
- **最終更新**: 2025-11-13T02:43:48.919Z

### エンドポイント
```
POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase1-notion-script-generator
```

### 入力データ形式
```json
{
  "pageId": "Notion page ID"
}
```

### 出力データ
Notion pageに以下のプロパティを書き込む:
- `hook`: フック（導入）
- `introduction`: イントロダクション
- `mainPoint1`: メインポイント1
- `mainPoint2`: メインポイント2
- `mainPoint3`: メインポイント3
- `summary`: まとめ
- `callToAction`: CTA（行動喚起）

### 実行例
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase1-notion-script-generator \
  -H "Content-Type: application/json" \
  -d '{"pageId": "1a0471d0b5d08023b55bdb1ed5f0c01a"}'
```

---

## 🔹 Phase 2: 画像素材取得

### ワークフロー情報
- **Workflow ID**: `HrYFB54nhsPy5QPB`
- **名前**: "WF7 Phase2: 素材取得_google版"
- **ステータス**: ✅ Active
- **ノード数**: 19
- **最終更新**: 2025-11-05T07:59:08.235Z

### エンドポイント
```
[要確認] - ワークフロー詳細取得が必要
```

### 入力データ形式
```json
{
  "pageId": "Notion page ID"
}
```

### 出力データ
Notion pageのスライド毎に画像URLを登録（Cloudinary等）

---

## 🔹 Phase 3: 音声・字幕生成（オプション）

### ワークフロー情報
- **Workflow ID**: `4Oo5LL3KMKVn8gUJ`
- **名前**: "WF7 Phase3: 音声・字幕生成(オプション)"
- **ステータス**: ✅ Active
- **ノード数**: 14
- **最終更新**: 2025-11-08T03:33:30.387Z

### エンドポイント
```
[要確認] - ワークフロー詳細取得が必要
```

### 入力データ形式
```json
{
  "pageId": "Notion page ID"
}
```

### 出力データ
- 音声ファイル（ElevenLabs TTS）
- 字幕データ（SRT/VTT形式）

---

## 🔹 Phase 4: 動画レンダリング

Phase4は3つのサブフェーズに分割されています。

### Phase 4 Orchestrator（親フロー）

#### ワークフロー情報
- **Workflow ID**: `B9edfrjMAboVbnec`
- **名前**: "WF7 Phase4 Simplified Orchestrator"
- **ステータス**: ✅ Active
- **ノード数**: 13
- **最終更新**: 2025-11-12T06:53:21.539Z

#### 役割
Phase4a, 4b, 4cを順次実行するオーケストレーター

#### エンドポイント
```
[要確認] - ワークフロー詳細取得が必要
```

---

### Phase 4a: スライド生成（画像準備）

#### ワークフロー情報
- **Workflow ID**: `LYPbvJfkMzLlhc6t`
- **名前**: "WF7 Phase4a - Slide Generator"
- **ステータス**: ✅ Active
- **ノード数**: 10
- **最終更新**: 2025-11-12T07:00:57.476Z

#### 役割
Notion pageから各スライドの画像URLとテキストを抽出し、Phase4bへ渡すペイロードを生成

#### エンドポイント
```
POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-phase4a-slide-generator
```

#### 入力データ形式
```json
{
  "pageId": "Notion page ID"
}
```

#### 出力データ形式
```json
{
  "slides": [
    {
      "section": "hook",
      "text": "フックテキスト",
      "image_url": "https://...",
      "duration": 3
    },
    {
      "section": "intro",
      "text": "イントロテキスト",
      "image_url": "https://...",
      "duration": 10
    }
    // ... 7スライド分
  ]
}
```

---

### Phase 4b: 画像→動画変換（単一動画生成）

#### ワークフロー情報
- **Workflow ID**: `hfhZijyKIt1DjI1V`
- **名前**: "WF7 Phase4b - Single Video Generator (FIXED)"
- **ステータス**: ✅ 本番稼働（2025-11-12修正完了）
- **ノード数**: 12
- **最終更新**: 2025-11-12T10:33:20.303Z
- **API**: FAL Compose API (`/fal-ai/ffmpeg-api/compose`)

#### 修正履歴
**2025-11-12修正**: Duration単位の問題を修正
- **修正前**: 秒単位で送信 → 1x1px, 0.04秒の動画が生成される
- **修正後**: ミリ秒単位に変換（`* 1000`） → 1920x1080, 正確な秒数の動画生成
- **詳細**: `/docs/implementation/WF7-Phase4b-FAL-Duration-Fix.md`

#### トリガー
Execute Workflow Trigger（親ワークフローから呼び出し専用）

#### 入力データ形式
```json
{
  "slide_metadata": {
    "section": "hook",
    "text": "フックテキスト",
    "image_url": "https://...",
    "duration": 3,
    "motion_prompt": "..."
  },
  "script_id": "test-id",
  "slide_index": 0
}
```

#### 出力データ形式
```json
{
  "section": "hook",
  "duration": 3,
  "video_url": "https://v3b.fal.media/files/.../output.mp4",
  "fal_request_id": "...",
  "motion_prompt": "...",
  "filename": "video_1_hook.mp4",
  "text": "フックテキスト",
  "slide_index": 0,
  "script_id": "test-id"
}
```

#### 動画仕様
- **解像度**: 1920x1080
- **時間**: 入力duration通り（秒単位、ミリ秒に自動変換）
- **フレームレート**: 30fps
- **フォーマット**: MP4

---

### ⚠️ Phase 4b 代替案（未デプロイ）

以下のワークフローは作成されたが未デプロイ（既存の`hfhZijyKIt1DjI1V`が正常動作するため不要）:

- `TIioKx4bEaWYe3OF` - "WF7 Phase4b - Image to Video Generator (Luma Ray 2 Flash)" - **未アクティブ**
  - API: FAL Luma Ray 2 Flash (image-to-video)
  - 作成日: 2025-11-13
  - 状態: 代替案として作成されたが、既存のComposeベース版が正常動作するため使用不要

---

### Phase 4c: 動画連結（最終動画生成）

#### ワークフロー情報
- **Workflow ID**: `mfRdJJFJRKmeBjKv`
- **名前**: "WF7 Phase4c - Video Concatenator (Merge Videos API)"
- **ステータス**: ✅ Active
- **ノード数**: 11
- **最終更新**: 2025-11-13T01:13:11.508Z

#### エンドポイント
```
POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-phase4c-video-concatenator
```

#### 入力データ形式
```json
{
  "pageId": "script_id",
  "videos": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://v3b.fal.media/files/.../video1.mp4",
      "text": "フックテキスト"
    },
    {
      "section": "intro",
      "duration": 10,
      "video_url": "https://v3b.fal.media/files/.../video2.mp4",
      "text": "イントロテキスト"
    }
    // ... 7本の動画
  ]
}
```

#### 出力データ形式
```json
{
  "success": true,
  "script_id": "test-id",
  "final_video_url": "https://v3b.fal.media/files/.../merged_video.mp4",
  "total_duration": 60,
  "video_count": 7,
  "status": "COMPLETED"
}
```

#### テスト結果
- ✅ 7本の動画（合計60秒）を正常に連結
- ✅ FAL `/merge-videos` APIを使用
- ✅ 実行時間: 約12秒

---

## 🔹 Phase 5: メタデータ登録・連携

### ワークフロー情報
- **Workflow ID**: `nplNGERT86PfYt6v`
- **名前**: "WF7 Phase5: メタデータ登録・連携"
- **ステータス**: ✅ Active
- **ノード数**: 11
- **最終更新**: 2025-11-03T05:09:29.608Z

### エンドポイント
```
[要確認] - ワークフロー詳細取得が必要
```

### 入力データ形式
```json
{
  "pageId": "Notion page ID",
  "final_video_url": "https://..."
}
```

### 出力データ
Notion pageの「最終動画URL」プロパティに動画URLを登録

---

## 🚫 存在しないワークフロー

以下のワークフローIDは**存在しません**（MCPが誤って返すが、n8n UIには存在しない）:

- ❌ `hxlKuJkYP68LN6wy` - "WF7 Phase2-3-4-5 統合フロー"
  - 原因: 削除されたワークフローのキャッシュ、または誤ったID
  - 対策: 各Phaseを個別に実行すること

---

## 📋 アーカイブ済み・非推奨ワークフロー

以下のワークフローは**使用しないこと**:

### Phase4 旧バージョン
- `dv9EGt12bsGlmo6J` - "WF7 Phase4: 動画レンダリング (Improved with Async Polling)2" - Archived
- `xvlnFeJJwHKMHBwK` - "WF7 Phase4: 動画レンダリング (Async Polling)" - Archived
- `SDO8X6oR5W5y2s6A` - "WF7 Phase4 - V2 Fixed" - Archived
- `3vcAVkofjJeEuUJx` - "WF7 Phase4 - V2 Fixed" - Archived
- `qSN7EHj5yl0nPXij` - "WF7 Phase4 - V3 Fixed_old" - Archived
- `RXCoQkQ0JCRGg8wR` - "WF7 Phase4 - V3 Fixed" - Archived
- `r9Sp5n0mkUCcH8cw` - "WF7 Phase4 - V3 Fixed_final" - Archived
- `7XkTMfUxG4y7KEzc` - "WF7 Phase4: 動画レンダリング (Improved with Async Polling)" - Archived

### Phase4b 旧バージョン
- `wHaKi98mTlUvFIOR` - "WF7 Phase4b - Image to Video" - Archived
- `EKttZfIOld4S4s5a` - "WF7 Phase4b - Image to Video (Cloudinary Slideshow)" - Archived
- `yyR10x16t0OdhIjG` - "WF7 Phase4b - Image to Video (Cloudinary Slideshow)" - Inactive

### Phase4ab 統合版（廃止）
- `rg4bT7i7YyvXtl0l` - "WF7 Phase4ab - Integrated (Slide Generator + Image to Video)" - Archived

### Phase4c 旧バージョン
- `chPw11OY5sex6d9I` - "WF7 Phase4c - Video Concatenator" - Inactive（26ノード版、compose API使用）

### テスト用ワークフロー
- `0SI8qdISZ087GEj0` - "WF7-TEST: FFmpeg Async Polling Test" - Archived
- `cYTkm8H2Qw3uDWcc` - "WF7 Phase4: 動画レンダリング (Test with Mock Data)" - Archived

---

## 🔧 補助サービス

### File Server ワークフロー群

これらはWF7の生成したファイルを配信するためのWebhook:

- `begM0Y848sOmKl8l` - "WF7 File Server" - Active
- `6THdoVz1tt94EmO7` - "WF7 File Server: Script Delivery" - Active
- `eKP2krAa0JW8lgA4` - "WF7 File Server: Assets Delivery" - Active
- `jq0zK4bddgFKuoY4` - "WF7 File Server: Audio Delivery" - Active
- `OmL0qWaXyT5wOVUg` - "WF7 File Server: Subtitle Delivery" - Active
- `uS3HUKrMtGIlHyu1` - "WF7 File Server: Thumbnail Delivery" - Active
- `rmo3ez37uHbSYKEC` - "WF7 File Server: Video Delivery" - Active

---

## ✅ 推奨実行フロー

### 1. 完全テスト（Phase1から開始）

```bash
# Step 1: Notion テストページ作成
# (手動 or Notion API)

# Step 2: Phase1 実行（台本生成）
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase1-notion-script-generator \
  -H "Content-Type: application/json" \
  -d '{"pageId": "YOUR_NOTION_PAGE_ID"}'

# Step 3: Phase2 実行（画像素材取得）
# [エンドポイント要確認]

# Step 4: Phase3 実行（音声・字幕生成）[オプション]
# [エンドポイント要確認]

# Step 5: Phase4 Orchestrator 実行（動画レンダリング）
# [エンドポイント要確認]
# 内部でPhase4a→4b→4cを順次実行

# Step 6: Phase5 実行（メタデータ登録）
# [エンドポイント要確認]
```

### 2. 部分テスト（Phase4のみ）

既存のNotionページ（Phase1-3完了済み）を使用:

```bash
# Phase4a: スライド生成
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"pageId": "YOUR_NOTION_PAGE_ID"}'

# Phase4b: 各スライドを動画化（7回繰り返し）
# [新ワークフローデプロイ後]

# Phase4c: 動画連結
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-phase4c-video-concatenator \
  -H "Content-Type: application/json" \
  -d @test-payload.json
```

---

## 🔍 次のアクション

### 緊急対応が必要
1. ✅ Phase4b新ワークフローのデプロイ（Luma Ray 2 Flash版）
   - ファイル: `now/2025-11-13_phase4b-image-to-video-workflow.json`

### 情報確認が必要
2. ⏳ Phase2のWebhook エンドポイント確認
3. ⏳ Phase3のWebhook エンドポイント確認
4. ⏳ Phase4 OrchestratorのWebhook エンドポイント確認
5. ⏳ Phase5のWebhook エンドポイント確認

### テスト実行
6. ⏳ Phase1実行テスト（既に成功）
7. ⏳ Phase2単独テスト
8. ⏳ Phase3単独テスト
9. ⏳ Phase4完全テスト（4a→4b→4c）
10. ⏳ Phase5単独テスト
11. ⏳ WF7全体統合テスト

---

## 📝 ドキュメント管理

このドキュメントは以下の場所で管理されています:

- **作業中**: `now/2025-11-13_wf7-architecture-map.md`
- **最終版**: `docs/design/WF7-Architecture-Map.md` (整理後に移動予定)

---

**最終更新**: 2025-11-13
**レビュアー**: Claude Code
**ステータス**: 初版作成完了、エンドポイント情報の追加が必要
