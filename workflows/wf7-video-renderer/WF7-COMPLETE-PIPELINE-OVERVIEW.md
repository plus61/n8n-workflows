# WF7 SNS動画生成パイプライン - 完全プロセス概要

**作成日**: 2025-11-01
**バージョン**: 1.0
**目的**: WF7全Phase連携による動画生成プロセスの完全可視化

---

## 🎯 概要

WF7は、note記事のトピックから短編SNS動画(ショート動画・リール)を自動生成する5段階パイプラインです。

### パイプライン全体像

```
WF6(記事生成)
    ↓
[Phase1] 台本整形 → script.json
    ↓
[Phase2] 素材取得 → assets.json + 画像ダウンロード
    ↓
[Phase3] 音声・字幕生成 → audio.mp3 + subtitle.srt (オプション)
    ↓
[Phase4] 動画レンダリング → video.mp4 + thumbnail.jpg
    ↓
[Phase5] メタデータ登録 → Notion動画データベース登録
```

### 生成される動画の特徴

- **長さ**: 30-60秒のショート動画
- **形式**: MP4 (1080x1920 縦型)
- **構成要素**:
  - 視覚素材: Pexels/Unsplash画像
  - テキストオーバーレイ: 台本テキスト
  - 音声ナレーション: OpenAI TTS (オプション)
  - 字幕: SRT形式 (オプション)

---

## 📋 Phase詳細分析

### Phase1: SNS動画台本整形

**Workflow ID**: `fqbULAMXIGyBkNtL`
**Status**: Active

#### 🔹 入力

| データ | 取得元 | 形式 |
|--------|--------|------|
| articleId | WF6 Webhook | String |
| notionPageId | WF6 Webhook | String |
| topic | WF6 Webhook | String |
| generatedContent | WF6 Webhook | String |

**Webhook URL**: `POST /webhook/wf7-phase1-script`

#### 🔹 処理フロー

```
1. WF6完了Webhook
   ↓
2. 入力データ整形
   - articleId, topic, contentを抽出
   ↓
3. GPTペイロード作成
   - システムプロンプト: SNS動画台本生成
   - ユーザープロンプト: トピック + 記事内容
   ↓
4. GPT API呼び出し (GPT-4)
   - 30-60秒の動画台本生成
   - シーン分割 (3-5シーン)
   - 各シーンに画像タグ付与
   ↓
5. スクリプトJSON解析
   - GPTレスポンスをJSON形式に変換
   ↓
6. Notionペイロード作成
   ↓
7. Notion API呼び出し
   - 動画制作ステータス: "台本完成"
   ↓
8. ScriptJSON生成
   - script.json フォーマット作成
   ↓
9. Slack通知
   ↓
10. Respond to Webhook
```

#### 🔹 出力

| データ | 保存先 | 形式 | 内容 |
|--------|--------|------|------|
| script.json | メモリ内 | JSON | シーン配列、各シーンにテキスト・タイミング・画像タグ |
| notionPageId | Notion | Property | 更新されたページID |
| articleId | 次Phase | String | 記事識別子 |

**script.json構造例**:
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "今日は○○について紹介します",
      "duration": 3.5,
      "imageTag": "business meeting"
    },
    {
      "id": 2,
      "text": "まず最初のポイントは...",
      "duration": 4.0,
      "imageTag": "office workspace"
    }
  ],
  "totalDuration": 45,
  "title": "○○の完全ガイド"
}
```

---

### Phase2: 素材取得

**Workflow ID**: `sGjN9Vqw4pGTLmaX`
**Status**: Active

#### 🔹 入力

| データ | 取得元 | 形式 |
|--------|--------|------|
| articleId | Phase1 | String |
| notionPageId | Phase1 | String |
| script | Phase1 | JSON |

**Webhook URL**: `POST /webhook/wf7-phase2-assets`

#### 🔹 処理フロー

```
1. WF7-Phase2 Webhook
   ↓
