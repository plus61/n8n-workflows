# WF7 Phase4c実装手順書

**作成日**: 2025-11-08
**目的**: Phase4c（FFmpeg動画結合）のn8nワークフロー実装手順
**対象ワークフロー**: WF7 Phase4 - V3 Fixed (ID: qSN7EHj5yl0nPXij)

---

## 📋 実装概要

Phase4cでは、Phase4bで生成された7本の動画をFFmpegで結合し、Google Driveにアップロード、Notion DBを更新します。

### 処理フロー

```
IF - Phase4b Success Check (True)
  ↓
Code - Phase4c FFmpeg Concat
  ↓
Code - Read Video Binary
  ↓
Google Drive - Upload Final Video
  ↓
Notion - Update Script Record
  ↓
Code - Cleanup Temp Files
  ↓
Respond to Webhook
```

---

## 🔧 実装手順

### Step 1: Phase4c Code Node追加

**ノード名**: `Code - Phase4c FFmpeg Concat`
**ノードタイプ**: `n8n-nodes-base.code`
**typeVersion**: `2`
**位置**: X座標: `-1136`, Y座標: `-128`

**設定内容**:

1. **Language**: `Python`
2. **Mode**: `Run Once for All Items`
3. **Code**: 以下のPythonコードをコピー

```python
import subprocess
import os
import tempfile
import time

def download_video(video_url, output_path):
    try:
        if "drive.google.com" in video_url:
            if "/file/d/" in video_url:
                file_id = video_url.split("/file/d/")[1].split("/")[0]
                video_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        result = subprocess.run(
            ["curl", "-L", "-o", output_path, video_url],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 0:
                return True
        return False
    except Exception as e:
        return False

def create_concat_file(video_paths, concat_file_path):
    with open(concat_file_path, 'w', encoding='utf-8') as f:
        for video_path in video_paths:
            f.write(f"file '{video_path}'\n")

def concat_videos_with_ffmpeg(video_paths, output_path, timeout=600):
    try:
        concat_file = os.path.join(os.path.dirname(output_path), 'concat.txt')
        create_concat_file(video_paths, concat_file)
        cmd = [
            'ffmpeg',
            '-y',
            '-safe', '0',
            '-f', 'concat',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0 and os.path.exists(output_path):
            if os.path.exists(concat_file):
                os.remove(concat_file)
            return True
        return False
    except Exception as e:
        return False

input_data = items[0]['json']
script_id = input_data.get('script_id', 'unknown')
videos_metadata = input_data.get('videos_metadata', [])

if len(videos_metadata) != 7:
    raise ValueError(f"動画数が不正です。期待: 7本、実際: {len(videos_metadata)}本")

temp_dir = tempfile.mkdtemp(prefix='wf7_phase4c_')
downloaded_paths = []

for i, video_meta in enumerate(videos_metadata, 1):
    section = video_meta.get('section', f'video_{i}')
    video_url = video_meta.get('video_url')
    if not video_url:
        raise ValueError(f"動画URL未設定: section={section}")
    video_filename = f"video_{i}_{section}.mp4"
    video_path = os.path.join(temp_dir, video_filename)
    if not download_video(video_url, video_path):
        raise RuntimeError(f"動画ダウンロード失敗: {section}")
    downloaded_paths.append(video_path)

output_filename = f"final_video_{script_id}_{int(time.time())}.mp4"
output_path = os.path.join(temp_dir, output_filename)

if not concat_videos_with_ffmpeg(downloaded_paths, output_path):
    raise RuntimeError("FFmpeg結合失敗")

output_size = os.path.getsize(output_path)
total_duration = sum(v.get('duration', 0) for v in videos_metadata)

return [{
    'json': {
        'success': True,
        'script_id': script_id,
        'output_video_path': output_path,
        'output_video_size': output_size,
        'total_duration': total_duration,
        'videos_count': len(videos_metadata),
        'temp_dir': temp_dir,
        'articleId': input_data.get('articleId')
    }
}]
```

