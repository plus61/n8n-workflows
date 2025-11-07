# WF7 Phase 4c: n8nワークフロー実装ガイド

**作成日**: 2025-11-06
**バージョン**: 1.0
**目的**: FFmpeg動画結合ワークフローのn8n実装手順書

---

## 📋 概要

Phase 4cは、FAL.aiで生成された7本の動画を1本に結合し、Google Driveにアップロード、Notion DBを更新するワークフローです。

### 処理フロー

```
Phase 4bからの入力データ受信
  ↓
Python Code Node（phase4c_ffmpeg_concat.py実行）
  ↓
Google Drive Upload（完成動画をアップロード）
  ↓
Notion DB Update（動画URLと完成ステータスを更新）
  ↓
Cleanup Code Node（一時ファイル削除）
  ↓
Respond to Webhook（成功レスポンス）
```

### 入力

Phase 4bから以下のデータを受信:

```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.ai/files/xxx/video.mp4",
      "fal_video_id": "xxx",
      "filename": "video_1_hook.mp4"
    }
    // ... 6 more videos
  ]
}
```

### 出力

- **Google Drive**: 最終完成動画（約80秒、MP4）
- **Notion DB**: 完成動画URL、ステータス更新

---

## 🔧 ノード構成

### 1. Python Code Node - FFmpeg Concat

**ノード名**: `Code - Concat Videos with FFmpeg`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "python",
  "mode": "runOnceForAllItems",
  "pythonCode": "# phase4c_ffmpeg_concat.pyのコードをコピー\n\n# エントリーポイント\nresult = concat_videos(items[0]['json'])\nreturn [result]"
}
```

#### ⚠️ 重要な注意事項

1. **タイムアウト設定**: FFmpeg処理は最大600秒（10分）
   ```python
   timeout=600  # 10分タイムアウト
   ```

2. **Railway環境の依存関係**:
   - `ffmpeg`: プリインストール済み
   - `curl`: プリインストール済み
   - `subprocess`, `tempfile`: Python標準ライブラリ

3. **一時ファイル管理**:
   - `/tmp/wf7_phase4c_xxxxxx/` に一時保存
   - Google Driveアップロード後にクリーンアップ必要

4. **Google Drive URL変換**:
   ```python
   # https://drive.google.com/file/d/FILE_ID/view
   # → https://drive.google.com/uc?export=download&id=FILE_ID
   ```

#### 入力例

Phase 4bからの出力をそのまま使用:

```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.ai/files/xxx/video_hook.mp4",
      "fal_video_id": "fal_xxx_1",
      "filename": "video_1_hook.mp4"
    }
    // ... 6 more
  ]
}
```

#### 出力例

```json
{
  "success": true,
  "script_id": "29b68d5c-2986-817f-xxxx",
  "output_video_path": "/tmp/wf7_phase4c_abc123/final_video_29b68d5c_1699999999.mp4",
  "output_video_size": 15728640,
  "total_duration": 80,
  "videos_count": 7,
  "temp_dir": "/tmp/wf7_phase4c_abc123"
}
```

---

### 2. Google Drive Upload

**ノード名**: `Google Drive - Upload Final Video`
**ノードタイプ**: `n8n-nodes-base.googleDrive`

#### 設定

```json
{
  "operation": "upload",
  "name": "={{ 'WF7_Final_' + $json.script_id + '_' + $now.toFormat('yyyyMMdd_HHmmss') + '.mp4' }}",
  "binaryData": true,
  "binaryPropertyName": "data",
  "options": {
    "parents": ["WF7 Final Videos Folder ID"],
    "mimeType": "video/mp4"
  }
}
```

#### ⚠️ 前処理が必要

Google Drive Uploadノードはバイナリデータを必要とするため、前段でファイル読み込みが必要です。

**解決策1**: `Read Binary File` ノードを追加

```json
{
  "operation": "readBinaryFile",
  "filePath": "={{ $json.output_video_path }}"
}
```

**解決策2**: Code Nodeでbase64エンコード

```python
# phase4c_ffmpeg_concat.pyのconcat_videos()関数に追加
with open(output_path, 'rb') as f:
    video_binary = base64.b64encode(f.read()).decode()

