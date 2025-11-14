#!/usr/bin/env python3
"""
n8nワークフローをアップロードするスクリプト
"""
import json
import sys

def load_workflow(file_path):
    """ワークフローファイルを読み込む"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workflow_file = '/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json'
    workflow_id = 'r9Sp5n0mkUCcH8cw'
    
    print(f"ワークフローファイルを読み込み中: {workflow_file}")
    workflow = load_workflow(workflow_file)
    
    print(f"ワークフロー名: {workflow['name']}")
    print(f"ノード数: {len(workflow['nodes'])}")
    print(f"接続数: {len(workflow['connections'])}")
    
    # JSONファイルとして出力（n8n MCPツールで使用するため）
    output_file = '/tmp/workflow_for_n8n.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    print(f"\nワークフローを一時ファイルに保存しました: {output_file}")
    print(f"\n次のステップ:")
    print(f"1. n8n UIでワークフローID {workflow_id} を開く")
    print(f"2. ワークフローをインポートするか、手動で更新する")
    print(f"\nまたは、n8n MCPツールを使用してワークフローを更新してください。")

if __name__ == '__main__':
    main()


