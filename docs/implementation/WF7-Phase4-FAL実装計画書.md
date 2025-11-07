# 🎯 WF7 Phase 4: FAL.ai実装 設計計画書

**作成日**: 2025-11-06
**目的**: FAL.ai認証テスト完了後の具体的な実装手順と修正計画の策定
**バージョン**: 1.0

---

## 📊 現状分析

### 現在の実装状況

```yaml
Railway n8n環境:
  ✅ デプロイ成功（コミット f9064eb）
  ✅ n8n 1.118.2 稼働中
  ✅ FFmpeg + Noto Sans JPフォント インストール済み
  ✅ Python環境（Code Node対応）
  ✅ URL: https://n8n-python-production-344b.up.railway.app/

既存WF7 Phase4:
  - Workflow ID: xvlnFeJJwHKMHBwK
  - 現在の実装: fal.ai FFmpeg API使用
  - 状態: 稼働中

認証テスト:
  ⏳ FAL.ai API認証テスト実施中
  ⏳ 結果待ち
```

### 実装方針の確認

```yaml
ハイブリッドアプローチ:
  Phase 4a: Pillowでスライド画像生成（7枚）
  Phase 4b: FAL Image-to-Videoで動画化（7本）
  Phase 4c: FFmpegで結合（1本の完成動画）

コスト削減効果:
  Creatomate比: 70-84%削減
  月間コスト: $39.20（70本想定）
  レンダリング単価: $0.56/本

工数見積もり:
  Phase 4a: 2🍅
  Phase 4b: 2🍅
  Phase 4c: 1🍅
  E2Eテスト: 1🍅
  合計: 6🍅（約1.6時間）
```

---

## 🔧 実装計画

### 前提条件の確認

**✅ すでに完了している項目**:
1. Railway環境のセットアップ（FFmpeg, Noto Sans JPフォント）
2. n8n専用Dockerfileの確立
3. Python Code Node環境の準備

**⏳ 認証テスト後に実施する項目**:
1. FAL API Key取得・設定
2. n8n Credentials登録
3. 初回動画生成テスト

---

## 📋 Phase 2-3への修正要求

### 1. Notion DBスキーマ更新

**追加カラム**（Phase 4a用）:

```yaml
新規カラム:
  motion_prompts:
    - Type: JSON
    - 説明: 各スライドの動きプロンプト（7種類）
    - 例: {"hook": "dramatic zoom in effect", "intro": "smooth slide transition", ...}

  duration_config:
    - Type: JSON
    - 説明: 各セクションの秒数設定
    - 例: {"hook": 3, "intro": 10, "point1": 13, ...}

  visual_elements:
    - Type: JSON
    - 説明: アイコン・図解の指定
    - 例: {"hook": {"icon": "⚠️", "position": "top-center"}, ...}

  brand_colors:
    - Type: JSON
    - 説明: ブランドカラー設定
    - 例: {"background": "#1a1a2e", "primary_text": "#ffffff", ...}

  font_sizes:
    - Type: JSON（オプション）
    - 説明: フォントサイズ設定
```

**実装方法**:
- Notion API経由でプロパティを追加
- または Notion Web UIで手動追加

---

### 2. ChatGPTプロンプトへのSTEP11追加

**Phase 2-3のChatGPT プロンプトに以下を追加**:

```markdown
## STEP11: 動きのプロンプト生成

各セクションの動画に適した「動きのプロンプト」を生成します。

**各セクションの推奨される動き**:

1. **フック（3秒）**:
   - 目的: 視聴者の注意を一瞬で引く
   - 推奨: ズームイン、ドラマチックな登場
   - 例: "dramatic zoom in effect, professional business style, sharp focus"

2. **導入（10秒）**:
   - 目的: 視聴者の悩みに共感し、動画の価値を示す
   - 推奨: スムーズなスライド、落ち着いたトーン
   - 例: "smooth slide transition, calm professional tone, steady camera"

3. **本編（13秒×3）**:
   - 目的: 3つの要点を明確に伝える
   - 推奨: フェードイン、軽いズーム、教育的な雰囲気
   - 例: "gentle fade in with subtle zoom, educational style, clean motion"

4. **まとめ（20秒）**:
   - 目的: 得られる未来を描き、信頼感を与える
   - 推奨: シネマティックなパン、インスピレーショナル
   - 例: "cinematic pan effect, inspiring tone, smooth movement"

5. **CTA（7秒）**:
   - 目的: 行動を促す
   - 推奨: パルス効果、緊急感、注目を引く
   - 例: "pulsing call-to-action, urgent professional, attention-grabbing"

**出力形式（JSON）**:
```json
{
  "hook": "...",
  "intro": "...",
  "point1": "...",
  "point2": "...",
  "point3": "...",
  "summary": "...",
  "cta": "..."
}
```
```

