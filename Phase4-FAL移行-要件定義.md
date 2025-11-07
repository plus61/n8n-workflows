# Phase 4: FAL.ai移行 要件定義書

**作成日**: 2025-11-06
**決定事項**: WF7 Phase 4のレンダリングエンジンをFAL.aiに変更（コスト最適化）

---

## 📋 背景

### 変更理由
- Creatomateのコスト高（月額料金 + レンダリング単価）
- **FAL.aiはコスト効率が高い**（従量課金、4x faster）
- FastAPI実装課題の解決（E2E環境問題）

### FAL.aiの特徴

```yaml
主要機能:
  - Text-to-Video: プロンプトから動画生成
  - Image-to-Video: 静止画に動きをつける
  - Audio Generation: 音声・効果音生成（Veo 3）
  - FFmpeg Utilities: 動画編集・結合・メタデータ処理

利用可能モデル:
  - Veo 3: Google最新モデル、音声生成対応
  - Hunyuan Video: 高品質、テキスト整合性高
  - Stable Video Diffusion: 安定した生成
  - Framepack: Image-to-Video特化

パフォーマンス:
  - 推論速度: 従来比4x faster
  - グローバル分散サーバーレス
  - コールドスタートなし

API:
  - Python, JavaScript, Swift対応
  - シンプルなREST API
  - 600+モデル利用可能
```

---

## 🎯 実装アプローチ: ハイブリッド方式

### 基本戦略

```yaml
Phase 2-3台本生成（既存）
  ↓
Phase 4a: スライド画像生成（新規）
  - Pillow/Canva APIで5部構成の静止画生成
  - テキストを正確に配置
  ↓
Phase 4b: FAL Image-to-Video（新規）
  - 各スライドに動きをつける
  - 3-7秒の短い動画を7本生成
  ↓
Phase 4c: FFmpeg結合（新規）
  - 7本の動画を結合
  - トランジション追加
  - 音声合成（オプション）
  ↓
Phase 5: SNS投稿（既存）
```

**このアプローチの利点**:
✅ テキスト配置の正確性（画像生成で保証）
✅ 動きのプロフェッショナル性（FALのAI生成）
✅ 5部構成の厳密な実装
✅ 低コスト（FAL Image-to-Videoは安価）

---

## 📊 神教育動画12選からの要件マッピング

### 5部構成の要件（再確認）

```yaml
1. フック（3秒）:
  要件:
    - 冒頭で惹きつける一言
    - 数字×失敗の共感型が効果的
    - 5案から選択

  FAL実装:
    - スライド1: "【悲報】87%が知らないMEO集客の罠"
    - Image-to-Video: 3秒、ズームイン効果
    - プロンプト: "dramatic zoom in effect, professional business style"

2. 導入（10秒）:
  要件:
    - 視聴者の悩みへの共感
    - 動画を見るメリット提示

  FAL実装:
    - スライド2: 導入テキスト（100字）
    - Image-to-Video: 10秒、左→右スライド効果
    - プロンプト: "smooth slide transition, calm professional tone"

3. 本編（40秒 = 13秒×3）:
  要件:
    - 3つの要点とストーリー
    - 具体例・図解・実例

  FAL実装:
    - スライド3-5: 各ポイント（100字）
    - Image-to-Video: 各13秒、フェードイン＋ズーム
    - プロンプト: "gentle fade in with subtle zoom, educational style"

4. まとめ（20秒）:
  要件:
    - 得られる未来・変化ビジョン
    - 信頼感・実績の補強

  FAL実装:
    - スライド6: まとめテキスト（100字）
    - Image-to-Video: 20秒、パン効果
    - プロンプト: "cinematic pan effect, inspiring tone"

5. CTA（7秒）:
  要件:
    - LINE登録への自然な誘導
    - 3パターンから選択

  FAL実装:
    - スライド7: CTA（25字）
    - Image-to-Video: 7秒、パルス効果
    - プロンプト: "pulsing call-to-action, urgent professional"
```

---

## 🔧 WF変更点の詳細

### Phase 4の分割設計

#### Phase 4a: スライド画像生成（新規）

```yaml
入力: Phase 2-3の台本データ（Notion DB）

処理:
  1. Python/Pillow または Canva API
  2. テンプレート画像（1080x1920、縦型）
  3. テキストレイヤー配置
     - フォント: Noto Sans JP（日本語対応）
     - サイズ: 可読性重視
     - 色: ブランドカラー適用
  4. 7枚の画像を生成

出力:
  - slide_1_hook.png
  - slide_2_intro.png
  - slide_3_point1.png
  - slide_4_point2.png
  - slide_5_point3.png
  - slide_6_summary.png
  - slide_7_cta.png

実装方法:
  - n8n Code Nodeで Pillow実行
  - または Canva API統合
```

