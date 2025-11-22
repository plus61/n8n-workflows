# Google Spreadsheet MCP サーバー導入ガイド

**作成日時**: 2025-11-22 13:32:29 JST

## ✅ 完了した手順

### 1. MCPサーバーバイナリのインストール
```bash
go install github.com/kazz187/mcp-google-spreadsheet@latest
```

**インストール先**: `~/go/bin/mcp-google-spreadsheet`

### 2. Go環境確認
- Go version: 1.25.4
- GOPATH: `/Users/yuichiroooosuger/go`

---

## 📋 次のステップ：Google Cloud認証設定

### Step 1: Google Cloud Platformプロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）

### Step 2: 必要なAPIの有効化

以下の2つのAPIを有効化します：

1. **Google Drive API**
   - https://console.cloud.google.com/apis/library/drive.googleapis.com
   - 「APIを有効にする」をクリック

2. **Google Sheets API**
   - https://console.cloud.google.com/apis/library/sheets.googleapis.com
   - 「APIを有効にする」をクリック

### Step 3: OAuth 2.0クライアントIDの作成

1. [認証情報ページ](https://console.cloud.google.com/apis/credentials)に移動
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類：「デスクトップアプリ」を選択
4. 名前：任意（例：`Claude Code MCP`）
5. 「作成」をクリック
6. **client_secret.json**をダウンロード

### Step 4: 認証ファイルの配置

ダウンロードした`client_secret.json`を安全な場所に保存します：

```bash
# 推奨ディレクトリ作成
mkdir -p ~/.config/mcp-google-spreadsheet

# ダウンロードしたファイルを移動
mv ~/Downloads/client_secret_*.json ~/.config/mcp-google-spreadsheet/client_secret.json
```

### Step 5: Google Driveフォルダの準備

1. Google Driveで操作対象となるフォルダを作成または選択
2. フォルダURLからフォルダIDを取得
   - URL例：`https://drive.google.com/drive/folders/1Abc...XYZ`
   - フォルダID：`1Abc...XYZ`（最後の部分）

---

## 🔧 Claude Code設定（次のステップ）

### Claude Desktop設定ファイルの編集

macOSの場合：
```bash
# 設定ファイルの場所
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 設定内容（例）

```json
{
  "mcpServers": {
    "google-spreadsheet": {
      "command": "/Users/yuichiroooosuger/go/bin/mcp-google-spreadsheet",
      "args": [],
      "env": {
        "MCPGS_CLIENT_SECRET_PATH": "/Users/yuichiroooosuger/.config/mcp-google-spreadsheet/client_secret.json",
        "MCPGS_TOKEN_PATH": "/Users/yuichiroooosuger/.config/mcp-google-spreadsheet/token.json",
        "MCPGS_FOLDER_ID": "YOUR_FOLDER_ID_HERE"
      }
    }
  }
}
```

**注意**：
- `YOUR_FOLDER_ID_HERE` は実際のGoogle DriveフォルダIDに置き換えてください
- `token.json`は初回認証時に自動生成されます

---

## 🚀 初回起動と認証

1. Claude Codeを再起動
2. 初回起動時にブラウザが開き、Googleアカウント認証を求められます
3. アカウントを選択し、権限を許可
4. 認証が完了すると`token.json`が自動生成されます

---

## 📝 利用可能な機能

このMCPサーバーをインストールすると、Claude Codeから以下の操作が可能になります：

- Google Spreadsheetの読み取り
- Google Spreadsheetへの書き込み
- スプレッドシートの作成
- セルの更新
- シート情報の取得

---

## ⚠️ トラブルシューティング

### 認証エラーが発生する場合

1. `client_secret.json`のパスが正しいか確認
2. Google Cloud ConsoleでAPIが有効化されているか確認
3. OAuth同意画面の設定が完了しているか確認

### MCPサーバーが起動しない場合

```bash
# バイナリが正しくインストールされているか確認
ls -la ~/go/bin/mcp-google-spreadsheet

# 実行権限があるか確認
chmod +x ~/go/bin/mcp-google-spreadsheet

# 直接実行してエラーメッセージを確認
~/go/bin/mcp-google-spreadsheet
```

---

## 📚 参考リンク

- リポジトリ: https://github.com/kazz187/mcp-google-spreadsheet
- Google Cloud Console: https://console.cloud.google.com/
- Google Drive API: https://developers.google.com/drive
- Google Sheets API: https://developers.google.com/sheets