---

## 🔧 Phase 4の詳細実装計画

### Phase 4a: スライド画像生成（2🍅）

#### n8nワークフロー構成

```yaml
Node 1: Webhook Trigger
  - Path: /webhook-test/wf7-phase4a-slides
  - Method: POST
  - 説明: 外部からの実行トリガー

Node 2: Notion Database Query
  - Database: WF7_Scripts
  - Filter: status = "approved"
  - Sort: created_at DESC
  - Limit: 1
  - 説明: 最新の承認済み台本を取得

Node 3: Code Node (Python) - Slide Generator
  - 機能: 7枚のスライド画像を生成
  - 入力: Notion DBのデータ
  - 出力: 7つのbase64画像 + メタデータ
  - ライブラリ: Pillow, textwrap, base64

Node 4: Split Out (1→7)
  - 7枚の画像を個別アイテムに分割
  - 各アイテムに section, duration, image_base64 を含む

Node 5: HTTP Request - Upload to Google Drive
  - Method: POST
  - URL: Google Drive API
  - Body: image_base64 → file upload
  - 出力: Google Drive File ID + URL

Node 6: Aggregate
  - 7枚の画像URLを配列に結合
  - 順序保持（hook→intro→point1-3→summary→cta）

Node 7: Set Variables
  - slides配列を整形
  - Phase 4bへの準備
```

#### Pythonコード実装（Node 3）

**実装場所**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/phase4a_slide_generator.py`

**主要機能**:
- Pillowで1080x1920の縦型画像生成
- Noto Sans JPフォント使用
- テキスト折り返し、中央配置
- アイコン・ラベル・秒数表示
- base64エンコード出力

**フォントパス**: `/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf`（Railway環境で利用可能）

**出力形式**:
```json
[
  {
    "section": "hook",
    "duration": 3,
    "image_base64": "iVBORw0KGgoAAAANSUhEUg...",
    "filename": "slide_1_hook.png"
  },
  ...
]
```

**テスト手順**:
1. 手動でWebhookをトリガー
2. 生成された7枚の画像を確認
3. テキスト配置、フォント、色を検証

---

### Phase 4b: FAL Image-to-Video（2🍅）

#### n8nワークフロー構成

```yaml
Node 1: Loop Over Items
  - 入力: Phase 4aの7枚の画像URL
  - 各画像に対して処理

Node 2: Set - Prepare FAL Request
  - image_url: {{$json.image_url}}
  - duration: {{$json.duration}}
  - motion_prompt: {{$json.motion_prompt}}
  - section: {{$json.section}}

Node 3: HTTP Request - FAL Submit
  - URL: https://fal.run/fal-ai/stable-video-diffusion
  - Method: POST
  - Authentication: Header Auth
    - Name: Authorization
    - Value: Key {{$credentials.fal_api_key}}
  - Body (JSON):
    {
      "image_url": "={{$json.image_url}}",
      "motion_bucket_id": 127,
      "cond_aug": 0.02,
      "num_frames": "={{$json.duration * 8}}",
      "num_inference_steps": 25,
      "fps": 8,
      "seed": "={{Math.floor(Math.random() * 1000000)}}",
      "prompt": "={{$json.motion_prompt}}"
    }
  - 出力: request_id

Node 4: Wait
  - Duration: 10秒
  - 理由: FALのレンダリング開始待ち

Node 5: Loop - Check Status
  - Condition: {{$json.status}} !== "succeeded" AND {{$runIndex}} < 30
  - HTTP Request - Get Status:
    - URL: https://fal.run/fal-ai/stable-video-diffusion/{{$json.request_id}}
    - Method: GET
    - Authentication: 同上
  - Wait Between Checks: 10秒
  - 最大試行: 30回（5分）

Node 6: IF - Check Success
  - Condition: {{$json.status}} === "succeeded"
  - True: Extract Video URL
  - False: Error Handler

Node 7: Extract Video URL
  - video_url: {{$json.video.url}}
  - section: {{$json.section}}
  - duration: {{$json.duration}}

