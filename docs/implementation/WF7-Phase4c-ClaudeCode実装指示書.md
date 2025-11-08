# WF7 Phase4c Claude Code実装指示書

**作成日**: 2025-11-08  
**対象**: Claude Code (Composer)  
**目的**: Phase4c（FFmpeg動画結合）のn8nワークフロー実装を自動化  
**対象ワークフロー**: WF7 Phase4 - V3 Fixed (ID: `qSN7EHj5yl0nPXij`)

---

## 📋 実装概要

### 目的
Phase4bで生成された7本の動画をFFmpegで結合し、Google Driveにアップロード、Notion DBを更新するPhase4c処理を実装する。

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

### 現在の状況
- ✅ Phase4a: 実装完了（Workflow ID: `LYPbvJfkMzLlhc6t`）
- ✅ Phase4b: 実装完了（Workflow ID: `wHaKi98mTlUvFIOR`）
- ⏳ Phase4c: 実装待ち（本指示書に基づき実装）

### 課題
- n8n-mcpツールの`n8n_update_partial_workflow`でエラーが発生（`request/body must NOT have additional properties`）
- 代替アプローチとして、ワークフローJSONを直接編集して更新する方法を採用

---

## 🔧 実装アプローチ

### 方法1: ワークフローJSON直接編集（推奨）

1. **ワークフローJSONを取得**
   ```bash
   mcp_n8n-mcp_n8n_get_workflow({id: "qSN7EHj5yl0nPXij"})
   ```

2. **JSONを編集**
   - 新しいノードを`nodes`配列に追加
   - 接続を`connections`オブジェクトに追加
   - 既存接続を更新

3. **ワークフローを更新**
   ```bash
   mcp_n8n-mcp_n8n_update_full_workflow({
     id: "qSN7EHj5yl0nPXij",
     nodes: [...],
     connections: {...}
   })
   ```

### 方法2: 段階的実装（フォールバック）

各ノードを1つずつ追加し、接続を段階的に更新する。

---

## 📝 実装手順（詳細）

### Step 0: 準備

1. **現在のワークフローを取得**
   ```javascript
   const workflow = await mcp_n8n-mcp_n8n_get_workflow({
     id: "qSN7EHj5yl0nPXij"
   });
   ```

2. **バックアップを作成**
   - 取得したワークフローJSONを`workflows/archive/wf7phase4_v3_before_phase4c_YYYYMMDD.json`に保存

3. **既存ノードの確認**
   - `IF - Phase4b Success Check`ノードのIDを確認: `if-phase4b-success-node`
   - 現在のTrue分岐接続先: `Split Out` (ID: `6c179b70-9314-467c-902a-757abd79755b`)

---

### Step 1: Code - Phase4c FFmpeg Concatノードの追加

