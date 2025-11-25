#!/bin/bash

# WF10 Webhook Railway再デプロイ後検証スクリプト
# 作成日時: 2025-11-23 08:50:08 JST

set -e

WEBHOOK_URL="https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger"
TEST_PAGE_ID="2b368d5c2986811f87ecf2aecaedf1cf"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "WF10 Webhook Railway再デプロイ後検証"
echo "実行日時: $(date +"%Y-%m-%d %H:%M:%S %Z")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: ヘルスチェック
echo "🔍 Step 1: Webhookエンドポイント疎通確認"
echo "URL: $WEBHOOK_URL"
echo ""

HTTP_STATUS=$(curl -I -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" || echo "ERROR")

if [ "$HTTP_STATUS" == "200" ]; then
  echo "✅ ヘルスチェック成功: HTTP $HTTP_STATUS"
else
  echo "❌ ヘルスチェック失敗: HTTP $HTTP_STATUS"
  echo "⚠️  Railway再デプロイが完了していない可能性があります"
  echo "   30秒待機してから再実行してください"
  exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 2: 30秒待機（n8n初期化完了まで）
echo "⏳ Step 2: n8n初期化完了待機（30秒）"
for i in {30..1}; do
  echo -ne "\r残り ${i} 秒...  "
  sleep 1
done
echo -e "\r✅ 待機完了       "
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 3: 9回目E2Eテスト実行
echo "🚀 Step 3: 9回目E2Eテスト実行"
echo "Notion Page ID: $TEST_PAGE_ID"
echo ""

RESPONSE_FILE="now/2025-11-23_08-50_e2e-test-9th-response.json"

echo "リクエスト送信中..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"page_id\": \"$TEST_PAGE_ID\"}" \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  "$WEBHOOK_URL" > "$RESPONSE_FILE" 2>&1

echo ""
echo "✅ レスポンス保存: $RESPONSE_FILE"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 4: 検証結果表示
echo "📊 Step 4: 検証結果"
echo ""
echo "次のステップ:"
echo "1. n8n UIにアクセスして実行履歴を確認"
echo "   railway open → n8nサービス → 'Open App' → Executions"
echo ""
echo "2. Share File nodeの詳細確認（最重要）"
echo "   ✅ 使用パラメータ: permissionsInput, role, type"
echo "   ❌ 使用していないこと: permissionsUi"
echo "   ✅ Google Drive APIエラーがないこと"
echo ""
echo "3. 全14ノードの実行結果確認"
echo "   目標: 全ノード成功（緑色のチェックマーク）"
echo ""
echo "4. Notionページ更新確認"
echo "   ✅ Video_URL: 動画URLが記録されている"
echo "   ✅ Status: 'Completed' に更新されている"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 検証スクリプト完了"
echo "詳細な実行結果は手動で確認してください"
echo ""
