#!/bin/bash

# now フォルダの整理スクリプト
# 作業終了時にファイルを適切なディレクトリに振り分ける

set -e

NOW_DIR="./now"
WORKFLOWS_DIR="./workflows"
DOCS_DIR="./docs"
SCRIPTS_DIR="./scripts"
DATA_DIR="./data"

# 色付きメッセージ
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  now フォルダ整理スクリプト${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# now フォルダの存在確認
if [ ! -d "$NOW_DIR" ]; then
    echo "Error: now フォルダが存在しません"
    exit 1
fi

# ファイル数確認（状態管理ファイルを除外）
FILE_COUNT=$(find "$NOW_DIR" -type f ! -name "README.md" ! -name "CURRENT_STATE.md" ! -name "DECISIONS.md" | wc -l | tr -d ' ')

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "整理するファイルがありません。"
    exit 0
fi

echo "整理対象ファイル数: $FILE_COUNT"
echo ""

# 確認プロンプト
read -p "ファイルを整理しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました。"
    exit 0
fi

echo ""

# ディレクトリ作成
mkdir -p "$WORKFLOWS_DIR"
mkdir -p "$DOCS_DIR"/{design,implementation,testing,verification,knowledge}
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$DATA_DIR"

# ファイル分類関数
classify_markdown() {
    local file="$1"
    local content=$(cat "$file")

    # キーワードマッチング（優先順位順）
    if echo "$content" | grep -qiE "(設計|デザイン|仕様|アーキテクチャ|設計書)"; then
        echo "$DOCS_DIR/design"
    elif echo "$content" | grep -qiE "(実装|手順|計画|Todo|実装計画)"; then
        echo "$DOCS_DIR/implementation"
    elif echo "$content" | grep -qiE "(テスト|検証|結果|実行|テスト結果)"; then
        echo "$DOCS_DIR/testing"
    elif echo "$content" | grep -qiE "(検証|チェックリスト|確認|検証レポート)"; then
        echo "$DOCS_DIR/verification"
    elif echo "$content" | grep -qiE "(知識|ナレッジ|ベストプラクティス|Tips)"; then
        echo "$DOCS_DIR/knowledge"
    else
        echo "$DOCS_DIR"
    fi
}

is_n8n_workflow() {
    local file="$1"
    # n8nワークフロー構造を持つか確認
    if jq -e '.nodes and .connections' "$file" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# ファイル整理
MOVED_COUNT=0

for file in "$NOW_DIR"/*; do
    # 状態管理ファイルとREADME.mdはスキップ
    filename=$(basename "$file")
    if [ "$filename" == "README.md" ] || [ "$filename" == "CURRENT_STATE.md" ] || [ "$filename" == "DECISIONS.md" ]; then
        continue
    fi

    if [ ! -f "$file" ]; then
        continue
    fi

    extension="${filename##*.}"

    case "$extension" in
        json)
            # n8nワークフローかデータファイルか判定
            if is_n8n_workflow "$file"; then
                target_dir="$WORKFLOWS_DIR"
                echo -e "${GREEN}✓${NC} $filename → workflows/"
            else
                target_dir="$DATA_DIR"
                echo -e "${GREEN}✓${NC} $filename → data/"
            fi
            ;;
        md)
            # Markdownファイルの分類
            target_dir=$(classify_markdown "$file")
            relative_path=${target_dir#./docs/}
            if [ "$relative_path" == "docs" ]; then
                echo -e "${GREEN}✓${NC} $filename → docs/"
            else
                echo -e "${GREEN}✓${NC} $filename → docs/$relative_path/"
            fi
            ;;
        sh|py)
            # スクリプトファイル
            if [[ "$filename" == test-* ]]; then
                target_dir="."
                echo -e "${GREEN}✓${NC} $filename → ./ (テストスクリプト)"
            else
                target_dir="$SCRIPTS_DIR"
                echo -e "${GREEN}✓${NC} $filename → scripts/"
            fi
            ;;
        *)
            # その他のファイル
            target_dir="$DATA_DIR"
            echo -e "${YELLOW}?${NC} $filename → data/ (その他)"
            ;;
    esac

    # ファイル移動（同名ファイルがある場合はタイムスタンプを付加）
    if [ -f "$target_dir/$filename" ]; then
        timestamp=$(date +%Y%m%d_%H%M%S)
        name="${filename%.*}"
        ext="${filename##*.}"
        new_filename="${name}_${timestamp}.${ext}"
        mv "$file" "$target_dir/$new_filename"
        echo -e "  ${YELLOW}→ 同名ファイルが存在するため ${new_filename} にリネーム${NC}"
    else
        mv "$file" "$target_dir/"
    fi

    ((MOVED_COUNT++))
done

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}整理完了: ${MOVED_COUNT} ファイルを移動しました${NC}"
echo -e "${BLUE}================================================${NC}"