2. アセットタグ抽出
   - script.jsonから各シーンのimageTagを抽出
   - タグリスト生成
   ↓
3. 各タグに対して:
   a) Pexels検索
      ↓
   b) Pexelsレスポンス処理
      ↓
   c) Pexels成功判定
      - 成功: 素材ダウンロード
      - 失敗: Unsplashフォールバック
   ↓
4. 素材ダウンロード
   - 高解像度画像取得 (1080x1920推奨)
   ↓
5. アセットメタ整形
   - ファイルパス、URL、解像度記録
   ↓
6. 結果統合
   - 全シーンの素材を統合
   ↓
7. AssetsJSON生成
   - assets.json フォーマット作成
   ↓
8. Notionペイロード作成
   ↓
9. Notionページ更新
   - assetsJson プロパティに保存
   - 動画制作ステータス: "素材取得完了"
   ↓
10. Respond to Webhook
```

#### 🔹 出力

| データ | 保存先 | 形式 | 内容 |
|--------|--------|------|------|
| assets.json | Notion Property | JSON | 各シーンの画像URL・メタデータ |
| 画像ファイル | /tmp/wf7/assets/ | JPG/PNG | ダウンロードした画像 |

**assets.json構造例**:
```json
{
  "assets": [
    {
      "sceneId": 1,
      "imageUrl": "https://images.pexels.com/photos/123/...",
      "localPath": "/tmp/wf7/assets/scene1.jpg",
      "width": 1080,
      "height": 1920,
      "source": "pexels",
      "photographer": "John Doe"
    },
    {
      "sceneId": 2,
      "imageUrl": "https://images.unsplash.com/photo-456/...",
      "localPath": "/tmp/wf7/assets/scene2.jpg",
      "width": 1080,
      "height": 1920,
      "source": "unsplash",
      "photographer": "Jane Smith"
    }
  ]
}
```

---

### Phase3: 音声・字幕生成 (オプション)

**Workflow ID**: `KkiF386PmAVaY1mA`
**Status**: Active

#### 🔹 入力

| データ | 取得元 | 形式 |
|--------|--------|------|
| articleId | Phase2 | String |
| notionPageId | Phase2 | String |
| script | Phase1 (Notion) | JSON |
| needsNarration | リクエスト | Boolean |

**Webhook URL**: `POST /webhook/wf7-phase3-audio`

#### 🔹 処理フロー

```
1. WF7-Phase3 Webhook
   ↓
2. 音声必要性判定
   - needsNarration = false → スキップ
   - needsNarration = true → 音声生成
   ↓
3. ナレーション抽出
   - script.jsonから各シーンのテキスト抽出
   - フルナレーション原稿作成
   ↓
4. OpenAI TTS音声生成
   - モデル: tts-1
   - 音声: alloy/echo/fable/onyx/nova/shimmer
   - 形式: MP3
   ↓
5. 音声ファイル保存
   - ローカルパス: /tmp/wf7/audio/{articleId}.mp3
   ↓
6. 音声メタデータ保存
   - ファイルサイズ、長さ記録
   ↓
7. SRT字幕生成
   - タイムコード付き字幕作成
   - script.jsonのdurationベース
   ↓
8. 字幕ファイル保存
   - ローカルパス: /tmp/wf7/subtitles/{articleId}.srt
   ↓
9. 字幕メタデータ保存
   ↓
10. Notionペイロード作成
    - voiceFileUrl生成 (File Server URL)
    - subtitleFileUrl生成 (File Server URL)
    ↓
11. Notionページ更新
    - 動画制作ステータス: "音声・字幕完成"
    ↓