**Pillowサンプルコード**:
```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_slide(text, duration_label, bg_color="#1a1a2e"):
    # 1080x1920 縦型画像
    img = Image.new('RGB', (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 日本語フォント
    font_title = ImageFont.truetype("NotoSansJP-Bold.ttf", 80)
    font_body = ImageFont.truetype("NotoSansJP-Regular.ttf", 60)

    # テキスト折り返し
    wrapped = textwrap.fill(text, width=20)

    # 中央配置
    bbox = draw.textbbox((0, 0), wrapped, font=font_body)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1080 - text_width) // 2
    y = (1920 - text_height) // 2

    # テキスト描画
    draw.text((x, y), wrapped, fill="#ffffff", font=font_body)

    # 秒数ラベル
    draw.text((50, 1800), duration_label, fill="#aaaaaa", font=font_title)

    return img
```

---

#### Phase 4b: FAL Image-to-Video（新規）

```yaml
入力: 7枚のスライド画像

処理:
  1. FAL API呼び出し（Image-to-Video）
  2. モデル選択: fal-ai/stable-video-diffusion または fal-ai/framepack
  3. 各画像に動きをつける
  4. プロンプトで動きの種類を指定

出力:
  - video_1_hook.mp4 (3秒)
  - video_2_intro.mp4 (10秒)
  - video_3_point1.mp4 (13秒)
  - video_4_point2.mp4 (13秒)
  - video_5_point3.mp4 (13秒)
  - video_6_summary.mp4 (20秒)
  - video_7_cta.mp4 (7秒)
```

**FAL API実装例**:
```python
import fal_client

def generate_video_from_image(image_path, duration, prompt):
    handler = fal_client.submit(
        "fal-ai/stable-video-diffusion",
        arguments={
            "image_url": image_path,  # またはbase64
            "motion_bucket_id": 127,  # 動きの強さ
            "cond_aug": 0.02,
            "num_frames": duration * 8,  # 8fps想定
            "num_inference_steps": 25,
            "prompt": prompt
        }
    )

    result = handler.get()
    return result["video"]["url"]

# 使用例
videos = []
videos.append(generate_video_from_image(
    "slide_1_hook.png",
    duration=3,
    prompt="dramatic zoom in effect, professional business style"
))
videos.append(generate_video_from_image(
    "slide_2_intro.png",
    duration=10,
    prompt="smooth slide transition, calm professional tone"
))
# ... 以下同様
```

**n8n実装方法**:
```yaml
HTTP Request Node:
  Method: POST
  URL: https://fal.run/fal-ai/stable-video-diffusion
  Authentication: Bearer Token (FAL API Key)
  Body:
    image_url: "={{$json.image_url}}"
    motion_bucket_id: 127
    num_frames: "={{$json.duration * 8}}"
    prompt: "={{$json.motion_prompt}}"

Loop Node:
  - 7回繰り返し
  - 各スライドに対して実行
  - 完了まで待機（polling）
```

---

#### Phase 4c: FFmpeg結合（新規）

```yaml
入力: 7本の動画ファイル

処理:
  1. FFmpegで動画結合
  2. トランジション追加（オプション）
  3. 音声合成（オプション、FAL Veo 3使用）
  4. 最終出力: 60-90秒の完成動画

出力:
  - final_video_YYYYMMDD_HHMMSS.mp4
```

**FFmpegコマンド例**:
```bash
# シンプルな結合
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# filelist.txt の内容:
# file 'video_1_hook.mp4'
# file 'video_2_intro.mp4'
# file 'video_3_point1.mp4'
# file 'video_4_point2.mp4'
# file 'video_5_point3.mp4'
# file 'video_6_summary.mp4'
# file 'video_7_cta.mp4'

# トランジション付き結合（xfade filter）
ffmpeg -i video_1_hook.mp4 -i video_2_intro.mp4 \
  -filter_complex "[0][1]xfade=transition=fade:duration=0.5:offset=2.5" \
  output_with_transition.mp4
```

**n8n実装方法**:
```yaml
Execute Command Node:
  Command: ffmpeg
  Arguments:
    - "-f"
    - "concat"
    - "-safe"
    - "0"
    - "-i"
    - "filelist.txt"
    - "-c"
    - "copy"
    - "output.mp4"

または

Code Node (Python):
  import subprocess

  file_list = [
      "video_1_hook.mp4",
      "video_2_intro.mp4",
      # ... 省略
  ]

  # filelist.txt作成
  with open("filelist.txt", "w") as f:
      for video in file_list:
          f.write(f"file '{video}'\n")

  # FFmpeg実行
  subprocess.run([
      "ffmpeg", "-f", "concat", "-safe", "0",
      "-i", "filelist.txt", "-c", "copy", "output.mp4"
  ])
```

