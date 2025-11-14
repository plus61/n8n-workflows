# Phase4a テストデータ

## 📋 Notionページに設定するプロパティ

### 基本情報
- **Page Title**: Phase4a Test Script
- **Status**: Draft（任意）

### 台本データプロパティ（Rich Text形式）

#### hook_text_5options
配列形式で5つのオプションを設定（最初のものが使用されます）:
```json
["今すぐ成功したい人へ", "失敗から学ぶ方法", "時間を有効活用する秘訣", "人生を変える習慣", "今日から始める自己改善"]
```

または単純な文字列:
```
今すぐ成功したい人へ
```

#### introduction_text
```
この動画では、成功するための3つの重要なポイントをご紹介します。
```

#### main_point_1
```
まず1つ目は、明確な目標設定です。目標がなければ、どこに向かっているのかわかりません。
```

#### main_point_2
```
2つ目は、継続的な学習です。毎日少しずつでも学び続けることが成功への近道です。
```

#### main_point_3
```
最後に、行動力です。知識だけでは不十分で、実際に行動に移すことが最も重要です。
```

#### summary_text
```
この3つのポイントを実践すれば、必ず成功に近づくことができます。今日から始めましょう！
```

#### cta_text_3options
配列形式で3つのオプションを設定（最初のものが使用されます）:
```json
["今すぐチャンネル登録", "詳細はリンクから", "無料ガイドをダウンロード"]
```

または単純な文字列:
```
今すぐチャンネル登録
```

### オプションプロパティ（JSON形式）

#### Brand Colors (JSON)
```json
{
  "background": "#1a1a2e",
  "primary_text": "#ffffff",
  "secondary_text": "#aaaaaa",
  "accent": "#00d4ff",
  "cta_bg": "#ff6b6b",
  "cta_text": "#ffffff"
}
```

#### Visual Elements (JSON)
```json
{
  "hook": {
    "icon": "⚠️"
  },
  "point1": {
    "icon": "🎯"
  },
  "point2": {
    "icon": "📚"
  },
  "point3": {
    "icon": "⚡"
  }
}
```

#### Duration Config (JSON)
```json
{
  "hook": 3,
  "intro": 10,
  "point1": 13,
  "point2": 13,
  "point3": 14,
  "summary": 20,
  "cta": 7
}
```

#### Motion Prompts (JSON)
```json
{
  "hook": "dramatic zoom in effect, professional business style, sharp focus",
  "intro": "smooth slide transition, calm professional tone, steady camera",
  "point1": "gentle fade in with subtle zoom, educational style, clean motion",
  "point2": "gentle fade in with subtle zoom, educational style, clean motion",
  "point3": "gentle fade in with subtle zoom, educational style, clean motion",
  "summary": "cinematic pan effect, inspiring tone, smooth movement",
  "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
}
```

## 🚀 テスト実行手順

### ステップ1: Notionページの作成
1. Notion Hubデータベースに新しいページを作成
2. 上記のプロパティをすべて設定
3. ページIDをコピー（URLから取得: `https://www.notion.so/xxx...xxx`）

### ステップ2: Webhookトリガー
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "YOUR_PAGE_ID_HERE"}'
```

### ステップ3: n8n UI で確認
1. n8n UIでワークフロー「WF7 Phase4 - V3 Fixed」を開く
2. 実行履歴を確認
3. 各ノードの出力をチェック:
   - **Code - Generate Slides with Pillow**: 7枚のスライドデータ（Base64）
   - **Split Out - Individual Slides**: 7つのアイテムに分割
   - **Code - Convert to Binary**: バイナリデータ変換
   - **Google Drive - Upload Slide Image**: 7枚のアップロード結果
   - **Aggregate - Combine All Slides**: 統合結果（7枚）
   - **Set - Phase4a Payload New**: `slides_count: 7`, `phase4a_success: true`

### ステップ4: Google Driveで確認
1. Google Driveの指定フォルダを開く
2. 以下のファイル名で7枚の画像が存在することを確認:
   - `slide_1_hook.png`
   - `slide_2_intro.png`
   - `slide_3_point1.png`
   - `slide_4_point2.png`
   - `slide_5_point3.png`
   - `slide_6_summary.png`
   - `slide_7_cta.png`

## ✅ 期待される結果

1. **スライド生成成功**: 7枚すべてのスライドが生成される
2. **画像形式**: PNG, 1080x1920ピクセル
3. **テキスト表示**: 日本語テキストが正しく表示される
4. **Google Driveアップロード**: 7枚すべてアップロード成功
5. **データ統合**: `slides_metadata`配列に7つの要素
6. **IF条件通過**: `phase4a_success: true`, `slides_count: 7`

## 🔍 トラブルシューティング

### 問題1: Code Nodeエラー
- **原因**: Pillowライブラリまたはフォントファイルが見つからない
- **解決**: Railway環境にNoto Sans JPフォントがインストールされているか確認

### 問題2: 画像が生成されない
- **原因**: Notionプロパティ名が一致していない
- **解決**: プロパティ名のスペルと大文字小文字を確認

### 問題3: Google Driveアップロード失敗
- **原因**: 認証情報の期限切れ
- **解決**: n8n UIでGoogle Drive認証情報を再認証

### 問題4: 7枚未満のスライド
- **原因**: データ統合ノードの出力構造が不正
- **解決**: `データ統合`ノードの出力を確認し、必要なプロパティが含まれているか確認
