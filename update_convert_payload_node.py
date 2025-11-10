#!/usr/bin/env python3
"""
Convert Payload to Tracksノードのコードを修正するスクリプト
オプション1実装後に対応
"""

import json
import sys

def update_convert_payload_node(workflow_data):
    """Convert Payload to Tracksノードのコードを修正"""
    
    # 修正後のコード
    new_code = """// ペイロード変換: オプション1実装後、ペイロード構築ノードの出力はすでにtracks形式
// そのまま使用する（変換不要）
const phase4cPayload = $('ペイロード構築').item.json;
const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;

// オプション1実装後は、ペイロード構築ノードの出力がすでにtracks形式
// そのまま使用する（script_idは除外）
const tracksPayload = {
  tracks: phase4cPayload.tracks || [{
    id: "1",
    type: "video",
    keyframes: []
  }]
};

return [{
  json: {
    payload: tracksPayload,
    response_url: attempt1Data.raw_status_response.response_url,
    request_id: attempt1Data.request_id,
    script_id: attempt1Data.script_id || 'unknown'
  }
}];"""
    
    # Convert Payload to Tracksノードを探して更新
    for node in workflow_data.get('nodes', []):
        if node.get('id') == 'convert-payload-to-tracks':
            node['parameters']['jsCode'] = new_code
            node['notes'] = 'オプション1実装後: ペイロード構築ノードの出力（tracks形式）をそのまま使用'
            print(f"✅ Convert Payload to Tracksノードのコードを更新しました")
            return workflow_data
    
    print("❌ Convert Payload to Tracksノードが見つかりませんでした")
    return workflow_data

if __name__ == '__main__':
    # ワークフローJSONファイルのパスを指定
    workflow_file = sys.argv[1] if len(sys.argv) > 1 else 'workflow.json'
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        updated_workflow = update_convert_payload_node(workflow_data)
        
        # 更新されたワークフローを保存
        output_file = workflow_file.replace('.json', '_updated.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_workflow, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 更新されたワークフローを {output_file} に保存しました")
        
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {workflow_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSONの解析エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