12. Respond to Webhook
```

#### 🔹 出力

| データ | 保存先 | 形式 | 内容 |
|--------|--------|------|------|
| audio.mp3 | /tmp/wf7/audio/ | MP3 | OpenAI TTS生成音声 |
| subtitle.srt | /tmp/wf7/subtitles/ | SRT | タイムコード付き字幕 |
| voiceFileUrl | Notion | String | File Server URL (query param形式) |
| subtitleFileUrl | Notion | String | File Server URL (query param形式) |

**File Server URL形式** (Railway対応):
```
voiceFileUrl: https://xxx.up.railway.app/webhook/wf7-files-audio?articleId=xxx
subtitleFileUrl: https://xxx.up.railway.app/webhook/wf7-files-subtitle?articleId=xxx
```

**subtitle.srt構造例**:
```srt
1
00:00:00,000 --> 00:00:03,500
今日は○○について紹介します

2
00:00:03,500 --> 00:00:07,500
まず最初のポイントは...

3
00:00:07,500 --> 00:00:12,000
次に重要なのが...
```

---

### Phase4: 動画レンダリング

**Workflow ID**: `VF3kFwJLKVq990jn`
**Status**: Active

#### 🔹 入力

| データ | 取得元 | 形式 |
|--------|--------|------|
| articleId | Phase3 | String |
| notionPageId | Phase3 | String |
| scriptUrl | File Server | URL (query param) |
| assetsUrl | File Server | URL (query param) |
| subtitleUrl | File Server | URL (query param, optional) |
| templateId | リクエスト | String |

**Webhook URL**: `POST /webhook/wf7-phase4-render`

**重要**: scriptUrl, assetsUrlは**File Server経由**で取得
- scriptUrl: `https://xxx.up.railway.app/webhook/wf7-files-script?articleId=xxx`
- assetsUrl: `https://xxx.up.railway.app/webhook/wf7-files-assets?articleId=xxx`

#### 🔹 処理フロー

```
1. WF7-Phase4 Webhook
   ↓
2. 入力データ解析
   - articleId, scriptUrl, assetsUrl検証
   ↓
3. レンダリングリクエスト構築
   - jobId生成
   - renderRequest作成
   ↓
4. 並列処理:
   a) script.json ダウンロード
      - File Server GETリクエスト
      ↓
      script.json 保存
      - /tmp/wf7/scripts/{articleId}.json

   b) assets.json ダウンロード
      - File Server GETリクエスト
      ↓
      assets.json 保存
      - /tmp/wf7/render/{articleId}_assets.json
   ↓
5. 動画レンダリング実行
   - Python実行: python /app/render_video.py
   - 引数: article-id, script-path, assets-path
   - 処理:
     * script.jsonとassets.jsonを読み込み
     * 各シーンに画像配置
     * テキストオーバーレイ追加
     * シーン遷移エフェクト適用
     * 音声トラック追加 (optional)
     * 字幕追加 (optional)
     * MP4エンコード (1080x1920)
   - 出力:
     * /tmp/wf7/videos/{articleId}.mp4
     * /tmp/wf7/thumbnails/{articleId}.jpg
   ↓
6. 動画メタデータ抽出
   - ファイルサイズ、長さ、解像度取得
   - videoUrl生成 (File Server URL)
   - thumbUrl生成 (File Server URL)
   ↓
7. Notionペイロード作成
   ↓
8. Notionページ更新
   - videoUrl, thumbUrl保存
   - 動画制作ステータス: "レンダリング完了"
   ↓
9. Respond to Webhook
```

#### 🔹 レンダリング処理詳細

**Pythonスクリプト処理** (`render_video.py`):
1. script.json読み込み → シーン情報取得
2. assets.json読み込み → 画像パス取得
3. 各シーンに対して:
   - 画像読み込み (PIL/OpenCV)
   - リサイズ: 1080x1920 (9:16縦型)
   - テキストオーバーレイ追加:
     * フォント: Noto Sans JP
     * サイズ: 48-72px
     * 位置: 画面下部 (字幕エリア避ける)
     * 背景: 半透明黒 (視認性向上)
   - シーン長さ: script.durationに従う
4. シーン結合:
   - MoviePy/FFmpeg使用
   - フェードイン/アウトエフェクト
   - シーン間トランジション
