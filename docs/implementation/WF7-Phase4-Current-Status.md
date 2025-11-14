# WF7 Phase4 現状技術スタック整理（2025-01-12）

## 📋 ドキュメント概要

**作成日**: 2025-01-12
**目的**: n8n実ワークフロー確認により判明した実際の技術スタックと現状の整理
**対象**: WF7 Phase4a/b/c（画像生成→動画変換→動画結合）

---

## 🔍 実ワークフロー確認結果

### Phase4a - 画像生成（スライド生成）

**Workflow ID**: `LYPbvJfkMzLlhc6t`
**Name**: WF7-4a: Slide Generator
**Status**: ✅ **Active & 稼働中**

#### 使用技術スタック

| 技術 | 用途 | 詳細 |
|------|------|------|
| **Python Pillow (PIL)** | 画像生成 | テキストから1080x1920の画像を生成 |
| **Noto Sans JP** | フォント | Regular/Bold（Railway環境） |
| **Cloudinary** | 画像保存 | Unsigned Upload方式 |
| **Railway** | 実行環境 | Python環境、フォント利用可能 |

#### 処理フロー

```
1. Notion - Get Script Data
   ↓ （property_script_jsonから7セグメント取得）
2. Code - Generate Slides with Pillow
   ↓ （PIL使用、7枚の画像生成）
3. Code - Convert to Binary
   ↓ （Data URI形式に変換）
4. HTTP Request - Upload to Cloudinary
   ↓ （unsigned upload）
5. Code - Merge Slide Metadata
   ↓
6. Aggregate - Combine All Slides
   ↓
7. Set - Phase 4b Input Data
   ↓
8. Execute Workflow - Phase4b（自動トリガー）
```

#### Output形式

```json
{
  "script_id": "string",
  "slides": [
    {
      "section": "hook|intro|point1|point2|point3|summary|cta",
      "duration": 3,
      "cloudinary_url": "https://res.cloudinary.com/drzmodro8/image/upload/...",
      "motion_prompt": "Subtle zoom in effect...",
      "text": "実際のスライドテキスト",
      "filename": "slide_0_hook.png"
    }
    // ... 7枚分
  ],
  "total_duration": 57
}
```

#### ✅ 現状評価

- **動作状況**: ✅ 正常動作
- **品質**: ✅ 高品質（1080x1920、日本語フォント対応）
- **速度**: ✅ 高速（Pillow処理、並列アップロード）
- **コスト**: ✅ 無料（Python標準ライブラリ、Cloudinary無料枠）

---

### Phase4b - 動画変換（画像→動画）

#### 🗄️ v1: FAL.ai Compose API（アーカイブ済み）

**Workflow ID**: `wHaKi98mTlUvFIOR`
**Name**: WF7-4b: Image to Video (FAL)
**Status**: ❌ **Active: false, Archived: true**

##### 使用技術スタック

| 技術 | 用途 | 詳細 |
|------|------|------|
| **FAL.ai FFmpeg Compose API** | 画像→動画変換 | `https://queue.fal.run/fal-ai/ffmpeg-api/compose` |
| **Cloudinary** | 画像ホスティング | Signed Upload（SHA-1認証） |
| **SHA-1 Hash** | 認証 | JavaScript実装 |

##### 処理フロー

```
1. Validate Input（1-7スライド確認）
   ↓
2. Split Out - Slides（7並列処理）
   ↓
3. Download from Google Drive
   ↓
4. Generate Cloudinary Signature（SHA-1）
   ↓
5. Upload to Cloudinary（Base64）
   ↓
6. Prepare FAL Payload
   ↓
7. Submit to FAL Compose API
   ↓
8. Wait 5 seconds
   ↓
9. Check Status（polling、max 10 retries）
   ↓
10. Get Result
   ↓
11. Build Video Metadata
   ↓
12. Aggregate - Wait for All Videos
   ↓
13. Build Final Response
```

##### Output形式

```json
{
  "success": true,
  "script_id": "string",
  "videos_metadata": [
    {
      "section": "hook",
      "video_url": "https://fal.media/files/.../compose_video.mp4",
      "duration": 3,
      "status": "completed"
    }
    // ... 7個分
  ],
  "total_duration": 57
}
```

##### 📊 評価

- **動作状況**: 🗄️ アーカイブ済み（過去は正常動作）
- **品質**: ✅ 高品質（1920x1080、30fps）
- **速度**: ✅ 並列処理で効率的
- **コスト**: 💰 有料（FAL.ai料金）
- **信頼性**: ✅ 実績あり