**ノード仕様**:
```json
{
  "id": "code-phase4c-ffmpeg-concat",
  "name": "Code - Phase4c FFmpeg Concat",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [-1136, -128],
  "parameters": {
    "language": "python",
    "mode": "runOnceForAllItems",
    "pythonCode": "import subprocess\nimport os\nimport tempfile\nimport time\n\ndef download_video(video_url, output_path):\n    try:\n        if \"drive.google.com\" in video_url:\n            if \"/file/d/\" in video_url:\n                file_id = video_url.split(\"/file/d/\")[1].split(\"/\")[0]\n                video_url = f\"https://drive.google.com/uc?export=download&id={file_id}\"\n        result = subprocess.run(\n            [\"curl\", \"-L\", \"-o\", output_path, video_url],\n            capture_output=True,\n            text=True,\n            timeout=60\n        )\n        if result.returncode == 0 and os.path.exists(output_path):\n            file_size = os.path.getsize(output_path)\n            if file_size > 0:\n                return True\n        return False\n    except Exception as e:\n        return False\n\ndef create_concat_file(video_paths, concat_file_path):\n    with open(concat_file_path, 'w', encoding='utf-8') as f:\n        for video_path in video_paths:\n            f.write(f\"file '{video_path}'\\n\")\n\ndef concat_videos_with_ffmpeg(video_paths, output_path, timeout=600):\n    try:\n        concat_file = os.path.join(os.path.dirname(output_path), 'concat.txt')\n        create_concat_file(video_paths, concat_file)\n        cmd = [\n            'ffmpeg',\n            '-y',\n            '-safe', '0',\n            '-f', 'concat',\n            '-i', concat_file,\n            '-c', 'copy',\n            output_path\n        ]\n        result = subprocess.run(\n            cmd,\n            capture_output=True,\n            text=True,\n            timeout=timeout\n        )\n        if result.returncode == 0 and os.path.exists(output_path):\n            if os.path.exists(concat_file):\n                os.remove(concat_file)\n            return True\n        return False\n    except Exception as e:\n        return False\n\ninput_data = items[0]['json']\nscript_id = input_data.get('script_id', 'unknown')\nvideos_metadata = input_data.get('videos_metadata', [])\n\nif len(videos_metadata) != 7:\n    raise ValueError(f\"動画数が不正です。期待: 7本、実際: {len(videos_metadata)}本\")\n\ntemp_dir = tempfile.mkdtemp(prefix='wf7_phase4c_')\ndownloaded_paths = []\n\nfor i, video_meta in enumerate(videos_metadata, 1):\n    section = video_meta.get('section', f'video_{i}')\n    video_url = video_meta.get('video_url')\n    if not video_url:\n        raise ValueError(f\"動画URL未設定: section={section}\")\n    video_filename = f\"video_{i}_{section}.mp4\"\n    video_path = os.path.join(temp_dir, video_filename)\n    if not download_video(video_url, video_path):\n        raise RuntimeError(f\"動画ダウンロード失敗: {section}\")\n    downloaded_paths.append(video_path)\n\noutput_filename = f\"final_video_{script_id}_{int(time.time())}.mp4\"\noutput_path = os.path.join(temp_dir, output_filename)\n\nif not concat_videos_with_ffmpeg(downloaded_paths, output_path):\n    raise RuntimeError(\"FFmpeg結合失敗\")\n\noutput_size = os.path.getsize(output_path)\ntotal_duration = sum(v.get('duration', 0) for v in videos_metadata)\n\nreturn [{\n    'json': {\n        'success': True,\n        'script_id': script_id,\n        'output_video_path': output_path,\n        'output_video_size': output_size,\n        'total_duration': total_duration,\n        'videos_count': len(videos_metadata),\n        'temp_dir': temp_dir,\n        'articleId': input_data.get('articleId')\n    }\n}]"
  }
}
```

**実装アクション**:
1. ワークフローの`nodes`配列に上記ノードを追加
2. `connections`オブジェクトに以下を追加:
   ```json
   "IF - Phase4b Success Check": {
     "main": [
       [
         {
           "node": "Code - Phase4c FFmpeg Concat",
           "type": "main",
           "index": 0
         }
       ],
       [
         {
           "node": "エラー時Notion更新（Phase4b）",
           "type": "main",
           "index": 0
         }
       ]
     ]
   }
   ```
3. 既存の`Split Out`への接続を削除

---

### Step 2: Code - Read Video Binaryノードの追加

**ノード仕様**:
```json
{
  "id": "code-read-video-binary",
  "name": "Code - Read Video Binary",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [-912, -128],
  "parameters": {
    "language": "python",
    "mode": "runOnceForAllItems",
    "pythonCode": "import base64\n\noutput_video_path = items[0]['json']['output_video_path']\n\nwith open(output_video_path, 'rb') as f:\n    video_binary = f.read()\n    video_base64 = base64.b64encode(video_binary).decode('utf-8')\n\nreturn [{\n    'json': items[0]['json'],\n    'binary': {\n        'data': video_base64\n    }\n}]"
  }
}
```

**接続**:
```json
"Code - Phase4c FFmpeg Concat": {
  "main": [
    [
      {
        "node": "Code - Read Video Binary",
        "type": "main",
        "index": 0
      }
    ]
  ]
}
```

---

### Step 3: Google Drive - Upload Final Videoノードの追加