5. 音声トラック追加 (optional):
   - audio.mp3を動画と同期
6. 字幕追加 (optional):
   - subtitle.srtをバーンイン
7. MP4エンコード:
   - コーデック: H.264
   - ビットレート: 5-8Mbps
   - フレームレート: 30fps
8. サムネイル生成:
   - 最初のシーンから抽出
   - サイズ: 1080x1920 → 540x960 (縮小)

#### 🔹 出力

| データ | 保存先 | 形式 | 内容 |
|--------|--------|------|------|
| video.mp4 | /tmp/wf7/videos/ | MP4 | 完成動画 (1080x1920, 30-60秒) |
| thumbnail.jpg | /tmp/wf7/thumbnails/ | JPG | 動画サムネイル |
| videoUrl | Notion | String | File Server URL (query param形式) |
| thumbUrl | Notion | String | File Server URL (query param形式) |

**File Server URL形式**:
```
videoUrl: https://xxx.up.railway.app/webhook/wf7-files-video?articleId=xxx
thumbUrl: https://xxx.up.railway.app/webhook/wf7-files-thumbnail?articleId=xxx
```

---

### Phase5: メタデータ登録・連携

**Workflow ID**: `0CK4yaBsipa1UgSz`
**Status**: Active

#### 🔹 入力

| データ | 取得元 | 形式 |
|--------|--------|------|
| articleId | Phase4 | String |
| notionPageId | Phase4 | String |
| title | Phase4 | String |
| videoUrl | Phase4 | String |
| thumbUrl | Phase4 | String |

**Webhook URL**: `POST /webhook/wf7-phase5-metadata`

#### 🔹 処理フロー

```
1. WF7-Phase5 Webhook
   ↓
2. 入力データ解析
   - articleId, videoUrl, thumbUrl検証
   ↓
3. Notionペイロード構築
   - 動画データベース用ページ作成
   ↓
4. Notionページ作成
   - 動画タイトル
   - 動画URL
   - サムネイルURL
   - 公開ステータス: "未公開"
   ↓
5. Slackメッセージ構築 (disabled)
   ↓
6. Slack通知送信 (disabled)
   ↓
7. WF8ペイロード構築 (disabled)
   ↓
8. WF8Webhook送信 (disabled)
   ↓
9. Notionメタデータペイロード作成
   ↓
10. Notionメタデータ更新
    - 元記事ページのvideo_statusを更新
    - 動画制作ステータス: "完成"
    ↓
11. Respond to Webhook
```

#### 🔹 出力

| データ | 保存先 | 形式 | 内容 |
|--------|--------|------|------|
| 動画ページ | Notion動画DB | Page | 動画メタデータ一式 |
| video_status | Notion記事DB | Property | "完成" |

**Notion動画ページ構造**:
```json
{
  "properties": {
    "Title": { "title": "○○の完全ガイド" },
    "VideoURL": { "url": "https://xxx/webhook/wf7-files-video?articleId=xxx" },
    "ThumbnailURL": { "url": "https://xxx/webhook/wf7-files-thumbnail?articleId=xxx" },
    "Status": { "select": { "name": "未公開" } },
    "ArticleID": { "rich_text": "xxx" },
    "CreatedAt": { "date": { "start": "2025-11-01T12:00:00Z" } }
  }
}
```

---

## 🔄 Phase間データフロー完全図