---

#### ❌ v2: Cloudinary Slideshow API（動作不良）

**Workflow ID**: `yyR10x16t0OdhIjG`
**Name**: WF7-4b: Image to Video (Cloudinary)
**Status**: ✅ **Active: true（但しAPI失敗）**

##### 使用技術スタック

| 技術 | 用途 | 詳細 |
|------|------|------|
| **Cloudinary `create_slideshow` API** | 画像→動画変換 | Beta機能、動作不良 |
| **SHA-1 Hash** | 認証 | JavaScript完全実装 |

##### 処理フロー

```
1. Validate Input
   ↓
2. Split Out - Slides
   ↓
3. Code - Build Slideshow Manifest
   ↓ （複雑なtracks/clips/media構造）
4. Code - Generate Cloudinary Signature
   ↓ （SHA-1ハッシュ計算）
5. HTTP Request - Create Slideshow
   ↓ ❌ **HTTP 404エラー発生**
```

##### Manifest構造例

```json
{
  "type": "video",
  "width": 1920,
  "height": 1080,
  "duration": 57,
  "fps": 30,
  "vars": {
    "slide1": "test_slide_1",
    "slide2": "test_slide_2"
  },
  "tracks": [{
    "width": 1920,
    "height": 1080,
    "clips": [
      {
        "media": ["{{slide1}}", "image", "upload"],
        "type": "image",
        "clipDuration": 3000,
        "transformation": "c_fill,w_1920,h_1080"
      }
    ]
  }]
}
```

##### ❌ 現状問題

- **動作状況**: ❌ **HTTP 404エラー**
- **原因**: Cloudinary Beta API の不安定性
- **調査状況**: 10以上のmanifest構造パターンをテスト済み
- **認証**: ✅ SHA-1署名は正常（検証済み）
- **画像**: ✅ 実際のアップロード済み画像使用
- **結論**: API自体の問題と判断

**詳細調査レポート**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/docs/testing/WF7-Phase4b-Cloudinary-Investigation-Report.md`

---

### Phase4c - 動画結合（7動画→1動画）

**Workflow ID**: -（未実装）
**Status**: 🔲 **実装予定**

#### 採用技術（確定）

**FAL.ai FFmpeg `merge-videos` API**

| 項目 | 詳細 |
|------|------|
| **Endpoint** | `https://fal.run/fal-ai/ffmpeg-api/merge-videos` |
| **Method** | POST（fal.subscribe） |
| **Input** | `video_urls` array（7要素）、`target_fps`、`resolution` |
| **Output** | 結合された動画URL、メタデータ |
| **Processing** | ポーリング（最大5分） |
| **料金** | 商用利用可能（FAL.ai料金） |

#### Input形式

```json
{
  "video_urls": [
    "https://fal.media/files/.../video1.mp4",
    "https://fal.media/files/.../video2.mp4",
    // ... 7個
  ],
  "target_fps": 30,
  "resolution": "landscape_16_9"
}
```

#### Output形式

```json
{
  "success": true,
  "script_id": "string",
  "final_video_url": "https://fal.media/files/.../merged_video.mp4",
  "final_video_metadata": {
    "content_type": "video/mp4",
    "file_name": "merged_video.mp4",
    "file_size": 15728640,
    "url": "https://fal.media/files/.../merged_video.mp4",
    "width": 1920,
    "height": 1080
  },
  "total_duration": 57,
  "video_size_mb": "15.00"
}
```

#### 実装計画

**実装工数**: 4-6時間（API仕様確認済み）

**処理フロー**:
```
1. Validate Input（Phase4b output）
   ↓
2. Extract video_urls（7個のURL配列化）
   ↓
3. Code - Call FAL merge-videos API
   ↓ （fal.subscribe使用）
4. Wait for Completion（polling）
   ↓
5. Build Final Response
   ↓
6. Return to WF7 Main
```

**実装コード例**:
```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/ffmpeg-api/merge-videos", {
  input: {
    video_urls: $json.videos_metadata.map(v => v.video_url),
    target_fps: 30,
    resolution: "landscape_16_9"
  }
});

return {
  success: true,
  script_id: $json.script_id,
  final_video_url: result.video.url,
  final_video_metadata: result.video,
  total_duration: $json.total_duration,
  video_size_mb: (result.video.file_size / 1024 / 1024).toFixed(2)
};
```

---

