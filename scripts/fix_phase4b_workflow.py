#!/usr/bin/env python3
"""
WF7 Phase4bワークフローの改善スクリプト
- CodeノードのonError設定を修正
- HTTP RequestノードにmaxTriesを追加
"""

import json
import sys

def fix_workflow(workflow_data):
    """ワークフローを修正"""
    nodes = workflow_data.get('nodes', [])
    
    # 修正が必要なノード名とその設定
    nodes_to_fix = {
        'Code - Generate Cloudinary Signature': 'continueRegularOutput',
        'Code - Prepare FAL Payload': 'continueRegularOutput',
        'Code - Build Video Metadata': 'continueRegularOutput',
        'Code - Timeout Error': 'continueRegularOutput',
        'IF - Render Completed?': 'continueRegularOutput',
        'IF - Check Retry Limit': 'continueRegularOutput',
    }
    
    for node in nodes:
        node_name = node.get('name', '')
        if node_name in nodes_to_fix:
            node['onError'] = nodes_to_fix[node_name]
            print(f"✅ Fixed: {node_name} -> onError: {nodes_to_fix[node_name]}")
        
        # HTTP Request - Submit to FALにmaxTriesを追加
        if node_name == 'HTTP Request - Submit to FAL':
            if 'retryOnFail' in node and node.get('retryOnFail'):
                if 'maxTries' not in node:
                    node['maxTries'] = 3
                    print(f"✅ Added maxTries to {node_name}")
                if 'waitBetweenTries' not in node:
                    node['waitBetweenTries'] = 1000
                    print(f"✅ Added waitBetweenTries to {node_name}")
    
    return workflow_data

if __name__ == '__main__':
    # ワークフローID
    workflow_id = 'wHaKi98mTlUvFIOR'
    
    # ワークフローファイルを読み込み
    workflow_file = 'workflows/wf7_phase4b_fixed.json'
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # ワークフローを修正
        fixed_workflow = fix_workflow(workflow_data)
        
        # 修正したワークフローを保存
        output_file = 'workflows/wf7_phase4b_fixed_v2.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_workflow, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ ワークフローを修正しました: {output_file}")
        print(f"📋 次のステップ: n8n APIを使用してワークフローを更新してください")
        
    except FileNotFoundError:
        print(f"❌ エラー: {workflow_file} が見つかりません")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ エラー: JSONの解析に失敗しました: {e}")
        sys.exit(1)