---

## 📈 神教育動画12選からの追加要件

### STEP6-10の詳細実装

神教育動画12選では、各動画用途について**STEP6-10**で詳細台本を生成します（各1000字以上）。

```yaml
STEP6: フックを5案作成
  → Phase 2-3で生成済み
  → Phase 4aで5枚の画像生成
  → Phase 4bで5本の動画生成
  → A/Bテスト可能

STEP7: 本編の各要点をかみくだく（例えや図解あり）
  → Phase 4aの画像生成時に図解を追加
  → アイコン・グラフ・イラストの配置
  → Canva APIまたはPillowで実装

STEP8: 記憶に残る言い回し・比喩・名言風表現
  → Phase 2-3の台本生成で含める
  → Phase 4aで強調表示（太字・色変え）

STEP9: 能動的に引き込む問いかけ・クイズ・投げかけ
  → 本編スライド3-5に組み込み
  → 「あなたは○○していますか?」形式
  → Phase 4bで動きを強調（ズーム効果）

STEP10: CTA文を3パターン作成
  → Phase 2-3で生成済み
  → Phase 4aで3枚の画像生成
  → Phase 4bで3本の動画生成
  → 最終的に最適案を選択
```

---

## 🔧 Phase 2-3への変更要求

### 出力形式の追加

```yaml
Phase 2-3既存出力（Notion DB）:
  hook_text_5options: ["案1", "案2", ...]
  introduction_text: "導入文"
  main_point_1/2/3: "ポイント1/2/3"
  summary_text: "まとめ"
  cta_text_3options: ["CTA案1", "CTA案2", ...]

Phase 2-3追加出力（Phase 4a用）:
  motion_prompts: {
    hook: "dramatic zoom in effect, professional business style",
    intro: "smooth slide transition, calm professional tone",
    point1: "gentle fade in with subtle zoom, educational style",
    point2: "gentle fade in with subtle zoom, educational style",
    point3: "gentle fade in with subtle zoom, educational style",
    summary: "cinematic pan effect, inspiring tone",
    cta: "pulsing call-to-action, urgent professional"
  }

  duration_config: {
    hook: 3,
    intro: 10,
    point1: 13,
    point2: 13,
    point3: 14,
    summary: 20,
    cta: 7
  }

  visual_elements: {
    point1_icon: "📊",  # オプション
    point2_icon: "🎯",
    point3_icon: "✅"
  }
```

---

## 💰 コスト試算

### FAL.ai料金体系

```yaml
Image-to-Video (Stable Video Diffusion):
  - 価格: $0.05 - 0.10 per video (推定)
  - 1本あたり: 7動画 × $0.08 = $0.56

月間コスト試算:
  - テスト: 20本/月 × $0.56 = $11.20
  - 本番: 50本/月 × $0.56 = $28.00
  - 合計: $39.20/月

比較（Creatomate）:
  - Pro: $xx/月 + $x × 70本 = $xxx/月

結論: FAL.aiは 約70-80% コスト削減
```

---

## 🚀 実装ロードマップ

### Step 1: Phase 4a実装（スライド画像生成）2🍅

```yaml
タスク:
  1. Pillow環境構築
     - Railway Pythonプロジェクト確認
     - Pillow, Noto Sans JPフォントインストール

  2. スライド生成スクリプト作成
     - 7枚のテンプレート関数
     - テキスト自動配置
     - ブランドカラー適用

  3. n8n統合
     - Code Nodeでスクリプト実行
     - Notion DBからデータ取得
     - 画像ファイルをクラウドストレージ保存
```

### Step 2: Phase 4b実装（FAL Image-to-Video）2🍅

```yaml
タスク:
  1. FAL APIアカウント確認
     - API Key取得
     - クレジット確認

  2. n8n HTTP Request実装
     - 7回ループ
     - 各画像に対してAPI呼び出し
     - 完了待機（polling）

  3. エラーハンドリング
     - タイムアウト処理
     - リトライロジック
```

### Step 3: Phase 4c実装（FFmpeg結合）1🍅

```yaml
タスク:
  1. FFmpeg動作確認
     - Railway環境でffmpeg利用可能か確認
     - テスト結合実行

  2. n8n統合
     - Execute CommandまたはCode Node
     - filelist.txt生成
     - 最終動画出力
```

### Step 4: E2Eテスト（1🍅）

