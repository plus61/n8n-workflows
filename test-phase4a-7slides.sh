#!/bin/bash

# WF7 Phase4a 7枚画像生成テスト実行スクリプト
# 作成日: 2025-11-08

# Webhook URL
WEBHOOK_URL="https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script"

# テスト用NotionページID（引数で指定、または環境変数から取得）
NOTION_PAGE_ID="${1:-${NOTION_PAGE_ID}}"

if [ -z "$NOTION_PAGE_ID" ]; then
    echo "❌ エラー: NotionページIDが指定されていません"
    echo ""
    echo "使用方法:"
    echo "  ./test-phase4a-7slides.sh YOUR_NOTION_PAGE_ID"
    echo ""
    echo "または環境変数を設定:"
    echo "  export NOTION_PAGE_ID=your-page-id"
    echo "  ./test-phase4a-7slides.sh"
    exit 1
fi

echo "🚀 WF7 Phase4a テスト実行を開始します..."
echo ""
echo "📋 設定情報:"
echo "  Webhook URL: ${WEBHOOK_URL}"
echo "  Notion Page ID: ${NOTION_PAGE_ID}"
echo ""

# テスト実行
echo "📤 Webhookをトリガーしています..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{\"notionPageId\": \"${NOTION_PAGE_ID}\"}")

# HTTPステータスコードを取得
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo ""
echo "📥 レスポンス:"
echo "  HTTP Status: ${HTTP_CODE}"
echo "  Response Body:"
echo "${BODY}" | jq '.' 2>/dev/null || echo "${BODY}"

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo ""
    echo "✅ Webhook呼び出し成功"
    echo ""
    echo "📊 次のステップ:"
    echo "  1. n8n UIでワークフロー 'WF7 Phase4 - V3 Fixed' を開く"
    echo "  2. 実行履歴を確認"
    echo "  3. 以下のノードの出力を確認:"
    echo "     - Code - Generate Slides with Pillow: 7枚のスライドが生成されているか"
    echo "     - Split Out - Individual Slides: 7つのアイテムに分割されているか"
    echo "     - Google Drive - Upload Slide Image: 7枚の画像がアップロードされているか"
    echo "     - Aggregate - Combine All Slides: 7枚の結果が統合されているか"
    echo "     - Set - Phase4a Payload New: slides_count=7, phase4a_success=true"
else
    echo ""
    echo "❌ Webhook呼び出し失敗 (HTTP ${HTTP_CODE})"
    echo ""
    echo "🔍 トラブルシューティング:"
    echo "  1. NotionページIDが正しいか確認"
    echo "  2. ワークフローがアクティブか確認"
    echo "  3. Webhook URLが正しいか確認"
    exit 1
fi

