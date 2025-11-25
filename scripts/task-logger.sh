#!/bin/bash

# タスクログシステム
# 使用方法: ./task-logger.sh start "タスク名" または ./task-logger.sh end "タスク名"

DAILY_DIR="/Users/yuichiroooosuger/Desktop/2rd_brain/Daily"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="${DAILY_DIR}/${TODAY}.md"

# ログファイルが存在しない場合は作成
if [ ! -f "$LOG_FILE" ]; then
    cat > "$LOG_FILE" << EOF
# ${TODAY}

## 📋 タスクログ

EOF
    echo "✅ ログファイル作成: $LOG_FILE"
fi

# タスクログセクションが存在しない場合は追加
if ! grep -q "## 📋 タスクログ" "$LOG_FILE"; then
    echo "" >> "$LOG_FILE"
    echo "## 📋 タスクログ" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi

# 引数チェック
if [ $# -lt 2 ]; then
    echo "❌ エラー: 引数が不足しています"
    echo "使用方法:"
    echo "  タスク開始: ./task-logger.sh start \"タスク名\""
    echo "  タスク完了: ./task-logger.sh end \"タスク名\""
    exit 1
fi

ACTION=$1
TASK_NAME=$2
TIMESTAMP=$(date +"%H:%M:%S")

case $ACTION in
    start|s)
        # ファイル末尾にタスク開始を追記
        echo "" >> "$LOG_FILE"
        echo "### 🔄 ${TASK_NAME}" >> "$LOG_FILE"
        echo "- **開始**: ${TIMESTAMP}" >> "$LOG_FILE"
        echo "✅ タスク開始を記録: $TASK_NAME ($TIMESTAMP)"
        ;;
    end|e)
        # タスク名に一致する最後のタスクに完了時刻を追加
        if grep -q "### 🔄 ${TASK_NAME}" "$LOG_FILE"; then
            # awkを使って、タスク名の直後の行（開始時刻の行）の後に完了時刻を追加
            awk -v task="### 🔄 ${TASK_NAME}" -v end="- **完了**: ${TIMESTAMP}" '
                $0 ~ task {
                    found=1
                    print
                    next
                }
                found && /- \*\*開始\*\*:/ {
                    print
                    print end
                    found=0
                    next
                }
                found && /^###/ {
                    found=0
                    print
                    next
                }
                { print }
            ' "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE" || {
                # awkが失敗した場合は末尾に追記
                echo "- **完了**: ${TIMESTAMP}" >> "$LOG_FILE"
            }
        else
            # タスク名が見つからない場合は末尾に追記
        echo "- **完了**: ${TIMESTAMP}" >> "$LOG_FILE"
        fi
        echo "✅ タスク完了を記録: $TASK_NAME ($TIMESTAMP)"
        ;;
    *)
        echo "❌ エラー: 無効なアクション '$ACTION'"
        echo "使用方法: start/s (開始) または end/e (完了)"
        exit 1
        ;;
esac

# ログファイルの最後の5行を表示
echo ""
echo "📋 最新のログ:"
tail -n 5 "$LOG_FILE"