**接続**:
- 入力: `IF - Phase4b Success Check` (True分岐)
- 出力: `Code - Read Video Binary`

---

### Step 2: 動画ファイル読み込みCode Node追加

**ノード名**: `Code - Read Video Binary`
**ノードタイプ**: `n8n-nodes-base.code`
**typeVersion**: `2`
**位置**: X座標: `-912`, Y座標: `-128`

**設定内容**:

1. **Language**: `Python`
2. **Mode**: `Run Once for All Items`
3. **Code**: 以下のPythonコードをコピー

```python
import base64

output_video_path = items[0]['json']['output_video_path']

with open(output_video_path, 'rb') as f:
    video_binary = f.read()
    video_base64 = base64.b64encode(video_binary).decode('utf-8')

return [{
    'json': items[0]['json'],
    'binary': {
        'data': video_base64
    }
}]
```

**接続**:
- 入力: `Code - Phase4c FFmpeg Concat`
- 出力: `Google Drive - Upload Final Video`

---

### Step 3: Google Driveアップロードノード追加

**ノード名**: `Google Drive - Upload Final Video`
**ノードタイプ**: `n8n-nodes-base.googleDrive`
**typeVersion**: `3`
**位置**: X座標: `-688`, Y座標: `-128`

**設定内容**:

1. **Operation**: `Upload`
2. **Name**: `={{ 'WF7_Final_' + $json.script_id + '_' + $now.toFormat('yyyyMMdd_HHmmss') + '.mp4' }}`
3. **Binary Data**: `true`
4. **Binary Property Name**: `data`
5. **Options**:
   - **MIME Type**: `video/mp4`

**Credentials**: Google Drive OAuth2 API (既存の資格情報を使用)

**接続**:
- 入力: `Code - Read Video Binary`
- 出力: `Notion - Update Script Record`

---

### Step 4: Notion更新ノード追加

**ノード名**: `Notion - Update Script Record`
**ノードタイプ**: `n8n-nodes-base.notion`
**typeVersion**: `2`
**位置**: X座標: `-464`, Y座標: `-128`

**設定内容**:

1. **Resource**: `Database Page`
2. **Operation**: `Update`
3. **Page ID**: `={{ $('Code - Phase4c FFmpeg Concat').item.json.script_id }}`
4. **Properties**:
   - **Status**: `VideoReady` (Select型)
   - **Video URL**: `={{ $json.webViewLink }}` (URL型)
   - **Video Size (MB)**: `={{ Math.round($('Code - Phase4c FFmpeg Concat').item.json.output_video_size / 1024 / 1024 * 100) / 100 }}` (Number型)
   - **Total Duration (sec)**: `={{ $('Code - Phase4c FFmpeg Concat').item.json.total_duration }}` (Number型)

**Credentials**: Notion API (既存の資格情報を使用)

**接続**:
- 入力: `Google Drive - Upload Final Video`
- 出力: `Code - Cleanup Temp Files`

---

### Step 5: 一時ファイルクリーンアップCode Node追加

**ノード名**: `Code - Cleanup Temp Files`
**ノードタイプ**: `n8n-nodes-base.code`
**typeVersion**: `2`
**位置**: X座標: `-240`, Y座標: `-128`

**設定内容**:

1. **Language**: `Python`
2. **Mode**: `Run Once for All Items`
3. **Code**: 以下のPythonコードをコピー

```python
import shutil
import os

temp_dir = items[0]['json'].get('temp_dir')

if temp_dir and os.path.exists(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        return [{'json': {'cleanup_success': True, 'temp_dir': temp_dir}}]
    except Exception as e:
        return [{'json': {'cleanup_success': False, 'error': str(e)}}]
else:
    return [{'json': {'cleanup_success': False, 'error': 'temp_dir not found'}}]
```

**接続**:
- 入力: `Notion - Update Script Record`
- 出力: `Respond to Webhook`

---

### Step 6: Webhook応答ノード接続