```yaml
テストケース:
  1. 正常系（LINE登録誘導動画）
     - Phase 2-3→4a→4b→4c→Phase 5
     - 全プロセス成功確認

  2. 品質確認
     - テキスト可読性
     - 動きの自然さ
     - 結合のスムーズさ

  3. 異常系
     - FAL API失敗時の挙動
     - FFmpeg失敗時の挙動
```

---

## 📊 期待効果

### 定量的効果

```yaml
コスト削減:
  - Creatomate比: 70-80%削減
  - 月額: $39.20（FAL） vs $xxx（Creatomate）

品質向上:
  - テキスト配置: 100%正確（画像生成による）
  - 動き: AIによるプロフェッショナルな動き
  - 5部構成: 厳密な実装

開発工数:
  - Phase 4a: 2🍅（スライド画像生成）
  - Phase 4b: 2🍅（FAL統合）
  - Phase 4c: 1🍅（FFmpeg結合）
  - テスト: 1🍅
  - 合計: 6🍅（Creatomate 5🍅と同等）
```

### 定性的効果

```yaml
柔軟性:
  - スライドデザインの完全制御
  - テキスト配置の自由度
  - ブランディングの一貫性

拡張性:
  - 図解・アイコン追加が容易
  - A/Bテストの実装が簡単
  - 新しい動画タイプの追加が容易

メンテナンス性:
  - Pillowコードの保守が容易
  - FAL APIのシンプルさ
  - デバッグが容易
```

---

## ⚠️ リスクと対策

### リスク1: FAL Image-to-Videoの品質

```yaml
リスク内容:
  - 動きが不自然になる可能性
  - テキストがぼやける可能性

影響度: 中
発生確率: 中

対策:
  1. モデル選択の最適化
     - Stable Video Diffusion vs Framepack
     - パラメータチューニング
  2. 高解像度画像の使用（1080x1920）
  3. 動きの強さ調整（motion_bucket_id）
  4. テスト生成で品質確認
```

### リスク2: 処理時間

```yaml
リスク内容:
  - Phase 4a+4b+4cの合計時間が長い
  - 7本の動画生成に時間がかかる

影響度: 低
発生確率: 高

対策:
  1. 並列処理の実装
     - 7本の動画を並列生成
     - n8n Split In Batches使用
  2. キャッシング戦略
     - 同じスライドは再利用
  3. バックグラウンド処理
     - webhook通知で非同期化
```

### リスク3: FFmpeg結合の失敗

```yaml
リスク内容:
  - コーデック不一致
  - フレームレート不一致

影響度: 低
発生確率: 低

対策:
  1. FAL出力を統一フォーマットに変換
     - 全動画を同じコーデックに変換
     - フレームレートを統一（30fps）
  2. FFmpegパラメータの最適化
  3. 事前検証スクリプト
```

---

## 📝 完了定義

### Phase 4完了条件

```yaml
必須条件:
  ✅ Phase 4a: スライド画像生成完了
  ✅ Phase 4b: FAL Image-to-Video統合完了
  ✅ Phase 4c: FFmpeg結合完了
  ✅ E2Eテスト成功（正常系＋異常系）
  ✅ 実装ドキュメント完備

品質基準:
  ✅ テキスト可読性: 100%正確
  ✅ 動画尺: 60-90秒
  ✅ ファイルサイズ: <50MB
  ✅ 処理時間: <5分/本
```

### 成果物

```yaml
ドキュメント:
  ✅ Phase4-FAL移行-要件定義.md
  ⏳ Phase4a-スライド生成実装ガイド.md
  ⏳ Phase4b-FAL統合実装ガイド.md
  ⏳ Phase4c-FFmpeg結合実装ガイド.md

実装:
  ⏳ n8n Phase 4a: Pillowスライド生成
  ⏳ n8n Phase 4b: FAL API統合
  ⏳ n8n Phase 4c: FFmpeg結合
```

---

## 💡 神教育動画12選からの学び

### 重要な設計原則

```yaml
1. 5部構成の厳守:
   - フック→導入→本編→まとめ→CTAの流れを崩さない
   - 各部の秒数配分を守る

2. STEP6-10の活用:
   - フック5案生成 → A/Bテスト実装
   - 図解・例え話 → スライド画像に反映
   - 問いかけ・クイズ → エンゲージメント向上
   - CTA 3案生成 → 最適化テスト

3. 心理導線の重視:
   - 共感→理解→納得→行動の流れ
   - 視聴者の感情変化を意識
   - 自然なCTA誘導
```

---

**作成**: Claude Code (Sonnet 4.5)
**Phase 4工数見込み**: 6🍅
**コスト削減**: Creatomate比70-80%削減
**次回更新**: Phase 4実装完了時
