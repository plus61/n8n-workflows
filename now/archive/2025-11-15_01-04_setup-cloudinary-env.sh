#!/bin/bash

# Cloudinary環境変数設定スクリプト（Railway CLI版）
# 作成日時: 2025-11-15 01:04:03 JST
#
# 目的: Railway fastapi-serverサービスにCloudinary環境変数を設定する
#
# 使用方法:
#   1. Cloudinary認証情報を準備
#      - Cloudinaryダッシュボード > Settings > Account で CLOUD_NAME を確認
#      - Cloudinaryダッシュボード > Settings > API Keys で API_KEY と API_SECRET を確認
#   2. このスクリプトを実行
#      ./setup-cloudinary-env.sh
#   3. プロンプトに従って認証情報を入力

set -e

echo "=================================================="
echo "Cloudinary環境変数設定（Railway CLI）"
echo "作成日時: 2025-11-15 01:04:03 JST"
echo "=================================================="
echo ""
echo "このスクリプトは、Railway fastapi-serverサービスに"
echo "Cloudinary環境変数を設定します。"
echo ""
echo "必要な情報:"
echo "  1. CLOUDINARY_CLOUD_NAME - CloudinaryのCloud Name"
echo "  2. CLOUDINARY_API_KEY    - CloudinaryのAPI Key"
echo "  3. CLOUDINARY_API_SECRET - CloudinaryのAPI Secret"
echo ""
echo "取得方法:"
echo "  - Cloudinaryダッシュボード > Settings > Account"
echo "  - Cloudinaryダッシュボード > Settings > API Keys"
echo ""
echo "=================================================="
echo ""

# 認証情報の入力
echo "Cloudinary認証情報を入力してください："
echo ""

read -p "CLOUDINARY_CLOUD_NAME: " CLOUD_NAME
read -p "CLOUDINARY_API_KEY: " API_KEY
read -s -p "CLOUDINARY_API_SECRET (非表示): " API_SECRET
echo ""
echo ""

# 入力検証
if [ -z "$CLOUD_NAME" ] || [ -z "$API_KEY" ] || [ -z "$API_SECRET" ]; then
    echo "❌ エラー: すべてのフィールドを入力してください"
    exit 1
fi

echo "入力内容を確認してください:"
echo "  CLOUDINARY_CLOUD_NAME: $CLOUD_NAME"
echo "  CLOUDINARY_API_KEY: $API_KEY"
echo "  CLOUDINARY_API_SECRET: ********"
echo ""

read -p "この内容でRailwayに設定しますか？ (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "キャンセルしました"
    exit 0
fi

echo ""
echo "=================================================="
echo "Railway環境変数を設定中..."
echo "=================================================="
echo ""

# Railway CLI で環境変数を一括設定
# 複数の --set オプションを1つのコマンドで実行できます
echo "Cloudinary環境変数を設定中（3つの変数を一括設定）..."

railway variables \
  --service fastapi-server \
  --set "CLOUDINARY_CLOUD_NAME=$CLOUD_NAME" \
  --set "CLOUDINARY_API_KEY=$API_KEY" \
  --set "CLOUDINARY_API_SECRET=$API_SECRET"

echo ""
echo "=================================================="
echo "✅ 環境変数の設定が完了しました！"
echo "=================================================="
echo ""
echo "設定された環境変数:"
echo "  - CLOUDINARY_CLOUD_NAME"
echo "  - CLOUDINARY_API_KEY"
echo "  - CLOUDINARY_API_SECRET"
echo ""
echo "次のステップ:"
echo "  1. Railway fastapi-serverサービスが自動的に再デプロイされます"
echo "     （数分かかる場合があります）"
echo ""
echo "  2. 再デプロイ完了を確認:"
echo "     railway logs --service fastapi-server"
echo ""
echo "  3. 環境変数が正しく設定されているか確認:"
echo "     railway variables --service fastapi-server | grep CLOUDINARY"
echo ""
echo "  4. Phase4aエンドポイントをテスト:"
echo "     ./now/2025-11-15_01-04_test-phase4a-cloudinary.sh"
echo ""
