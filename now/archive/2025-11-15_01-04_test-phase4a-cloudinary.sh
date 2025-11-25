#!/bin/bash

# Phase4a Cloudinaryアップロード機能テストスクリプト
# 作成日時: 2025-11-15 01:04:03 JST
#
# 目的: Phase4aエンドポイント(/generate-slide)がCloudinaryに画像をアップロードし、
#       image_urlフィールドを返すことを検証する
#
# 前提条件:
# - Railway fastapi-serverサービスに以下の環境変数が設定されていること
#   - CLOUDINARY_CLOUD_NAME
#   - CLOUDINARY_API_KEY
#   - CLOUDINARY_API_SECRET
# - サービスが再デプロイされていること

set -e

# 定数定義
RAILWAY_URL="https://fastapi-server-production-dc2b.up.railway.app"
ENDPOINT="/generate-slide"
TEST_SCRIPT_ID="test-cloudinary-$(date +%s)"
OUTPUT_DIR="/tmp/phase4a-cloudinary-test"

# 出力ディレクトリ作成
mkdir -p "$OUTPUT_DIR"

echo "=================================================="
echo "Phase4a Cloudinaryアップロード機能テスト"
echo "作成日時: 2025-11-15 01:04:03 JST"
echo "=================================================="
echo ""
echo "テスト設定:"
echo "  - エンドポイント: $RAILWAY_URL$ENDPOINT"
echo "  - スクリプトID: $TEST_SCRIPT_ID"
echo "  - 出力ディレクトリ: $OUTPUT_DIR"
echo ""

# テストケース定義
declare -a SECTIONS=("hook" "intro" "point1")
declare -a TEXTS=(
    "これは驚くべき発見です！"
    "本日のテーマをご紹介します"
    "第一のポイントは効率性です"
)
declare -a DURATIONS=(5 5 5)

echo "テストケース: ${#SECTIONS[@]}個のスライドを生成"
echo ""

# 各セクションをテスト
for i in "${!SECTIONS[@]}"; do
    section="${SECTIONS[$i]}"
    text="${TEXTS[$i]}"
    duration="${DURATIONS[$i]}"

    echo "[$((i+1))/${#SECTIONS[@]}] セクション: $section"
    echo "  - テキスト: $text"
    echo "  - 時間: ${duration}秒"

    # リクエストペイロード作成
    payload=$(cat <<EOF
{
  "section": "$section",
  "text": "$text",
  "duration": $duration,
  "script_id": "$TEST_SCRIPT_ID"
}
EOF
)

    # API呼び出し
    response_file="$OUTPUT_DIR/response_${section}.json"
    echo "  - API呼び出し中..."

    http_code=$(curl -s -w "%{http_code}" -X POST "$RAILWAY_URL$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        -o "$response_file")

    # HTTPステータスコード確認
    if [ "$http_code" != "200" ]; then
        echo "  ❌ エラー: HTTPステータスコード $http_code"
        echo "  レスポンス内容:"
        cat "$response_file" | jq '.' 2>/dev/null || cat "$response_file"
        exit 1
    fi

    echo "  ✅ HTTPステータスコード: $http_code"

    # レスポンス検証
    success=$(cat "$response_file" | jq -r '.success' 2>/dev/null)
    image_url=$(cat "$response_file" | jq -r '.image_url' 2>/dev/null)
    image_data=$(cat "$response_file" | jq -r '.imageData' 2>/dev/null)

    echo "  - success: $success"
    echo "  - image_url: ${image_url:0:60}..."
    echo "  - imageData: ${image_data:0:40}... (省略)"

    # 検証
    if [ "$success" != "true" ]; then
        echo "  ❌ エラー: success != true"
        exit 1
    fi

    if [ "$image_url" == "null" ] || [ -z "$image_url" ]; then
        echo "  ❌ 警告: image_urlがnullまたは空です"
        echo "  Cloudinaryアップロードが失敗している可能性があります"
        echo "  環境変数が正しく設定されているか確認してください:"
        echo "    - CLOUDINARY_CLOUD_NAME"
        echo "    - CLOUDINARY_API_KEY"
        echo "    - CLOUDINARY_API_SECRET"
        exit 1
    fi

    if [[ ! "$image_url" =~ ^https://res\.cloudinary\.com/ ]]; then
        echo "  ❌ エラー: image_urlがCloudinary URLではありません"
        echo "  実際の値: $image_url"
        exit 1
    fi

    echo "  ✅ image_url検証成功: Cloudinary URL"

    if [ "$image_data" == "null" ] || [ -z "$image_data" ]; then
        echo "  ❌ エラー: imageDataが空です（後方互換性エラー）"
        exit 1
    fi

    echo "  ✅ imageData検証成功: base64データ存在"
    echo ""
done

echo "=================================================="
echo "✅ すべてのテストが成功しました！"
echo "=================================================="
echo ""
echo "Cloudinary アップロード確認:"
echo "  - Cloudinaryダッシュボードを開いてください"
echo "  - フォルダ: wf7-slides/$TEST_SCRIPT_ID"
echo "  - 画像数: ${#SECTIONS[@]}枚"
echo ""
echo "レスポンスファイル:"
ls -lh "$OUTPUT_DIR"/response_*.json
echo ""
echo "次のステップ:"
echo "  1. Phase4b エンドポイントをテストして、image_urlが正しく使用されることを確認"
echo "  2. n8nワークフローWF7を更新して、Phase4a→4b自動パイプラインを実装"
echo ""