result = {
    # ... 既存のフィールド
    "video_base64": video_binary
}
```

#### 出力例

```json
{
  "id": "1xyz...abc",
  "name": "WF7_Final_29b68d5c_20251106_153045.mp4",
  "mimeType": "video/mp4",
  "size": "15728640",
  "webViewLink": "https://drive.google.com/file/d/1xyz...abc/view",
  "webContentLink": "https://drive.google.com/uc?id=1xyz...abc&export=download"
}
```

---

### 3. Notion DB Update

**ノード名**: `Notion - Update Script Record`
**ノードタイプ**: `n8n-nodes-base.notion`

#### 設定

```json
{
  "resource": "databasePage",
  "operation": "update",
  "pageId": "={{ $('Code - Concat Videos with FFmpeg').item.json.script_id }}",
  "properties": {
    "Final Video URL": {
      "type": "url",
      "url": "={{ $json.webViewLink }}"
    },
    "Video Status": {
      "type": "select",
      "select": {
        "name": "完成"
      }
    },
    "Video Size (MB)": {
      "type": "number",
      "number": "={{ Math.round($('Code - Concat Videos with FFmpeg').item.json.output_video_size / 1024 / 1024 * 100) / 100 }}"
    },
    "Total Duration (sec)": {
      "type": "number",
      "number": "={{ $('Code - Concat Videos with FFmpeg').item.json.total_duration }}"
    },
    "Completed At": {
      "type": "date",
      "date": {
        "start": "={{ $now.toISO() }}"
      }
    }
  }
}
```

#### Notion DB事前準備

WF7 動画管理マスタに以下のプロパティを追加:

1. **Final Video URL** (URL型)
2. **Video Status** (Select型)
   - オプション: 未作成、進行中、完成、エラー
3. **Video Size (MB)** (Number型)
4. **Total Duration (sec)** (Number型)
5. **Completed At** (Date型)

---

### 4. Cleanup Code Node

**ノード名**: `Code - Cleanup Temp Files`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "python",
  "mode": "runOnceForAllItems",
  "pythonCode": "import shutil\nimport os\n\ntemp_dir = items[0]['json'].get('temp_dir')\n\nif temp_dir and os.path.exists(temp_dir):\n    try:\n        shutil.rmtree(temp_dir)\n        print(f'🧹 一時ファイル削除完了: {temp_dir}')\n        return [{'cleanup_success': True, 'temp_dir': temp_dir}]\n    except Exception as e:\n        print(f'⚠️ 一時ファイル削除エラー: {e}')\n        return [{'cleanup_success': False, 'error': str(e)}]\nelse:\n    print('⚠️ temp_dirが見つかりません')\n    return [{'cleanup_success': False, 'error': 'temp_dir not found'}]"
}
```

#### 説明

FFmpegで使用した一時ファイル（7本の動画 + concat.txt）を削除し、Railwayディスク容量を節約します。

---

### 5. Respond to Webhook

**ノード名**: `Respond to Webhook - Success`
**ノードタイプ**: `n8n-nodes-base.respondToWebhook`

#### 設定

```json
{
  "respondWith": "json",
  "responseBody": "={{ JSON.stringify({ success: true, script_id: $('Code - Concat Videos with FFmpeg').item.json.script_id, final_video_url: $('Google Drive - Upload Final Video').item.json.webViewLink, video_size_mb: Math.round($('Code - Concat Videos with FFmpeg').item.json.output_video_size / 1024 / 1024 * 100) / 100, total_duration: $('Code - Concat Videos with FFmpeg').item.json.total_duration, notion_updated: true }) }}"
}
```

#### レスポンス例

```json
{
  "success": true,
  "script_id": "29b68d5c-2986-817f-xxxx",
  "final_video_url": "https://drive.google.com/file/d/1xyz...abc/view",
  "video_size_mb": 15.0,
  "total_duration": 80,
  "notion_updated": true
}
```

---

## 🧪 テスト手順

### 1. 単体テスト（Python Code Nodeのみ）

#### ローカルテスト

```bash
cd /Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer

# サンプル動画を用意（7本）
mkdir -p test_videos
# 実際のテスト動画をダウンロードまたは作成

python phase4c_ffmpeg_concat.py
```

#### Railway環境テスト

```bash
# Railwayコンソールで実行
python /app/workflows/wf7-video-renderer/phase4c_ffmpeg_concat.py
```

### 2. FFmpegテスト

```bash
# FFmpegが利用可能か確認
ffmpeg -version

# concat.txt作成
cat > /tmp/concat.txt << EOF
file '/tmp/video1.mp4'
file '/tmp/video2.mp4'
file '/tmp/video3.mp4'
EOF

# FFmpeg結合テスト
ffmpeg -y -safe 0 -f concat -i /tmp/concat.txt -c copy /tmp/output.mp4
```

### 3. n8n統合テスト

#### Step 1: Phase 4b完了後のデータで実行

Phase 4bのWebhookレスポンスをそのままPhase 4cに渡してテスト。

#### Step 2: Code Node単独実行

n8n UIで「Code - Concat Videos with FFmpeg」ノードを手動実行:

期待結果:
- ✅ 7本の動画がダウンロードされる
- ✅ FFmpegで1本に結合される
- ✅ 出力ファイルが `/tmp/` に作成される

#### Step 3: Google Drive Upload確認

- ✅ 完成動画がGoogle Driveにアップロードされる
- ✅ ファイル名が正しい（`WF7_Final_xxx.mp4`）
- ✅ 動画サイズが約15-20MB

#### Step 4: Notion DB更新確認

- ✅ Final Video URLが設定される
- ✅ Video Statusが「完成」になる
- ✅ Video Size、Total Durationが正しい

#### Step 5: Cleanup確認

- ✅ `/tmp/wf7_phase4c_xxx/` ディレクトリが削除される

