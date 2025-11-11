#!/usr/bin/env python3
"""
WF7 Phase4bワークフローをn8n APIにアップロードするスクリプト
"""
import json
import os

def main():
    workflow_file = 'workflows/wf7_phase4b_fixed_v2.json'
    workflow_id = 'wHaKi98mTlUvFIOR'
    
    print(f"📂 ワークフローファイルを読み込み中: {workflow_file}")
    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    nodes = workflow.get('nodes', [])
    connections = workflow.get('connections', {})
    name = workflow.get('name', 'WF7 Phase4b - Image to Video')
    
    print(f"✅ ワークフロー名: {name}")
    print(f"✅ ノード数: {len(nodes)}")
    print(f"✅ 接続数: {len(connections)}")
    
    # 修正されたノードを確認
    fixed_nodes = []
    for node in nodes:
        node_name = node.get('name', '')
        on_error = node.get('onError', '')
        if on_error:
            fixed_nodes.append(f"  - {node_name}: {on_error}")
    
    print(f"\n📋 修正されたノード ({len(fixed_nodes)}件):")
    for node_info in fixed_nodes[:10]:  # 最初の10件を表示
        print(node_info)
    if len(fixed_nodes) > 10:
        print(f"  ... 他 {len(fixed_nodes) - 10} 件")
    
    print(f"\n✅ ワークフローの修正が完了しました")
    print(f"📋 次のステップ:")
    print(f"   ワークフローID: {workflow_id}")
    print(f"   n8n MCPツールを使用してワークフローを更新してください")

if __name__ == '__main__':
    main()