**ノード仕様**:
```json
{
  "id": "google-drive-upload-final-video",
  "name": "Google Drive - Upload Final Video",
  "type": "n8n-nodes-base.googleDrive",
  "typeVersion": 3,
  "position": [-688, -128],
  "credentials": {
    "googleDriveOAuth2Api": {
      "id": "y89xQdP2gCTcdyup",
      "name": "Google Drive account"
    }
  },
  "parameters": {
    "operation": "upload",
    "name": "={{ 'WF7_Final_' + $json.script_id + '_' + $now.toFormat('yyyyMMdd_HHmmss') + '.mp4' }}",
    "binaryData": true,
    "binaryPropertyName": "data",
    "options": {
      "mimeType": "video/mp4"
    }
  }
}
```

**接続**:
```json
"Code - Read Video Binary": {
  "main": [
    [
      {
        "node": "Google Drive - Upload Final Video",
        "type": "main",
        "index": 0
      }
    ]
  ]
}
```

**注意**: 既存のGoogle Drive資格情報のIDを確認し、適切に設定する。

---

### Step 4: Notion - Update Script Recordノードの追加

**ノード仕様**:
```json
{
  "id": "notion-update-script-record",
  "name": "Notion - Update Script Record",
  "type": "n8n-nodes-base.notion",
  "typeVersion": 2,
  "position": [-464, -128],
  "credentials": {
    "notionApi": {
      "id": "y89xQdP2gCTcdyup",
      "name": "Notion account"
    }
  },
  "parameters": {
    "resource": "databasePage",
    "operation": "update",
    "pageId": "={{ $('Code - Phase4c FFmpeg Concat').item.json.script_id }}",
    "properties": {
      "Status": {
        "select": {
          "name": "VideoReady"
        }
      },
      "Video URL": {
        "url": "={{ $json.webViewLink }}"
      },
      "Video Size (MB)": {
        "number": "={{ Math.round($('Code - Phase4c FFmpeg Concat').item.json.output_video_size / 1024 / 1024 * 100) / 100 }}"
      },
      "Total Duration (sec)": {
        "number": "={{ $('Code - Phase4c FFmpeg Concat').item.json.total_duration }}"
      }
    }
  }
}
```

**接続**:
```json
"Google Drive - Upload Final Video": {
  "main": [
    [
      {
        "node": "Notion - Update Script Record",
        "type": "main",
        "index": 0
      }
    ]
  ]
}
```

**注意**: Notion DBのプロパティ名が正確であることを確認する。

---

### Step 5: Code - Cleanup Temp Filesノードの追加

**ノード仕様**:
```json
{
  "id": "code-cleanup-temp-files",
  "name": "Code - Cleanup Temp Files",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [-240, -128],
  "parameters": {
    "language": "python",
    "mode": "runOnceForAllItems",
    "pythonCode": "import shutil\nimport os\n\ntemp_dir = items[0]['json'].get('temp_dir')\n\nif temp_dir and os.path.exists(temp_dir):\n    try:\n        shutil.rmtree(temp_dir)\n        return [{'json': {'cleanup_success': True, 'temp_dir': temp_dir}}]\n    except Exception as e:\n        return [{'json': {'cleanup_success': False, 'error': str(e)}}]\nelse:\n    return [{'json': {'cleanup_success': False, 'error': 'temp_dir not found'}}]"
  }
}
```

**接続**:
```json
"Notion - Update Script Record": {
  "main": [
    [
      {
        "node": "Code - Cleanup Temp Files",
        "type": "main",
        "index": 0
      }
    ]
  ]
}
```

---

### Step 6: Respond to Webhookノードの接続

**既存ノードの確認**:
- ノードID: `755761b2-0760-40f8-bc23-811e733b5d11`
- ノード名: `Respond to Webhook`
- 位置: 必要に応じて`[-16, -128]`に移動

**ノード設定の更新**:
```json
{
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ {\n  \"success\": true,\n  \"script_id\": $('Code - Phase4c FFmpeg Concat').item.json.script_id,\n  \"final_video_url\": $('Google Drive - Upload Final Video').item.json.webViewLink,\n  \"video_size_mb\": Math.round($('Code - Phase4c FFmpeg Concat').item.json.output_video_size / 1024 / 1024 * 100) / 100,\n  \"total_duration\": $('Code - Phase4c FFmpeg Concat').item.json.total_duration,\n  \"notion_updated\": true\n} }}"
  }
}
```

