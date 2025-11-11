#!/usr/bin/env python3
"""
WF7 Phase4bワークフローの修正を適用するスクリプト
現在のワークフローのノードIDと位置座標を保持しつつ、修正済み設定を適用
"""
import json

# 現在のワークフローのノードIDと位置座標のマッピング
# (ノード名 -> 現在のIDと位置)
current_node_mapping = {
    "Webhook - Phase 4b Start": {
        "id": "c1763334-d628-407c-aa37-4eecebcf412e",
        "position": [-5392, 304]
    },
    "Execute Workflow Trigger": {
        "id": "2af94d86-a3e3-424d-bbf4-37edf8e3f01b",
        "position": [-5168, 304]
    },
    "Code - Validate Input": {
        "id": "719f6ac1-d92e-4ddb-806a-a21d066ac4c3",
        "position": [-4944, 304]
    },
    "Split Out - Slides": {
        "id": "8f808ab4-14b0-494d-8ad8-2da960d093a3",
        "position": [-4720, 384]
    },
    "HTTP Request - Download from Google Drive": {
        "id": "121d139f-05b5-431b-b5b6-5494ac7314e2",
        "position": [-4496, 384]
    },
    "Code - Generate Cloudinary Signature": {
        "id": "f8b183b1-b153-40fb-b12f-81eacc8c0c88",
        "position": [-4272, 384]
    },
    "Code - Upload to Cloudinary with Base64": {
        "id": "f1342286-b5d4-40c1-811f-d28f2f63b1cb",
        "position": [-4048, 384]
    },
    "Set - Preserve Slide Metadata": {
        "id": "f3b94046-6ee0-49b9-bcef-b52a1f392c43",
        "position": [-3824, 384]
    },
    "Code - Prepare FAL Payload": {
        "id": "e66d2318-44f1-45db-9c55-7968ba5f53af",
        "position": [-3600, 384]
    },
    "HTTP Request - Submit to FAL": {
        "id": "06fc6ca9-34f0-4e78-ab35-5945a0611733",
        "position": [-3376, 384]
    },
    "Wait - 5 Seconds": {
        "id": "2da16f09-3b54-415d-b31d-2a4c47ca7285",
        "position": [-3152, 384]
    },
    "HTTP Request - Check Status": {
        "id": "f37fb5f7-d974-40bf-82d1-039381a2d0de",
        "position": [-2928, 384]
    },
    "IF - Render Completed?": {
        "id": "f5dde118-fda5-45c5-96af-62d92363e40f",
        "position": [-2704, 288]
    },
    "HTTP Request - Get Result": {
        "id": "739b7b88-810d-4d7a-bf4b-00ecc75eac6b",
        "position": [-2480, 208]
    },
    "Code - Build Video Metadata": {
        "id": "e6b10d79-ae38-4b08-a3eb-b261de0f1001",
        "position": [-2256, 208]
    },
    "Aggregate - Wait for All Videos": {
        "id": "976bebe4-4a14-4824-b464-b8dee98d58a7",
        "position": [-2032, 208]
    },
    "Code - Build Final Response": {
        "id": "a1936107-6060-4105-b5da-826b31650405",
        "position": [-1808, 208]
    },
    "Set - Retry Counter": {
        "id": "ef30de85-eb4f-48f7-8952-cdf10d21d0a1",
        "position": [-2480, 432]
    },
    "IF - Check Retry Limit": {
        "id": "3867b3e6-bb6e-44e9-9dfc-6186d9842414",
        "position": [-2256, 416]
    },
    "Wait - Before Retry": {
        "id": "cf9e0baa-62ed-482e-a93d-3ed592f251e2",
        "position": [-2032, 432]
    },
    "Code - Timeout Error": {
        "id": "98f7a8af-f11c-418d-89ce-7e49f12b7af7",
        "position": [-2032, 624]
    },
    "Respond to Webhook": {
        "id": "75a3724c-486e-471e-9fc9-850a7fcf609a",
        "position": [-1584, 208]
    }
}

def apply_fixes():
    """修正済みワークフローを読み込み、現在のノードIDと位置座標を適用"""
    # 修正済みワークフローを読み込み
    with open('workflows/wf7_phase4b_fixed_v2.json', 'r', encoding='utf-8') as f:
        fixed_workflow = json.load(f)
    
    # ノードIDと位置座標を現在のものに置き換え
    for node in fixed_workflow['nodes']:
        node_name = node.get('name', '')
        if node_name in current_node_mapping:
            node['id'] = current_node_mapping[node_name]['id']
            node['position'] = current_node_mapping[node_name]['position']
    
    # 修正済みワークフローを保存
    output_file = 'workflows/wf7_phase4b_fixed_with_current_ids.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_workflow, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 修正済みワークフローを保存しました: {output_file}")
    print(f"📋 次のステップ:")
    print(f"   n8n MCPツールを使用してワークフローを更新してください")
    print(f"   ワークフローID: wHaKi98mTlUvFIOR")
    
    return output_file

if __name__ == '__main__':
    apply_fixes()

