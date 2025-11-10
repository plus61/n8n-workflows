#!/bin/bash

# WF7 Phase4b修正後の統合テスト実行スクリプト
# 作成日: 2025-11-09
# 目的: Phase4b修正後のE2Eテストを実行し、結果を記録する

set -e

# 設定
N8N_WEBHOOK_URL="https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script"
NOTION_PAGE_ID="${1:-2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9}"
TEST_NAME="Phase4b修正後統合テスト"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="test-phase4b-fixed-e2e-${TIMESTAMP}.log"

echo "========================================="
echo "${TEST_NAME}"
echo "========================================="
echo "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Notion Page ID: ${NOTION_PAGE_ID}"
echo "Webhook URL: ${N8N_WEBHOOK_URL}"
echo "ログファイル: ${LOG_FILE}"
echo "========================================="
echo ""

# Webhook呼び出し
echo "[$(date '+%H:%M:%S')] Webhook呼び出し開始..."
echo ""

RESPONSE=$(curl -X POST "${N8N_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"notionPageId\": \"${NOTION_PAGE_ID}\"
  }" \
  -w "\n%{http_code}" \
  -s)

HTTP_CODE=$(echo "${RESPONSE}" | tail -n1)
BODY=$(echo "${RESPONSE}" | sed '$d')

echo "[$(date '+%H:%M:%S')] HTTPステータスコード: ${HTTP_CODE}"
echo "[$(date '+%H:%M:%S')] レスポンス:"
echo "${BODY}" | jq '.' 2>/dev/null || echo "${BODY}"
echo ""

# 結果をログファイルに記録
{
  echo "========================================="
  echo "${TEST_NAME}"
  echo "========================================="
  echo "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Notion Page ID: ${NOTION_PAGE_ID}"
  echo "Webhook URL: ${N8N_WEBHOOK_URL}"
  echo "HTTPステータスコード: ${HTTP_CODE}"
  echo "レスポンス:"
  echo "${BODY}" | jq '.' 2>/dev/null || echo "${BODY}"
  echo ""
} >> "${LOG_FILE}"

# 結果判定
if [ "${HTTP_CODE}" -eq 200 ]; then
  echo "✅ Webhook呼び出し成功"
  echo ""
  echo "次のステップ:"
  echo "1. n8n UIで実行ログを確認してください"
  echo "2. 各フェーズ（Phase4a/4b/4c）の実行状況を確認してください"
  echo "3. Google Driveに最終動画がアップロードされているか確認してください"
  echo "4. Notion DBが正しく更新されているか確認してください"
  echo ""
  echo "実行ログの確認URL:"
  echo "https://n8n-python-production-344b.up.railway.app/workflow/r9Sp5n0mkUCcH8cw/executions"
  echo ""
else
  echo "❌ Webhook呼び出し失敗 (HTTP ${HTTP_CODE})"
  echo ""
  echo "エラー内容を確認してください:"
  echo "${BODY}"
  echo ""
fi

echo "ログファイル: ${LOG_FILE}"
echo ""

