#!/usr/bin/env python3
"""
Phase4cワークフローをtracks形式に更新するスクリプト
- Aggregate Videosノードでdurationも保持
- ペイロード構築ノードをtracks形式に変更
"""

import json
import sys

def update_workflow_to_tracks_format(workflow_data):
    """ワークフローをtracks形式に更新"""
    
    # Aggregate Videosノードを更新してdurationも集約
    for node in workflow_data.get('nodes', []):
        if node.get('id') == 'aggregate-videos':
            # durationフィールドも集約に追加
            node['parameters']['fieldsToAggregate']['fieldToAggregate'].append({
                'fieldToAggregate': 'duration'
            })
            print("✅ Aggregate Videosノードを更新: durationも集約")
            break
    
    # ペイロード構築ノードをtracks形式に更新
    for node in workflow_data.get('nodes', []):
        if node.get('id') == 'payload-builder':
            node['parameters']['jsCode'] = '''// FAL FFmpeg API /compose endpoint payload construction (tracks format)
// Phase4bと同じ形式を使用して、response_urlにGETリクエストを送信した際に正しいレスポンスが返るようにする

const inputData = $input.all();
const scriptId = inputData[0]?.json?.script_id || 'unknown';

if (!inputData || inputData.length === 0) {
  throw new Error('Input data is required');
}

// 入力データからvideo_urlとdurationを取得
// Aggregate Videosノードの出力は、各アイテムのvideo_urlとdurationを含む
let cumulativeTime = 0;
const keyframes = inputData.map((item, index) => {
  const videoUrl = item.json.video_url;
  // duration情報が含まれている場合はそれを使用、なければデフォルト5秒
  const duration = item.json.duration || 5;
  const timestamp = cumulativeTime;
  
  // 次のタイムスタンプ用に累積時間を更新
  cumulativeTime += duration;
  
  if (!videoUrl) {
    throw new Error(`video_url is missing at index ${index}`);
  }
  
  return {
    url: videoUrl,
    timestamp: timestamp,
    duration: duration
  };
});

// Phase4b形式（tracks）のペイロード
const payload = {
  tracks: [{
    id: "1",
    type: "video",
    keyframes: keyframes
  }]
};

return [{ json: { ...payload, script_id: scriptId } }];'''
            node['notes'] = 'FAL FFmpeg API /compose用のペイロードを構築（tracks形式）'
            print("✅ ペイロード構築ノードを更新: tracks形式に変更")
            break
    
    return workflow_data

def main():
    # MCPツールから取得したワークフローデータを使用
    # 実際には、n8n APIから取得したワークフローJSONを使用
    print("Phase4cワークフローをtracks形式に更新中...")
    print("=" * 60)
    
    # ワークフローID
    workflow_id = "chPw11OY5sex6d9I"
    
    print(f"\nワークフローID: {workflow_id}")
    print("\nこのスクリプトは、MCPツールを使用してワークフローを更新します。")
    print("手動でn8n APIからワークフローを取得して更新する必要があります。")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