```
┌─────────────────────────────────────────────────────────────────┐
│ WF6: note記事自動生成                                              │
│ Output: articleId, notionPageId, topic, generatedContent        │
└────────────────────────┬────────────────────────────────────────┘
                         │ Webhook POST
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase1: SNS動画台本整形                                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Input:                                                       │ │
│ │ - articleId, notionPageId, topic, generatedContent         │ │
│ │                                                              │ │
│ │ Process:                                                     │ │
│ │ 1. GPT-4でSNS動画台本生成 (30-60秒)                         │ │
│ │ 2. シーン分割 (3-5シーン)                                   │ │
│ │ 3. 各シーンに画像タグ付与                                   │ │
│ │ 4. script.json生成                                          │ │
│ │                                                              │ │
│ │ Output:                                                      │ │
│ │ - script.json (メモリ内)                                    │ │
│ │ - Notion更新: ステータス="台本完成"                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ 次Phaseトリガー
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase2: 素材取得                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Input:                                                       │ │
│ │ - articleId, notionPageId, script (from Notion)            │ │
│ │                                                              │ │
│ │ Process:                                                     │ │
│ │ 1. script.jsonから画像タグ抽出                              │ │
│ │ 2. 各タグでPexels検索 (失敗時Unsplash)                      │ │
│ │ 3. 高解像度画像ダウンロード (1080x1920)                     │ │
│ │ 4. assets.json生成                                          │ │
│ │                                                              │ │
│ │ Output:                                                      │ │
│ │ - assets.json (Notion Property)                            │ │
│ │ - 画像ファイル: /tmp/wf7/assets/*.jpg                       │ │
│ │ - Notion更新: ステータス="素材取得完了"                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ 次Phaseトリガー (optional)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase3: 音声・字幕生成 (オプション)                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Input:                                                       │ │
│ │ - articleId, notionPageId, script, needsNarration          │ │
│ │                                                              │ │
│ │ Process:                                                     │ │
│ │ 1. needsNarration判定                                       │ │
│ │ 2. OpenAI TTS音声生成 (MP3)                                 │ │
│ │ 3. SRT字幕生成 (タイムコード付き)                           │ │
│ │ 4. File Server URL生成                                      │ │
│ │                                                              │ │
│ │ Output:                                                      │ │
│ │ - audio.mp3: /tmp/wf7/audio/{articleId}.mp3               │ │
│ │ - subtitle.srt: /tmp/wf7/subtitles/{articleId}.srt        │ │
│ │ - voiceFileUrl (File Server URL - query param形式)         │ │
│ │ - subtitleFileUrl (File Server URL - query param形式)      │ │
│ │ - Notion更新: ステータス="音声・字幕完成"                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ 次Phaseトリガー
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ File Server (6 independent workflows)                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 1. Script Delivery: GET /webhook/wf7-files-script?articleId │ │
│ │ 2. Assets Delivery: GET /webhook/wf7-files-assets?articleId │ │
│ │ 3. Audio Delivery:  GET /webhook/wf7-files-audio?articleId  │ │
│ │ 4. Subtitle Delivery: GET /webhook/wf7-files-subtitle?...   │ │
│ │ 5. Video Delivery:  GET /webhook/wf7-files-video?articleId  │ │
│ │ 6. Thumbnail Delivery: GET /webhook/wf7-files-thumbnail?... │ │
│ │                                                              │ │
│ │ 特徴:                                                         │ │
│ │ - クエリパラメータ形式 (Railway対応)                         │ │
│ │ - articleId紐付けでファイル配信                              │ │
│ │ - バイナリファイル直接レスポンス                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ File Server経由データ取得
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase4: 動画レンダリング                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Input:                                                       │ │
│ │ - articleId, notionPageId                                   │ │
│ │ - scriptUrl (File Server URL)                               │ │
│ │ - assetsUrl (File Server URL)                               │ │
│ │ - subtitleUrl (File Server URL, optional)                   │ │
│ │                                                              │ │
│ │ Process:                                                     │ │
│ │ 1. File ServerからJSON/ファイルダウンロード                 │ │
│ │ 2. Python動画レンダリング実行:                              │ │
│ │    - 画像読み込み・リサイズ (1080x1920)                     │ │
│ │    - テキストオーバーレイ追加                                │ │
│ │    - シーン結合・トランジション                              │ │
│ │    - 音声トラック追加 (optional)                             │ │
│ │    - 字幕バーンイン (optional)                               │ │
│ │    - MP4エンコード (H.264, 30fps, 5-8Mbps)                  │ │
│ │ 3. サムネイル生成                                            │ │
│ │ 4. File Server URL生成                                       │ │
│ │                                                              │ │
│ │ Output:                                                      │ │
│ │ - video.mp4: /tmp/wf7/videos/{articleId}.mp4              │ │
│ │ - thumbnail.jpg: /tmp/wf7/thumbnails/{articleId}.jpg      │ │
│ │ - videoUrl (File Server URL - query param形式)              │ │
│ │ - thumbUrl (File Server URL - query param形式)              │ │
│ │ - Notion更新: ステータス="レンダリング完了"                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ 次Phaseトリガー
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase5: メタデータ登録・連携                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Input:                                                       │ │
│ │ - articleId, notionPageId, title, videoUrl, thumbUrl       │ │
│ │                                                              │ │
│ │ Process:                                                     │ │
│ │ 1. Notion動画データベースにページ作成                       │ │
│ │ 2. 動画メタデータ登録                                       │ │
│ │ 3. 元記事ページの動画ステータス更新                         │ │
│ │                                                              │ │
│ │ Output:                                                      │ │
│ │ - Notion動画ページ作成                                      │ │
│ │ - 元記事のvideo_status="完成"                               │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎬 生成される動画の詳細

### 動画仕様

| 項目 | 値 |
|------|-----|
| 解像度 | 1080x1920 (9:16縦型) |
| 長さ | 30-60秒 |
| フレームレート | 30fps |
| コーデック | H.264 |
| ビットレート | 5-8Mbps |
| 音声コーデック | AAC (optional) |
| ファイルサイズ | 8-15MB (目安) |

### 動画構成要素

#### 1. 視覚素材
- **画像**: Pexels/Unsplash高解像度画像
- **配置**: 各シーンに1枚
- **表示時間**: 3-5秒/シーン
- **エフェクト**: フェードイン/アウト、シーン遷移

#### 2. テキストオーバーレイ
- **フォント**: Noto Sans JP (日本語対応)
- **サイズ**: 48-72px
- **位置**: 画面下部 (字幕エリア避ける)
- **背景**: 半透明黒 (視認性向上)
- **アニメーション**: フェードイン/アウト

#### 3. 音声ナレーション (optional)
- **TTS**: OpenAI TTS-1
- **音声**: alloy/echo/fable/onyx/nova/shimmer
- **形式**: MP3
- **ビットレート**: 128kbps

#### 4. 字幕 (optional)
- **形式**: SRT (バーンイン)
- **フォント**: Noto Sans JP
- **サイズ**: 36-48px
- **位置**: 画面最下部
- **背景**: 黒帯 (視認性最大化)

### 動画例

**トピック**: "リモートワーク効率化ツール完全ガイド"

```
シーン1 (0:00-0:04)
  画像: オフィスのデスクトップPC
  テキスト: "リモートワークを快適にする5つのツール"

