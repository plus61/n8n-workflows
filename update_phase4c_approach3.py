#!/usr/bin/env python3
"""
WF7 Phase4c アプローチ3実装スクリプト
ドキュメント: docs/testing/WF7-Phase4c-実行1032-1036-修正まとめ.md
"""

import json
import os
import sys

# ワークフローID
WORKFLOW_ID = "chPw11OY5sex6d9I"

def update_extract_attempt2_code():
    """Extract Video URL (Attempt 2)ノードのコードを更新"""
    return """// アプローチ2: response_urlのGETレスポンスから動画URLを抽出
// エラーハンドリングを追加（422エラーの場合、別の方法を試す）
const resultData = $input.first().json;

// デバッグ用: レスポンス構造をログ出力
console.log('Get Result response keys:', Object.keys(resultData));
console.log('Get Result response preview:', JSON.stringify(resultData).substring(0, 500));

// エラーレスポンスの場合（422エラーなど）
if (resultData.detail || resultData.error) {
  // エラーメッセージから動画URLを抽出できない場合、nullを返す
  console.warn('Get Result returned error:', JSON.stringify(resultData));
  
  // アプローチ3が必要かチェック（status_urlがある場合）
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  const needsStatusUrlRequest = Boolean(attempt1Data.raw_status_response?.status_url);
  
  return [{
    json: {
      video_url: null,
      error: resultData.detail || resultData.error,
      needs_status_url_request: needsStatusUrlRequest,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}

// 動画URL抽出（成功実例パターン）
let videoUrl = resultData.output?.video_url
  || resultData.output?.video?.url
  || resultData.output?.url
  || resultData.video_url
  || resultData.result?.video_url
  || resultData.video?.url
  || (resultData.url && !resultData.url.includes('/requests/') && !resultData.url.includes('/status'));

if (!videoUrl) {
  const availableKeys = Object.keys(resultData);
  const responsePreview = JSON.stringify(resultData, null, 2).substring(0, 2000);
  console.warn('Video URL not found in response_url GET response');
  console.warn('Available keys:', availableKeys);
  console.warn('Response preview:', responsePreview);
  
  // アプローチ3が必要かチェック（status_urlがある場合）
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  const needsStatusUrlRequest = Boolean(attempt1Data.raw_status_response?.status_url);
  
  return [{
    json: {
      video_url: null,
      error: 'Video URL not found in response_url GET response',
      needs_status_url_request: needsStatusUrlRequest,
      raw_response: resultData,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}

return [{
  json: {
    video_url: videoUrl,
    needs_status_url_request: false,
    raw_response: resultData,
    request_id: $('Extract Video URL (Attempt 1)').item.json.request_id,
    script_id: $('Extract Video URL (Attempt 1)').item.json.script_id || 'unknown'
  }
}];"""

def update_merge_video_url_code():
    """Merge Video URLノードのコードを更新"""
    return """// 動画URLを統合（アプローチ1、アプローチ2、またはアプローチ3の結果）
// エラーハンドリングを改善
const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;

// アプローチ1で動画URLが取得できた場合
if (attempt1Data.video_url) {
  return [{
    json: {
      video_url: attempt1Data.video_url,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id,
      approach: 'status_response_direct'
    }
  }];
}

// アプローチ2の結果を確認（Needs Status URL Request?のfalse分岐から来る場合）
let attempt2Data = null;
try {
  const attempt2Node = $('Extract Video URL (Attempt 2)');
  if (attempt2Node && attempt2Node.item) {
    attempt2Data = attempt2Node.item.json;
  }
} catch (e) {
  // アプローチ2が実行されていない場合（アプローチ1で成功した場合）
}

// アプローチ2で動画URLが取得できた場合
if (attempt2Data && attempt2Data.video_url) {
  return [{
    json: {
      video_url: attempt2Data.video_url,
      request_id: attempt2Data.request_id,
      script_id: attempt2Data.script_id,
      approach: 'response_url_get'
    }
  }];
}

// アプローチ3の結果を確認（Needs Status URL Request?のtrue分岐から来る場合）
let attempt3Data = null;
try {
  const attempt3Node = $('Extract Video URL (Attempt 3)');
  if (attempt3Node && attempt3Node.item) {
    attempt3Data = attempt3Node.item.json;
  }
} catch (e) {
  // アプローチ3が実行されていない場合
}

// アプローチ3で動画URLが取得できた場合
if (attempt3Data && attempt3Data.video_url) {
  return [{
    json: {
      video_url: attempt3Data.video_url,
      request_id: attempt3Data.request_id,
      script_id: attempt3Data.script_id,
      approach: 'status_url_get'
    }
  }];
}

// どれも失敗した場合、詳細なエラーメッセージを返す
const errorDetails = {
  attempt1: {
    video_url: attempt1Data.video_url,
    needs_get_request: attempt1Data.needs_get_request,
    response_keys: Object.keys(attempt1Data.raw_status_response || {})
  },
  attempt2: attempt2Data ? (attempt2Data.error ? {
    error: attempt2Data.error,
    raw_response_keys: Object.keys(attempt2Data.raw_response || {})
  } : {
    video_url: attempt2Data.video_url,
    raw_response_keys: Object.keys(attempt2Data.raw_response || {})
  }) : 'not executed',
  attempt3: attempt3Data ? (attempt3Data.error ? {
    error: attempt3Data.error,
    raw_response_keys: Object.keys(attempt3Data.raw_response || {})
  } : {
    video_url: attempt3Data.video_url,
    raw_response_keys: Object.keys(attempt3Data.raw_response || {})
  }) : 'not executed'
};

throw new Error(
  'Video URL not found in all approaches.\\n' +
  'Attempt 1 (status response): ' + JSON.stringify(errorDetails.attempt1, null, 2) + '\\n' +
  'Attempt 2 (response_url GET): ' + JSON.stringify(errorDetails.attempt2, null, 2) + '\\n' +
  'Attempt 3 (status_url GET): ' + JSON.stringify(errorDetails.attempt3, null, 2)
);"""

