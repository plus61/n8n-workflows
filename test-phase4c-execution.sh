#!/bin/bash

# Phase4cテスト実行スクリプト
# ワークフローID: chPw11OY5sex6d9I

WORKFLOW_ID="chPw11OY5sex6d9I"
N8N_URL="https://n8n-python-production-344b.up.railway.app"

echo "=========================================="
echo "Phase4cテスト実行スクリプト"
echo "=========================================="
echo ""
echo "ワークフローID: $WORKFLOW_ID"
echo "ワークフロー名: WF7 Phase4c - Perfect Implementation"
echo ""

# 実行履歴を確認
echo "📊 最新の実行履歴を確認中..."
echo ""

# 実行履歴を取得（最新5件）
echo "curl -X GET \"$N8N_URL/api/v1/executions?workflowId=$WORKFLOW_ID&limit=5\" \\"
echo "  -H \"Content-Type: application/json\""
echo ""

echo "=========================================="
echo "テスト実行後の確認コマンド"
echo "=========================================="
echo ""
echo "1. 実行履歴を確認:"
echo "   curl -X GET \"$N8N_URL/api/v1/executions?workflowId=$WORKFLOW_ID&limit=1\" \\"
echo "     -H \"Content-Type: application/json\""
echo ""
echo "2. 特定の実行IDの詳細を確認:"
echo "   curl -X GET \"$N8N_URL/api/v1/executions/{EXECUTION_ID}\" \\"
echo "     -H \"Content-Type: application/json\""
echo ""
echo "3. ワークフローの状態を確認:"
echo "   curl -X GET \"$N8N_URL/api/v1/workflows/$WORKFLOW_ID\" \\"
echo "     -H \"Content-Type: application/json\""
echo ""
echo "=========================================="
echo "n8n UIでの確認方法"
echo "=========================================="
echo ""
echo "1. ワークフローを開く:"
echo "   $N8N_URL/workflow/$WORKFLOW_ID"
echo ""
echo "2. 実行履歴タブで最新の実行を確認"
echo ""
echo "3. 各ノードの実行結果を確認:"
echo "   - Aggregate Videos: 7本の動画URLが集約されているか"
echo "   - Submit to FAL: request_idが取得できているか"
echo "   - Fetch Status: statusがCOMPLETEDになっているか"
echo "   - Download Video: 動画がダウンロードできているか"
echo "   - Upload to Google Drive: webViewLinkが取得できているか"
echo "   - Update Notion DB: Notion DBが更新されているか"
echo ""
echo "=========================================="