シーン2 (0:04-0:08)
  画像: ビデオ会議の様子
  テキスト: "まずはZoomで高品質な会議を"

シーン3 (0:08-0:12)
  画像: Slackの画面
  テキスト: "Slackでチーム連携をスムーズに"

シーン4 (0:12-0:16)
  画像: Notionダッシュボード
  テキスト: "Notionでプロジェクト管理を一元化"

シーン5 (0:16-0:20)
  画像: 笑顔でPCを操作する人
  テキスト: "これであなたも生産性UP!"
```

---

## 📊 システムアーキテクチャ

### コンポーネント図

```
┌─────────────────────────────────────────────────────────┐
│ n8n Instance (Railway Environment)                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ WF7 Phase1-5 (Main Pipeline)                     │  │
│  │ - Phase1: Webhook + GPT API                      │  │
│  │ - Phase2: Pexels/Unsplash API                    │  │
│  │ - Phase3: OpenAI TTS                             │  │
│  │ - Phase4: Python Script Execution                │  │
│  │ - Phase5: Notion API                             │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ File Server (6 Workflows)                        │  │
│  │ - Script Delivery (GET query param)              │  │
│  │ - Assets Delivery (GET query param)              │  │
│  │ - Audio Delivery (GET query param)               │  │
│  │ - Subtitle Delivery (GET query param)            │  │
│  │ - Video Delivery (GET query param)               │  │
│  │ - Thumbnail Delivery (GET query param)           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