## 📊 技術スタック比較表

### 誤認識の修正

| 項目 | ❌ 以前の理解 | ✅ 実際の実装 |
|------|--------------|--------------|
| **Phase4a 画像生成** | FAL.ai Flux Schnell | **Python Pillow** |
| **Phase4a 画像ソース** | Unsplash | **PIL テキストレンダリング** |
| **Phase4b v1** | 不明 | **FAL Compose API（アーカイブ済み）** |
| **Phase4b v2** | 不明 | **Cloudinary Slideshow（動作不良）** |
| **Phase4c** | 検討中 | **FAL merge-videos API（確定）** |

### 現状の技術スタック（正確版）

| Phase | Workflow ID | Active | 技術 | 状態 | 品質 |
|-------|-------------|--------|------|------|------|
| **4a** | `LYPbvJfkMzLlhc6t` | ✅ | Python Pillow + Cloudinary | ✅ 稼働中 | ⭐⭐⭐⭐⭐ |
| **4b-v1** | `wHaKi98mTlUvFIOR` | ❌ | FAL Compose API | 🗄️ アーカイブ | ⭐⭐⭐⭐⭐ |
| **4b-v2** | `yyR10x16t0OdhIjG` | ✅ | Cloudinary Slideshow | ❌ API失敗 | ⭐（動作せず） |
| **4c** | - | - | FAL merge-videos API | 🔲 未実装 | - |

---

## 🎯 現状まとめ

### ✅ 正常動作中

1. **Phase4a**: Python Pillow + Cloudinary
   - 7枚の高品質スライド画像生成
   - 日本語フォント対応
   - 並列Cloudinaryアップロード
   - Phase4bへ自動トリガー

### 🗄️ アーカイブ済み（過去動作確認）

2. **Phase4b-v1**: FAL.ai Compose API
   - 7並列で画像→動画変換
   - 実績あり、信頼性高い
   - アーカイブ理由: Cloudinary API テスト目的

### ❌ 動作不良

3. **Phase4b-v2**: Cloudinary Slideshow API
   - HTTP 404エラー
   - 10以上のパターンテスト済み
   - Beta APIの不安定性が原因
   - 詳細調査済み

### 🔲 未実装

4. **Phase4c**: FAL merge-videos API
   - API仕様確認完了
   - 実装工数: 4-6時間
   - 技術的リスク: 低

---

## 💡 推奨アクション

### 短期（即座実施可能）

#### Option A: Phase4b-v1 復活（推奨）⭐⭐⭐⭐⭐

```yaml
Action: Unarchive Workflow `wHaKi98mTlUvFIOR`
Time: 0時間（設定変更のみ）
Risk: 極低（実績あり）
Cost: FAL.ai利用料金のみ
Benefit: 即座に全パイプライン復旧
```

**実施手順**:
1. n8nで`wHaKi98mTlUvFIOR`をUnarchive
2. Phase4aの`Execute Workflow`ノードをv1に変更
3. 動作テスト（実データで確認済み）
4. Phase4c実装へ進む

#### Option B: Cloudinary修正継続

```yaml
Action: Phase4b-v2 デバッグ継続
Time: 不明（API側問題の可能性大）
Risk: 高（Beta API）
Cost: 調査時間
Benefit: Cloudinary統合（もし成功すれば）
```

**推奨度**: ⭐⭐（時間対効果低い）

### 中期（Phase4c実装）

```yaml
Action: FAL merge-videos API実装
Prerequisites: Phase4bが動作していること
Time: 4-6時間
Risk: 低（API仕様確認済み）
Dependencies: Phase4b output形式
```

**実装後の完全パイプライン**:
```
Phase4a（Pillow）→ Phase4b（FAL）→ Phase4c（FAL）→ 完成動画
     ✅               ✅（復活後）      🔲              🎯
```

---

## 📁 関連ドキュメント

1. **Phase4b Cloudinary調査**: `/docs/testing/WF7-Phase4b-Cloudinary-Investigation-Report.md`
2. **Phase4 FAL要件定義**: `/docs/design/WF7-Phase4-FAL-API-Requirements.md`
3. **Phase4 簡素化設計**: `/docs/design/WF7-Phase4-簡素化設計書.md`

---

## 📝 更新履歴

- **2025-01-12**: 初版作成（実ワークフロー確認ベース）
  - Phase4a: Python Pillow使用を確認
  - Phase4b: 2バージョン存在を発見
  - Phase4c: FAL API仕様確認完了