Node 8: Aggregate
  - 7本の動画URLを配列に結合
  - 順序保持
```

#### 認証設定（FAL API）

**n8n Credentials設定**:
```yaml
Credential Type: Header Auth
Name: FAL API Key
Header Name: Authorization
Header Value: Key YOUR_FAL_API_KEY
```

**テスト手順**:
1. FAL.ai API認証テスト完了後、Credentialsに登録
2. 1枚の画像で動画生成テスト
3. ステータスポーリングの動作確認
4. 7枚すべての動画生成テスト

---

### Phase 4c: FFmpeg結合（1🍅）

#### n8nワークフロー構成

```yaml
Node 1: Aggregate Videos
  - 入力: Phase 4bの7本の動画URL配列
  - 順序確認（hook→intro→point1-3→summary→cta）

Node 2: Code Node (Python) - FFmpeg Concat
  - 機能: 7本の動画をダウンロード → 結合
  - 出力: 1本の完成動画（ローカルファイル）

Node 3: HTTP Request - Upload to Google Drive
  - 完成動画をGoogle Driveにアップロード
  - 出力: final_video_url

Node 4: HTTP Request - Update Notion DB
  - Database: WF7_Scripts
  - Update: status = "completed"
  - Add: final_video_url

Node 5: Webhook Response
  - 成功メッセージを返す

Node 6: Trigger Phase 5
  - Phase 5（SNS投稿）ワークフローを起動
```

#### Pythonコード実装（Node 2）

**実装場所**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/phase4c_ffmpeg_concat.py`

**主要機能**:
- requests で動画ダウンロード
- filelist.txt作成
- ffmpeg -f concat 実行
- 一時ファイルのクリーンアップ

**タイムアウト設定**: 600秒（コミット `213f551` で確立）

**FFmpegコマンド**:
```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

**テスト手順**:
1. 7本のテスト動画URLを用意
2. ダウンロード→結合の動作確認
3. 完成動画の品質チェック
4. ファイルサイズ・秒数の検証

---

## 🧪 E2Eテスト計画（1🍅）

### テストケース

#### 1. 正常系テスト

```yaml
シナリオ: LINE登録誘導動画の生成
手順:
  1. Phase 2-3で台本生成（status = approved）
  2. Phase 4a実行 → 7枚の画像確認
  3. Phase 4b実行 → 7本の動画確認
  4. Phase 4c実行 → 1本の完成動画確認
  5. Phase 5実行 → SNS投稿確認

期待結果:
  ✅ 60-90秒の完成動画
  ✅ テキストが正確に配置
  ✅ 動きが自然
  ✅ スムーズな結合
```

#### 2. 品質確認

```yaml
確認項目:
  - テキスト可読性（フォント、色、サイズ）
  - 動きの自然さ（ズーム、スライド、フェード）
  - 結合の滑らかさ（トランジション）
  - 音声なし（Phase 3で追加予定）
  - ファイルサイズ（<50MB推奨）
```

#### 3. 異常系テスト

```yaml
テストケース:
  1. FAL API タイムアウト → リトライ確認
  2. FFmpeg失敗 → エラーハンドリング確認
  3. Google Drive アップロード失敗 → 再試行確認
  4. Notion DB更新失敗 → ログ確認
```

---

## 📝 実装チェックリスト

### 🔧 環境準備

- [x] Railway n8nデプロイ成功
- [x] FFmpeg + Noto Sans JPフォント インストール
- [ ] FAL API アカウント作成
- [ ] FAL API Key取得
- [ ] n8n Credentials登録（FAL API Key）

### 📋 Phase 2-3修正

- [ ] Notion DBスキーマ更新（新規カラム追加）
- [ ] ChatGPTプロンプトにSTEP11追加
- [ ] テスト台本生成で確認

### 🎨 Phase 4a実装

- [ ] n8n Webhookノード作成
- [ ] Notion Database Queryノード実装
- [ ] Code Node（Python）でPillowスクリプト実装
- [ ] Split Outノード実装
- [ ] Google Drive Upload実装
- [ ] Aggregateノード実装
- [ ] 7枚の画像生成テスト

### 🎬 Phase 4b実装

- [ ] Loop Over Itemsノード実装
- [ ] HTTP Request（FAL Submit）実装
- [ ] Waitノード実装
- [ ] Loop（Check Status）実装
- [ ] IF（Check Success）実装
- [ ] Extract Video URLノード実装
- [ ] Aggregateノード実装
- [ ] 7本の動画生成テスト

### 🎞️ Phase 4c実装

- [ ] Aggregate Videosノード実装
- [ ] Code Node（Python）でFFmpeg実装
- [ ] Google Drive Upload実装
- [ ] Notion DB Update実装
- [ ] Webhook Responseノード実装
- [ ] Trigger Phase 5ノード実装
- [ ] 完成動画生成テスト

### 🧪 E2Eテスト

- [ ] 正常系テスト（LINE登録誘導動画）
- [ ] 品質確認（テキスト、動き、結合）
- [ ] 異常系テスト（エラーハンドリング）
- [ ] パフォーマンステスト（処理時間）

---

## 🚀 実装スケジュール

### Day 1: 環境準備 + Phase 4a実装（2🍅）

```yaml
午前（1🍅）:
  - FAL API アカウント作成
  - API Key取得
  - n8n Credentials設定
  - Phase 2-3修正（Notion DB + プロンプト）

