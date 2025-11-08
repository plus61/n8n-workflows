#!/bin/bash

# Phase4cテスト実行結果確認スクリプト
# 使用方法: ./check-phase4c-execution.sh

WORKFLOW_ID="r9Sp5n0mkUCcH8cw"
N8N_URL="https://n8n-python-production-344b.up.railway.app"

echo "=========================================="
echo "WF7 Phase4c テスト実行結果確認"
echo "=========================================="
echo ""
echo "ワークフローID: $WORKFLOW_ID"
echo "n8n URL: $N8N_URL"
echo ""
echo "最新の実行履歴を確認中..."
echo ""

# 最新の実行履歴を取得（curlで直接APIを呼び出す場合）
# 注意: n8n APIの認証が必要な場合があります

echo "n8n UIで実行履歴を確認してください:"
echo "$N8N_URL/workflow/$WORKFLOW_ID/executions"
echo ""
echo "または、MCPツールを使用して実行履歴を確認できます。"
echo ""

