#!/bin/bash

# Phase4cテスト結果確認スクリプト

WORKFLOW_ID="chPw11OY5sex6d9I"
EXECUTION_ID="1026"  # 最新の実行ID（必要に応じて変更）

echo "=========================================="
echo "Phase4cテスト結果確認"
echo "=========================================="
echo ""
echo "ワークフローID: $WORKFLOW_ID"
echo "実行ID: $EXECUTION_ID"
echo ""

echo "📊 実行結果を確認中..."
echo ""

# n8n MCPツールを使用する場合のコマンド例
echo "n8n MCPツールで実行結果を確認:"
echo "  mcp_n8n-mcp_n8n_get_execution({id: \"$EXECUTION_ID\", mode: \"summary\"})"
echo ""

echo "または、n8n UIで確認:"
echo "  https://n8n-python-production-344b.up.railway.app/workflow/$WORKFLOW_ID"
echo ""

echo "=========================================="