午後（1🍅）:
  - Phase 4a n8nワークフロー実装
  - Pillowスクリプト実装
  - テスト画像生成
```

### Day 2: Phase 4b実装（2🍅）

```yaml
午前（1🍅）:
  - FAL API統合実装
  - ポーリングロジック実装

午後（1🍅）:
  - 7本の動画生成テスト
  - 品質確認
  - エラーハンドリング実装
```

### Day 3: Phase 4c実装（1🍅）

```yaml
午前-午後（1🍅）:
  - FFmpeg結合スクリプト実装
  - n8n統合
  - 完成動画生成テスト
```

### Day 4: E2Eテスト（1🍅）

```yaml
終日（1🍅）:
  - 正常系テスト
  - 品質確認
  - 異常系テスト
  - パフォーマンステスト
  - ドキュメント作成
```

---

## ⚠️ リスクと対策

### リスク1: FAL API レート制限

```yaml
リスク内容:
  - 同時に7本の動画生成でレート制限に引っかかる可能性

影響度: 中
発生確率: 低

対策:
  1. 順次処理（1本ずつ生成）
  2. Wait時間の調整（10秒 → 15秒）
  3. リトライロジックの実装
```

### リスク2: FFmpeg処理時間

```yaml
リスク内容:
  - 7本の動画結合に時間がかかりタイムアウト

影響度: 中
発生確率: 低

対策:
  1. タイムアウト延長（600秒設定済み）
  2. シンプルな結合方式（-c copy）を使用
  3. トランジション効果は後回し
```

### リスク3: Notion DB更新失敗

```yaml
リスク内容:
  - 完成動画URLが記録されない

影響度: 低
発生確率: 低

対策:
  1. リトライロジックの実装
  2. エラーログの保存
  3. 手動更新の手順書作成
```

---

## 💰 コスト・工数まとめ

### コスト比較

| 項目 | Creatomate | FAL.ai | 削減効果 |
|------|-----------|---------|----------|
| 月額基本料金 | 推定 $50-100/月 | $0 | $50-100/月 |
| レンダリング単価 | 推定 $1-2/本 | $0.56/本 | 44-72% |
| 月間70本の場合 | $120-240/月 | $39.20/月 | **70-84%削減** |

### 工数見積もり

```yaml
Phase 4a: 2🍅（32分）
Phase 4b: 2🍅（32分）
Phase 4c: 1🍅（16分）
E2Eテスト: 1🍅（16分）
合計: 6🍅（約1.6時間）
```

---

## 📚 関連ドキュメント

- [Phase4-FAL移行-要件定義.md](../Phase4-FAL移行-要件定義.md)
- [Phase4-判断ゲート決定記録.md](../Phase4-判断ゲート決定記録.md)
- [WF7-Phase4-FAL実装変更点.md](../WF7-Phase4-FAL実装変更点.md)
- [n8n-workflow-construction-knowledge.md](../knowledge/n8n-workflow-construction-knowledge.md)

---

## 📝 変更履歴

| 日付 | バージョン | 変更内容 | 担当者 |
|------|-----------|---------|--------|
| 2025-11-06 | 1.0 | 初版作成 | Claude Code (Sonnet 4.5) |

---

**作成**: Claude Code (Sonnet 4.5)
**合計工数**: 6🍅（約1.6時間）
**コスト削減**: 70-84%削減
**実装難易度**: 中（3段階処理だが、各ステップは単純）