External Dependencies:
- OpenAI API (GPT-4, TTS-1)
- Pexels API (Image search)
- Unsplash API (Image search fallback)
- Notion API (Database operations)
- Python Runtime (Video rendering)
```

### データストレージ

| データタイプ | 保存場所 | 保持期間 | アクセス方法 |
|------------|---------|---------|------------|
| script.json | Notion Property | 永続 | File Server Webhook |
| assets.json | Notion Property | 永続 | File Server Webhook |
| audio.mp3 | /tmp/wf7/audio/ | コンテナ再起動まで | File Server Webhook |
| subtitle.srt | /tmp/wf7/subtitles/ | コンテナ再起動まで | File Server Webhook |
| video.mp4 | /tmp/wf7/videos/ | コンテナ再起動まで | File Server Webhook |
| thumbnail.jpg | /tmp/wf7/thumbnails/ | コンテナ再起動まで | File Server Webhook |

**重要**: `/tmp/`配下のファイルはRailwayコンテナ再起動で消失するため、永続化が必要な場合は外部ストレージ(S3等)への移行を推奨。

---

## 🔧 環境変数・認証情報

### 必須環境変数

| 変数名 | 用途 | 設定場所 |
|--------|------|---------|
| OPENAI_API_KEY | GPT-4 API、TTS API | n8n Credentials |
| PEXELS_API_KEY | Pexels画像検索 | n8n Credentials |
| UNSPLASH_ACCESS_KEY | Unsplash画像検索 | n8n Credentials |
| NOTION_API_KEY | Notionデータベース操作 | n8n Credentials |
| NOTION_VIDEO_DB_ID | 動画データベースID | Phase5ワークフロー |
| SLACK_WEBHOOK_URL | Slack通知 (optional) | n8n Credentials |
| BASE_URL | File Server URL | 全Phase共通 |

### Notion認証情報

**Integration Token**:
- Integration名: n8n WF7 Integration
- 権限: Read content, Update content, Insert content
- 接続データベース:
  - note記事データベース (WF6)
  - 動画データベース (Phase5)

---

## 🚀 実行方法

### 完全パイプライン実行

#### 1. WF6記事生成完了時の自動実行

```bash
# WF6が自動的にPhase1をトリガー
# WF6 Webhook → Phase1 Webhook
# 必要なデータ: articleId, notionPageId, topic, generatedContent
```

#### 2. Phase1手動トリガー (テスト用)

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase1-script \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-001",
    "notionPageId": "page-id-xxx",
    "topic": "リモートワーク効率化ツール",
    "generatedContent": "リモートワークを効率化するための..."
  }'
```

#### 3. Phase2手動トリガー

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-001",
    "notionPageId": "page-id-xxx",
    "script": {
      "scenes": [
        {"id": 1, "text": "...", "imageTag": "business meeting"}
      ]
    }
  }'
```

#### 4. Phase3手動トリガー (音声あり)

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-001",
    "notionPageId": "page-id-xxx",
    "needsNarration": true
  }'
```

#### 5. Phase4手動トリガー

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-001",
    "notionPageId": "page-id-xxx",
    "scriptUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-script?articleId=test-001",
    "assetsUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-assets?articleId=test-001",
    "subtitleUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-subtitle?articleId=test-001",
    "templateId": "default"
  }'
```

#### 6. Phase5手動トリガー

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase5-metadata \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-001",
    "notionPageId": "page-id-xxx",
    "title": "リモートワーク効率化ツール完全ガイド",
    "videoUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-video?articleId=test-001",
    "thumbUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-thumbnail?articleId=test-001"
  }'
```

