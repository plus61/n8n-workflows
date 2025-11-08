#!/usr/bin/env python3
"""
WF7 Phase4c ノード追加スクリプト

このスクリプトは、既存のワークフローJSONに Phase4c関連のノードを追加します
"""

import json
import uuid

def generate_node_id():
    """新しいノードIDを生成"""
    return str(uuid.uuid4())

def create_phase4c_ffmpeg_concat_node():
    """Code - Phase4c FFmpeg Concat ノードを作成"""
    python_code = '''import subprocess
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
            f.write(f"file '{video_path}'\\n")

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
}]'''

    return {
        "id": "code-phase4c-ffmpeg-concat",
        "name": "Code - Phase4c FFmpeg Concat",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-1136, -128],
        "parameters": {
            "language": "python",
            "mode": "runOnceForAllItems",
            "pythonCode": python_code
        }
    }

def create_read_video_binary_node():
    """Code - Read Video Binary ノードを作成"""
    python_code = '''import base64

output_video_path = items[0]['json']['output_video_path']

with open(output_video_path, 'rb') as f:
    video_binary = f.read()
    video_base64 = base64.b64encode(video_binary).decode('utf-8')

return [{
    'json': items[0]['json'],
    'binary': {
        'data': video_base64
    }
}]'''

    return {
        "id": "code-read-video-binary",
        "name": "Code - Read Video Binary",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-912, -128],
        "parameters": {
            "language": "python",
            "mode": "runOnceForAllItems",
            "pythonCode": python_code
        }
    }

def create_google_drive_upload_node():
    """Google Drive - Upload Final Video ノードを作成"""
    return {
        "id": "google-drive-upload-final-video",
        "name": "Google Drive - Upload Final Video",
        "type": "n8n-nodes-base.googleDrive",
        "typeVersion": 3,
        "position": [-688, -128],
        "credentials": {
            "googleDriveOAuth2Api": {
                "id": "plniYONxQ1iPNoAi",
                "name": "Google Drive account"
            }
        },
        "parameters": {
            "operation": "upload",
            "name": "={{ 'WF7_Final_' + $('Code - Phase4c FFmpeg Concat').item.json.script_id + '_' + $now.toFormat('yyyyMMdd_HHmmss') + '.mp4' }}",
            "binaryData": True,
            "binaryPropertyName": "data",
            "options": {
                "mimeType": "video/mp4"
            }
        }
    }

def create_notion_update_node():
    """Notion - Update Script Record ノードを作成"""
    return {
        "id": "notion-update-script-record",
        "name": "Notion - Update Script Record",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-464, -128],
        "credentials": {
            "notionApi": {
                "id": "y89xQdP2gCTcdyup",
                "name": "Notion account"
            }
        },
        "parameters": {
            "method": "PATCH",
            "url": "={{ 'https://api.notion.com/v1/pages/' + $('Code - Phase4c FFmpeg Concat').item.json.script_id }}",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "notionApi",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Notion-Version", "value": "2022-06-28"},
                    {"name": "Content-Type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ { properties: { Status: { select: { name: 'VideoReady' } }, 'Video URL': { url: $json.webViewLink }, 'Video Size (MB)': { number: Math.round($('Code - Phase4c FFmpeg Concat').item.json.output_video_size / 1024 / 1024 * 100) / 100 }, 'Total Duration (sec)': { number: $('Code - Phase4c FFmpeg Concat').item.json.total_duration } } } }}",
            "options": {}
        }
    }

def create_cleanup_temp_files_node():
    """Code - Cleanup Temp Files ノードを作成"""
    python_code = '''import shutil
import os

temp_dir = items[0]['json'].get('temp_dir')

if temp_dir and os.path.exists(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        return [{'json': {'cleanup_success': True, 'temp_dir': temp_dir}}]
    except Exception as e:
        return [{'json': {'cleanup_success': False, 'error': str(e)}}]
else:
    return [{'json': {'cleanup_success': False, 'error': 'temp_dir not found'}}]'''

    return {
        "id": "code-cleanup-temp-files",
        "name": "Code - Cleanup Temp Files",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-240, -128],
        "parameters": {
            "language": "python",
            "mode": "runOnceForAllItems",
            "pythonCode": python_code
        }
    }

def update_connections(workflow_data, phase4c_nodes):
    """接続を更新"""
    connections = workflow_data.get('connections', {})

    # IF - Phase4b Success Check から Code - Phase4c FFmpeg Concat への接続
    connections["IF - Phase4b Success Check"] = {
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
                    "node": "エラー時Notion更新(Phase4b)",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

    # Code - Phase4c FFmpeg Concat から Code - Read Video Binary への接続
    connections["Code - Phase4c FFmpeg Concat"] = {
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

    # Code - Read Video Binary から Google Drive - Upload Final Video への接続
    connections["Code - Read Video Binary"] = {
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

    # Google Drive - Upload Final Video から Notion - Update Script Record への接続
    connections["Google Drive - Upload Final Video"] = {
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

    # Notion - Update Script Record から Code - Cleanup Temp Files への接続
    connections["Notion - Update Script Record"] = {
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

    # Code - Cleanup Temp Files から Respond to Webhook への接続
    connections["Code - Cleanup Temp Files"] = {
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

    workflow_data['connections'] = connections
    return workflow_data

def update_respond_to_webhook_node(workflow_data):
    """Respond to Webhook ノードを更新"""
    for node in workflow_data['nodes']:
        if node.get('name') == 'Respond to Webhook':
            node['parameters'] = {
                "respondWith": "json",
                "responseBody": "={{ { success: true, script_id: $('Code - Phase4c FFmpeg Concat').item.json.script_id, final_video_url: $('Google Drive - Upload Final Video').item.json.webViewLink, video_size_mb: Math.round($('Code - Phase4c FFmpeg Concat').item.json.output_video_size / 1024 / 1024 * 100) / 100, total_duration: $('Code - Phase4c FFmpeg Concat').item.json.total_duration, notion_updated: true } }}",
                "options": {}
            }
            node['position'] = [-16, -128]
            break
    return workflow_data

def add_phase4c_nodes(workflow_json_path, output_json_path):
    """Phase4cノードをワークフローに追加"""
    # ワークフローJSONを読み込み
    with open(workflow_json_path, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)

    # 新しいノードを作成
    phase4c_nodes = [
        create_phase4c_ffmpeg_concat_node(),
        create_read_video_binary_node(),
        create_google_drive_upload_node(),
        create_notion_update_node(),
        create_cleanup_temp_files_node()
    ]

    # ノードを追加
    workflow_data['nodes'].extend(phase4c_nodes)

    # 接続を更新
    workflow_data = update_connections(workflow_data, phase4c_nodes)

    # Respond to Webhook ノードを更新
    workflow_data = update_respond_to_webhook_node(workflow_data)

    # 出力JSONを保存
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Phase4cノードを追加しました: {output_json_path}")
    return workflow_data

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("使用方法: python add_phase4c_nodes.py <input_workflow.json> <output_workflow.json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    add_phase4c_nodes(input_path, output_path)