---

## ⚠️ エラーハンドリング

### 1. FFmpegタイムアウト

**エラー**: `subprocess.TimeoutExpired`

**対処**: タイムアウト時間を延長

```python
# phase4c_ffmpeg_concat.pyで調整
timeout=900  # 15分に延長
```

**原因分析**:
- 動画ファイルサイズが大きい（各3-5MB × 7本 = 21-35MB）
- Railwayのディスク I/O が遅い

### 2. ダウンロード失敗

**エラー**: `curl: Failed to connect`

**対処**: リトライロジック追加

```python
def download_video_with_retry(video_url, output_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            if download_video(video_url, output_path):
                return True
            print(f"⚠️ リトライ {attempt + 1}/{max_retries}")
            time.sleep(5)
        except Exception as e:
            print(f"❌ ダウンロードエラー（試行{attempt + 1}）: {e}")
    return False
```

### 3. Google Drive Quota Exceeded

**エラー**: `User rate limit exceeded`

**対処**: ノード設定でリトライ有効化

```json
{
  "retryOnFail": true,
  "maxTries": 5,
  "waitBetweenTries": 10000
}
```

### 4. 一時ファイル容量不足

**エラー**: `No space left on device`

**対処**: Railwayディスク容量を確認

```bash
df -h /tmp
```

Railwayの `/tmp` は512MB制限:
- 7本の動画（各3-5MB） = 21-35MB
- 完成動画（15-20MB） = 15-20MB
- **合計約40-55MB** → 512MBの約10% → 問題なし

もし不足する場合は、処理後すぐに削除:

```python
# 各動画ダウンロード後すぐにFFmpegに渡し、ダウンロード元を削除
```

---

## 📊 パフォーマンス指標

### 目標値

- **処理時間**: <120秒（ダウンロード60秒 + FFmpeg60秒）
- **メモリ使用**: <200MB
- **ディスク使用**: <60MB（一時ファイル）
- **成功率**: 95%+

### 実測値の取得方法

n8n UIの「Execution Time」パネルで確認:

```
Code - Concat Videos with FFmpeg: ~90s
  - ダウンロード: ~50s (7本 × 7s)
  - FFmpeg結合: ~40s
Google Drive Upload: ~20s
Notion Update: ~2s
Cleanup: <1s
Total: ~113s
```

### FFmpeg処理時間の最適化

**現在**: `-c copy`（再エンコードなし、高速）

**代替案**: 再エンコード（品質統一、サイズ削減）

```bash
ffmpeg -y -safe 0 -f concat -i concat.txt \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4
```

再エンコード時の処理時間: 約180-240秒（現在の4-6倍）

**推奨**: 初期実装は `-c copy` を使用、品質問題があれば再エンコード検討

---

## 🔐 セキュリティ

### 1. 一時ファイルのクリーンアップ

**必須**: 処理完了後は必ず一時ファイルを削除

```python
# エラー発生時もクリーンアップ
try:
    result = concat_videos(input_data)
finally:
    cleanup_temp_files(temp_dir)
```

### 2. Google Drive権限

**推奨**: サービスアカウント使用
- 最小権限の原則（`drive.file` scope のみ）
- WF7専用フォルダへのアクセス制限

---

## 📝 次のステップ

Phase 4c完了後、以下を実施:

1. ✅ **Todo #10完了**: FFmpeg結合スクリプト作成完了
2. ✅ **Todo #11完了**: n8nワークフロー実装ガイド作成完了
3. ⏳ **Todo #12**: Phase 4c完成動画生成テスト実施
4. ⏳ **Todo #13**: E2Eテスト（Phase 2-3 → 4a → 4b → 4c → Phase 5）

---

## 📌 Phase 4 全体の統合

### Phase 4a → 4b → 4c データフロー

```yaml
Phase 4a (スライド生成):
  Input: Notion DB Record ID
  Output: 7枚の画像 + メタデータ

Phase 4b (FAL I2V):
  Input: Phase 4aの出力
  Output: 7本の動画 + メタデータ

Phase 4c (FFmpeg結合):
  Input: Phase 4bの出力
  Output: 1本の完成動画 + Notion DB更新
```

### Phase 4 統合Webhook

最終的には3つのフェーズを1つのWebhookでトリガー:

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-full-pipeline \
  -H "Content-Type: application/json" \
  -d '{"script_id": "29b68d5c-2986-817f-xxxx"}'
```

n8nワークフロー設計:

```
Webhook
  ↓
Phase 4a Webhook Call
  ↓
Wait for Phase 4a Complete
  ↓
Phase 4b Webhook Call
  ↓
Wait for Phase 4b Complete
  ↓
Phase 4c Webhook Call
  ↓
Final Response
```

---

**作成者**: Claude Code (Sonnet 4.5)
**更新日**: 2025-11-06
**関連ドキュメント**:
- WF7-Phase4-FAL実装計画書.md
- phase4c_ffmpeg_concat.py
- WF7-Phase4a-n8nワークフロー実装ガイド.md