### File Server動作確認

```bash
# script.json取得
curl https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-script?articleId=test-001

# assets.json取得
curl https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-assets?articleId=test-001

# 動画ダウンロード
curl -O https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-video?articleId=test-001
```

---

## ⚠️ 既知の制限事項

### 1. Railway環境制限

**Webhook制限**:
- パスパラメータ (`:articleId`) 非対応
- クエリパラメータ (`?articleId=xxx`) のみ対応

**対処済み**: 全File Server WebhookをQuery Parameter形式に移行済み

**ファイルストレージ制限**:
- `/tmp/`ディレクトリはコンテナ再起動で消失
- 永続化が必要な場合は外部ストレージ(S3, Cloudflare R2等)を推奨

### 2. Phase4 Python実行環境

**現在の状態**:
- Railway環境にPythonランタイムが未インストール
- `python: not found` エラー発生

**対処方法**:
1. **Buildpack追加** (推奨):
   ```json
   {
     "build": {
       "builder": "PROCFILE"
     },
     "buildpacks": [
       "heroku/nodejs",
       "heroku/python"
     ]
   }
   ```

2. **Dockerfile使用** (代替):
   ```dockerfile
   FROM node:18
   RUN apt-get update && apt-get install -y python3 python3-pip
   RUN pip3 install moviepy pillow opencv-python
   ```

### 3. API制限

| サービス | 制限 | 対処法 |
|---------|------|--------|
| OpenAI GPT-4 | 10K requests/day | リクエスト数監視 |
| OpenAI TTS | 1M characters/month | 音声生成をオプション化済み |
| Pexels | 200 requests/hour | Unsplashフォールバック実装済み |
| Unsplash | 50 requests/hour | エラーハンドリング実装 |
| Notion | 3 requests/second | リトライロジック推奨 |

---

## 📈 パフォーマンス指標

### Phase別実行時間 (目安)

| Phase | 平均実行時間 | 主なボトルネック |
|-------|------------|---------------|
| Phase1 | 10-20秒 | GPT-4 API応答時間 |
| Phase2 | 15-30秒 | 画像検索・ダウンロード |
| Phase3 | 8-15秒 | OpenAI TTS生成 |
| Phase4 | 30-60秒 | 動画レンダリング処理 |
| Phase5 | 3-5秒 | Notion API |
| **合計** | **66-130秒** | Phase4が最大ボトルネック |

### 最適化の余地

1. **Phase2並列化**: 画像ダウンロードを並列実行 → 50%高速化
2. **Phase4 GPU利用**: MoviePy/FFmpeg GPU対応 → 30-40%高速化
3. **File Server CDN化**: Cloudflare R2 + CDN → レスポンス高速化

---

## 🔮 今後の拡張計画

### Phase6: SNS自動投稿 (未実装)

```
Phase5 → Phase6: SNS投稿
  ├─ YouTube Shorts投稿
  ├─ TikTok投稿
  ├─ Instagram Reels投稿
  └─ Twitter動画投稿
```

### Phase7: 動画分析・最適化 (未実装)

```
Phase5 → Phase7: 分析
  ├─ 視聴回数追跡
  ├─ エンゲージメント分析
  ├─ A/Bテスト最適化
  └─ レコメンデーション改善
```

### テンプレート機能強化

- 複数動画テンプレート対応
- カスタムフォント・カラー設定
- ブランドロゴ挿入
- BGM追加機能

---

## 📚 関連ドキュメント

- [WF7 File Server URL Migration Report](./wf7-file-server-url-migration-report.md)
- [Railway Webhook Persistence Test Report](../../docs/webhook-persistence-test-report.md)
- [n8n Workflow Construction Knowledge Base](../../docs/knowledge/n8n-workflow-construction-knowledge.md)
- [Workflow Backup Policy](../../docs/workflow-backup-policy.md)

---

**最終更新**: 2025-11-01
**バージョン**: 1.0
**作成者**: Claude Code with n8n-mcp
