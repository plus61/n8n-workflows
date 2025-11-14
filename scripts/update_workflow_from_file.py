#!/usr/bin/env python3
"""
修正済みワークフローファイルをn8nにアップロードするスクリプト
"""
import json
import os
import requests

def load_workflow(file_path):
    """ワークフローファイルを読み込む"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_workflow(workflow_id, workflow_data, api_key, base_url):
    """n8n APIを使用してワークフローを更新"""
    url = f"{base_url}/api/v1/workflows/{workflow_id}"
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    # ワークフロー更新用のペイロード
    payload = {
        "name": workflow_data["name"],
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": workflow_data.get("settings", {}),
        "staticData": workflow_data.get("staticData"),
        "pinData": workflow_data.get("pinData", {})
    }
    
    response = requests.put(url, json=payload, headers=headers)
    return response

def main():
    workflow_file = 'workflows/wf7_phase4b_fixed_with_current_ids.json'
    workflow_id = 'wHaKi98mTlUvFIOR'
    
    # 環境変数からAPIキーとURLを取得
    api_key = os.getenv('N8N_API_KEY')
    base_url = os.getenv('N8N_BASE_URL', 'https://n8n-python-production-344b.up.railway.app')
    
    if not api_key:
        print("❌ N8N_API_KEY環境変数が設定されていません")
        print("環境変数を設定してから再度実行してください:")
        print("export N8N_API_KEY='your-api-key'")
        return
    
    print(f"ワークフローファイルを読み込み中: {workflow_file}")
    workflow = load_workflow(workflow_file)
    
    print(f"ワークフロー名: {workflow['name']}")
    print(f"ノード数: {len(workflow['nodes'])}")
    print(f"接続数: {len(workflow['connections'])}")
    
    # Webhookノードの接続を確認
    if 'Webhook - Phase 4b Start' in workflow['connections']:
        print("✅ Webhookノードの接続が存在します")
    else:
        print("❌ Webhookノードの接続が存在しません")
        return
    
    print(f"\nn8n APIを使用してワークフローを更新中...")
    print(f"ワークフローID: {workflow_id}")
    print(f"Base URL: {base_url}")
    
    try:
        response = update_workflow(workflow_id, workflow, api_key, base_url)
        
        if response.status_code == 200:
            print("✅ ワークフローの更新が成功しました")
            result = response.json()
            print(f"更新日時: {result.get('updatedAt', 'N/A')}")
        else:
            print(f"❌ ワークフローの更新に失敗しました")
            print(f"ステータスコード: {response.status_code}")
            print(f"レスポンス: {response.text}")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == '__main__':
    main()