**ノード名**: `Respond to Webhook`
**ノードタイプ**: `n8n-nodes-base.respondToWebhook`
**typeVersion**: `1.1`
**位置**: X座標: `-16`, Y座標: `-128`

**設定内容**:

1. **Respond With**: `JSON`
2. **Response Body**: 以下のJSONを設定

```json
{
  "success": true,
  "script_id": "={{ $('Code - Phase4c FFmpeg Concat').item.json.script_id }}",
  "final_video_url": "={{ $('Google Drive - Upload Final Video').item.json.webViewLink }}",
  "video_size_mb": "={{ Math.round($('Code - Phase4c FFmpeg Concat').item.json.output_video_size / 1024 / 1024 * 100) / 100 }}",
  "total_duration": "={{ $('Code - Phase4c FFmpeg Concat').item.json.total_duration }}",
  "notion_updated": true
}
```

**接続**:
- 入力: `Code - Cleanup Temp Files`
- 出力: (Webhook応答)

---

### Step 7: 既存処理の削除（オプション）

Phase4c実装後、既存のFAL処理ブロック（`Split Out`以降）は不要になりますが、動作確認後に削除することを推奨します。

**削除対象ノード**:
- `Split Out`
- `Driveファイル情報取得`
- `メタデータ整形`
- `ペイロード構築`
- `Submit to FAL`
- `Fetch Status`
- `Wait for Processing`
- `Check Render Status`
- `Render Completed?`
- `Get Image Result URL`
- `Download Image`
- `DriveへUL`
- `レスポンスデータ準備`
- `Notion更新` (既存)
- `レスポンスデータ復元`
- `Respond to Webhook` (既存)
- `Retry Counter`
- `Check Retry Limit`
- `Wait Before Retry`
- `Timeout Error Response`

---

## 🧪 テスト手順

### 1. 単体テスト

1. Phase4b完了後のデータで`Code - Phase4c FFmpeg Concat`ノードを手動実行
2. 7本の動画がダウンロードされ、結合されることを確認
3. 出力ファイルが`/tmp/wf7_phase4c_xxx/`に作成されることを確認

### 2. 統合テスト

1. Phase4b完了後のWebhookをトリガー
2. Phase4cが正常に実行されることを確認
3. Google Driveに完成動画がアップロードされることを確認
4. Notion DBが更新されることを確認
5. Webhook応答が返されることを確認

### 3. エラーハンドリングテスト

1. 動画URLが無効な場合のエラー処理を確認
2. FFmpeg結合失敗時のエラー処理を確認
3. Google Driveアップロード失敗時のエラー処理を確認

---

## ⚠️ 注意事項

1. **タイムアウト設定**: Code Nodeのタイムアウトを600秒（10分）に設定
2. **一時ファイル管理**: 処理完了後は必ず一時ファイルを削除
3. **エラーハンドリング**: 各ステップでエラーが発生した場合の処理を実装
4. **Notion DBスキーマ**: 以下のプロパティが存在することを確認
   - `Status` (Select型)
   - `Video URL` (URL型)
   - `Video Size (MB)` (Number型)
   - `Total Duration (sec)` (Number型)

---

## 📝 実装チェックリスト

- [ ] Step 1: Phase4c Code Node追加
- [ ] Step 2: 動画ファイル読み込みCode Node追加
- [ ] Step 3: Google Driveアップロードノード追加
- [ ] Step 4: Notion更新ノード追加
- [ ] Step 5: 一時ファイルクリーンアップCode Node追加
- [ ] Step 6: Webhook応答ノード接続
- [ ] Step 7: 既存処理の削除（オプション）
- [ ] 単体テスト実施
- [ ] 統合テスト実施
- [ ] エラーハンドリングテスト実施

---

**作成者**: Claude Code (Composer)
**更新日**: 2025-11-08
**関連ドキュメント**:
- `WF7-Phase4-FAL実装計画書.md`
- `phase4c_ffmpeg_concat.py`
- `WF7-Phase4b-integration-instructions.md`