def create_new_nodes():
    """新しいノードを作成"""
    return [
        {
            "id": "needs-status-url-request",
            "name": "Needs Status URL Request?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [2720, 96],
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{ $json.needs_status_url_request }}",
                            "value2": True
                        }
                    ]
                },
                "options": {}
            },
            "notes": "アプローチ2が失敗した場合、アプローチ3（status_url）が必要かチェック"
        },
        {
            "id": "get-status-url-approach3",
            "name": "Get Status URL (Approach 3)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": [2944, 32],
            "parameters": {
                "method": "GET",
                "url": "={{ $('Extract Video URL (Attempt 1)').item.json.raw_status_response.status_url }}",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "options": {
                    "response": {
                        "response": {
                            "neverError": True
                        }
                    },
                    "timeout": 30000
                }
            },
            "credentials": {
                "httpHeaderAuth": {
                    "id": "voV5kURaCkiUjLTZ",
                    "name": "fal"
                }
            },
            "notes": "status_urlにGETリクエストを送信（アプローチ3）"
        },
        {
            "id": "extract-video-url-attempt3",
            "name": "Extract Video URL (Attempt 3)",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [3168, 32],
            "parameters": {
                "jsCode": """// アプローチ3: status_urlのGETレスポンスから動画URLを抽出
const resultData = $input.first().json;

// デバッグ用: レスポンス構造をログ出力
console.log('Get Status URL response keys:', Object.keys(resultData));
console.log('Get Status URL response preview:', JSON.stringify(resultData).substring(0, 500));

// エラーレスポンスの場合
if (resultData.detail || resultData.error) {
  console.warn('Get Status URL returned error:', JSON.stringify(resultData));
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  return [{
    json: {
      video_url: null,
      error: resultData.detail || resultData.error,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}

// 動画URL抽出（複数のパターンを試す）
let videoUrl = resultData.output?.video_url
  || resultData.output?.video?.url
  || resultData.output?.url
  || resultData.video_url
  || resultData.result?.video_url
  || resultData.video?.url
  || (resultData.url && !resultData.url.includes('/requests/') && !resultData.url.includes('/status'));

if (!videoUrl) {
  const availableKeys = Object.keys(resultData);
  const responsePreview = JSON.stringify(resultData, null, 2).substring(0, 2000);
  console.warn('Video URL not found in status_url GET response');
  console.warn('Available keys:', availableKeys);
  console.warn('Response preview:', responsePreview);
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  return [{
    json: {
      video_url: null,
      error: 'Video URL not found in status_url GET response',
      raw_response: resultData,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}

const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
return [{
  json: {
    video_url: videoUrl,
    raw_response: resultData,
    request_id: attempt1Data.request_id,
    script_id: attempt1Data.script_id || 'unknown'
  }
}];"""
            },
            "notes": "status_urlのGETレスポンスから動画URLを抽出（アプローチ3）"
        }
    ]

def update_connections(connections):
    """接続を更新"""
    # Extract Video URL (Attempt 2)からMerge Video URLへの接続を削除
    if "Extract Video URL (Attempt 2)" in connections:
        connections["Extract Video URL (Attempt 2)"] = {
            "main": [
                [
                    {
                        "node": "Needs Status URL Request?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    
    # Needs Status URL Request?の接続を追加
    connections["Needs Status URL Request?"] = {
        "main": [
            [
                {
                    "node": "Get Status URL (Approach 3)",
                    "type": "main",
                    "index": 0
                }
            ],
            [
                {
                    "node": "Merge Video URL",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }
    
    # Get Status URL (Approach 3)の接続を追加
    connections["Get Status URL (Approach 3)"] = {
        "main": [
            [
                {
                    "node": "Extract Video URL (Attempt 3)",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }
    
    # Extract Video URL (Attempt 3)の接続を追加
    connections["Extract Video URL (Attempt 3)"] = {
        "main": [
            [
                {
                    "node": "Merge Video URL",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }
    
    return connections

if __name__ == "__main__":
    print("このスクリプトは、ワークフロー更新のためのヘルパー関数を提供します。")
    print("実際の更新は、n8n MCPツールを使用して実行してください。")

