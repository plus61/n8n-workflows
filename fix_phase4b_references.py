#!/usr/bin/env python3
"""
Phase4bノード参照修正スクリプト
Set - Phase4a Payload → Set - Phase4a Payload New に修正
"""

import json
import sys
import os
from datetime import datetime

def fix_workflow_references(workflow_data):
    """ワークフローのノード参照を修正"""
    workflow = workflow_data['data'] if 'data' in workflow_data else workflow_data
    fixes_applied = []
    
    # 修正1: HTTP Request - Call Phase4b の jsonBody
    for node in workflow['nodes']:
        if node.get('name') == 'HTTP Request - Call Phase4b':
            old_body = node['parameters'].get('jsonBody', '')
            if 'Set - Phase4a Payload' in old_body and 'Set - Phase4a Payload New' not in old_body:
                new_body = old_body.replace("Set - Phase4a Payload", "Set - Phase4a Payload New")
                node['parameters']['jsonBody'] = new_body
                fixes_applied.append({
                    'node': 'HTTP Request - Call Phase4b',
                    'field': 'jsonBody',
                    'old': old_body[:80] + '...',
                    'new': new_body[:80] + '...'
                })
            break
    
    # 修正2: Set - Phase4b Payload の articleId
    for node in workflow['nodes']:
        if node.get('name') == 'Set - Phase4b Payload':
            assignments = node['parameters'].get('assignments', {}).get('assignments', [])
            for assignment in assignments:
                if assignment.get('name') == 'articleId':
                    old_value = assignment.get('value', '')
                    if 'Set - Phase4a Payload' in old_value and 'Set - Phase4a Payload New' not in old_value:
                        new_value = old_value.replace("Set - Phase4a Payload", "Set - Phase4a Payload New")
                        assignment['value'] = new_value
                        fixes_applied.append({
                            'node': 'Set - Phase4b Payload',
                            'field': 'articleId',
                            'old': old_value,
                            'new': new_value
                        })
                    break
            break
    
    # 修正3: エラー時Notion更新(Phase4b) の url
    for node in workflow['nodes']:
        if node.get('name') == 'エラー時Notion更新(Phase4b)':
            old_url = node['parameters'].get('url', '')
            if 'Set - Phase4a Payload' in old_url and 'Set - Phase4a Payload New' not in old_url:
                new_url = old_url.replace("Set - Phase4a Payload", "Set - Phase4a Payload New")
                node['parameters']['url'] = new_url
                fixes_applied.append({
                    'node': 'エラー時Notion更新(Phase4b)',
                    'field': 'url',
                    'old': old_url,
                    'new': new_url
                })
            break
    
    return workflow, fixes_applied

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python3 fix_phase4b_references.py <workflow_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        workflow, fixes = fix_workflow_references(workflow_data)
        
        if fixes:
            print(f"✅ {len(fixes)}箇所の修正を適用しました:\n")
            for i, fix in enumerate(fixes, 1):
                print(f"{i}. {fix['node']} - {fix['field']}")
                print(f"   修正前: {fix['old']}")
                print(f"   修正後: {fix['new']}\n")
            
            # 修正後のワークフローをバージョン名付きで保存（元のファイルは上書きしない）
            input_dir = os.path.dirname(input_file)
            input_basename = os.path.basename(input_file)
            input_name, input_ext = os.path.splitext(input_basename)
            
            # タイムスタンプを生成（YYYYMMDD_HHMMSS形式）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # バージョン名を生成: 元のファイル名_phase4b_fixed_タイムスタンプ.json
            if input_name.endswith('_fixed'):
                # 既に_fixedが付いている場合は、その前の部分を使用
                base_name = input_name.replace('_fixed', '')
            else:
                base_name = input_name
            
            output_filename = f"{base_name}_phase4b_fixed_{timestamp}{input_ext}"
            output_file = os.path.join(input_dir, output_filename)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 修正後のワークフローを保存しました:")
            print(f"   ファイル名: {output_filename}")
            print(f"   パス: {output_file}")
            print(f"   元のファイル: {input_file} (変更なし)")
        else:
            print("修正が必要な箇所は見つかりませんでした。")
    
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