**接続**:
```json
"Code - Cleanup Temp Files": {
  "main": [
    [
      {
        "node": "Respond to Webhook",
        "type": "main",
        "index": 0
      }
    ]
  ]
}
```

---

## 🔄 実装手順（Claude Code向け）

### 実装フロー

1. **ワークフロー取得**
   ```javascript
   const workflow = await mcp_n8n-mcp_n8n_get_workflow({
     id: "qSN7EHj5yl0nPXij"
   });
   ```

2. **バックアップ作成**
   ```javascript
   // ワークフローJSONをファイルに保存
   await write_file({
     path: `workflows/archive/wf7phase4_v3_before_phase4c_${Date.now()}.json`,
     contents: JSON.stringify(workflow.data, null, 2)
   });
   ```

3. **ノード追加**
   - Step 1〜5のノードを`workflow.data.nodes`配列に追加
   - 各ノードのIDは一意であることを確認

4. **接続更新**
   - `workflow.data.connections`オブジェクトを更新
   - `IF - Phase4b Success Check`のTrue分岐を`Code - Phase4c FFmpeg Concat`に接続
   - 既存の`Split Out`への接続を削除
   - 新しいノード間の接続を追加

5. **ワークフロー更新**
   ```javascript
   await mcp_n8n-mcp_n8n_update_full_workflow({
     id: "qSN7EHj5yl0nPXij",
     name: workflow.data.name,
     nodes: workflow.data.nodes,
     connections: workflow.data.connections,
     settings: workflow.data.settings
   });
   ```

6. **検証**
   ```javascript
   const validation = await mcp_n8n-mcp_n8n_validate_workflow({
     id: "qSN7EHj5yl0nPXij"
   });
   ```

---

## ⚠️ 注意事項

### 1. ノードIDの一意性
- 各ノードのIDは一意である必要がある
- UUID形式を使用: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 2. 資格情報の確認
- Google Drive資格情報のIDを確認
- Notion API資格情報のIDを確認
- 既存のワークフローから取得したIDを使用

### 3. プロパティ名の確認
- Notion DBのプロパティ名が正確であることを確認
- 大文字小文字、スペースを含む名前を正確に指定

### 4. エラーハンドリング
- 各ステップでエラーが発生した場合、ロールバックを検討
- バックアップから復元可能な状態を維持

### 5. タイムアウト設定
- Code Nodeのタイムアウトを600秒（10分）に設定
- FFmpeg処理は最大600秒を想定

---

## 🧪 テスト手順

### 1. 単体テスト

1. `Code - Phase4c FFmpeg Concat`ノードを手動実行
2. Phase4b完了後のデータを使用
3. 7本の動画がダウンロードされ、結合されることを確認

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

## 📝 実装チェックリスト

- [ ] Step 0: ワークフロー取得とバックアップ作成
- [ ] Step 1: Code - Phase4c FFmpeg Concatノード追加
- [ ] Step 2: Code - Read Video Binaryノード追加
- [ ] Step 3: Google Drive - Upload Final Videoノード追加
- [ ] Step 4: Notion - Update Script Recordノード追加
- [ ] Step 5: Code - Cleanup Temp Filesノード追加
- [ ] Step 6: Respond to Webhookノード接続
- [ ] 接続の更新（IF - Phase4b Success Check）
- [ ] ワークフロー更新
- [ ] 検証
- [ ] 単体テスト実施
- [ ] 統合テスト実施
- [ ] エラーハンドリングテスト実施

---

## 🔗 関連ドキュメント

- `WF7-Phase4c-実装手順.md`: 手動実装手順書
- `WF7-Phase4c-手動実装ガイド.md`: n8n UIでの手動実装ガイド
- `phase4c_ffmpeg_concat.py`: Python実装コード
- `WF7-Phase4b-integration-instructions.md`: Phase4b統合指示書
- `WF7-Phase4-FAL実装計画書.md`: 全体実装計画書

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08  
**次のステップ**: 本指示書に基づき、Claude Codeが実装を実行

