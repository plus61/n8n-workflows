# WF7 Phase4 FAL.ai API 要件定義判定書

**作成日**: 2025-11-12
**前提**: Cloudinary `create_slideshow` API調査完了（信頼性問題により使用不可）
**関連ドキュメント**:
- `WF7-Phase4-簡素化設計書.md`
- `WF7-Phase4b-Cloudinary-Investigation-Report.md`

---

## 🎯 FAL.ai使用判定の前提条件

### Cloudinary調査結果に基づく現状認識
- ✅ Cloudinary `create_slideshow` APIは**Beta機能で信頼性問題あり**
- ✅ 動画生成の代替手段が必須
- ✅ 既存FAL.ai実装（Phase4a）は**動作実績あり**

### WF7全体のPhase構成
```
Phase4a: スライド生成 (画像生成)
  └─ Input: scriptData (7 sections)
  └─ Output: slides_metadata (7 images)

Phase4b: 動画生成 (画像→動画変換)
  └─ Input: slides_metadata (7 images)
  └─ Output: videos_metadata (7 videos)

Phase4c: 動画結合 (7動画→1最終動画)
  └─ Input: videos_metadata (7 videos)
  └─ Output: final_video_url (1 video)
```

---

## 📊 FAL.ai API使用判定マトリクス

### Phase4a: スライド生成（既存実装）

| 判定項目 | 判定結果 | 理由 |
|---------|---------|------|
| **FAL.ai使用** | ✅ **継続使用** | 既存実装 `LYPbvJfkMzLlhc6t` で動作確認済み |
| **代替手段検討** | ❌ 不要 | 安定動作中、変更リスクなし |
| **API エンドポイント** | `/fal-ai/flux/schnell` | 画像生成API |
| **実装状態** | ✅ 完了 | サブワークフローとして独立 |

**要件定義**:
- ✅ 現状維持（変更不要）
- ✅ 入力/出力データ契約確認済み
- ✅ エラーハンドリング実装済み

---

### Phase4b: 動画生成（要判定）

#### オプション1: FAL.ai継続使用 (推奨)

| 判定項目 | 評価 | 詳細 |
|---------|------|------|
| **技術的実現性** | ⭐⭐⭐⭐⭐ 5/5 | 既存実装あり、動作実績あり |
| **実装工数** | ⭐⭐⭐⭐⭐ 5/5 | 0時間（既存実装利用） |
| **信頼性** | ⭐⭐⭐⭐☆ 4/5 | Cloudinaryより高信頼 |
| **コスト** | ⭐⭐⭐☆☆ 3/5 | API呼び出し課金あり（7回/動画） |
| **処理時間** | ⭐⭐⭐☆☆ 3/5 | ~140秒（ポーリング含む） |
| **保守性** | ⭐⭐⭐⭐☆ 4/5 | FAL.ai APIドキュメント整備 |

**メリット**:
- ✅ 既存ワークフロー `wHaKi98mTlUvFIOR` 使用可能
- ✅ 即座に本番利用可能
- ✅ ポーリング・リトライロジック実装済み
- ✅ エラーハンドリング実装済み

**デメリット**:
- ❌ API呼び出し回数多い（7回/動画）
- ❌ 処理時間長い（~140秒）
- ❌ 外部APIへの依存

**要件定義**:
```yaml
Phase4b_FAL_Requirements:
  API_Endpoint: "/fal-ai/image-to-video"
  Input:
    script_id: string (必須)
    slides_metadata: array (必須、7要素)
      - section: string
      - image_url: string
      - duration: number

  Output:
    success: boolean (必須)
    script_id: string (必須)
    videos_metadata: array (必須、7要素)
      - section: string
      - video_url: string
      - duration: number
      - render_elapsed: number
    videos_count: number (必須、7)
    total_duration: number

  Processing:
    - FAL Submit API呼び出し（7回並列）
    - ポーリングでステータス確認（最大5分）
    - リトライロジック（最大3回）
    - エラーハンドリング統一

  Performance_Targets:
    - 処理時間: 120-150秒
    - 成功率: 95%以上
    - エラー時のリトライ: 3回まで
```

#### オプション2: Cloudinary Delivery URL Method

| 判定項目 | 評価 | 詳細 |
|---------|------|------|
| **技術的実現性** | ⭐⭐⭐☆☆ 3/5 | 実装調査が必要 |
| **実装工数** | ⭐⭐☆☆☆ 2/5 | 8-16時間（調査+実装+テスト） |
| **信頼性** | ⭐⭐⭐☆☆ 3/5 | 不明（`create_slideshow`より高い可能性） |
| **コスト** | ⭐⭐⭐⭐☆ 4/5 | Cloudinary無料枠内で可能 |
| **処理時間** | ⭐⭐⭐⭐☆ 4/5 | 推定60-90秒 |
| **保守性** | ⭐⭐⭐☆☆ 3/5 | CLTテンプレート学習コスト |

**メリット**:
- ✅ Cloudinary公式推奨手法
- ✅ コスト削減の可能性
- ✅ 処理時間短縮の可能性

**デメリット**:
- ❌ 実装方法の調査が必要
- ❌ CLTテンプレートファイルの学習コスト
- ❌ 動作保証なし（Beta APIの代替手段のため）

**要件定義**:
```yaml
Phase4b_Cloudinary_Delivery_URL_Requirements:
  Method: "Delivery URL with fl_render parameter"
  Implementation_Steps:
    1. CLTテンプレートファイル作成調査
    2. fl_renderパラメータ仕様確認
    3. テスト実装
    4. 動作検証

  Estimated_Implementation_Time: 8-16時間
  Risk_Level: 中（動作保証なし）

  Decision: ⚠️ 調査コスト高、FAL.ai継続使用を推奨
```

---

### Phase4c: 動画結合（要判定）

#### オプション1: FAL FFmpeg API (推奨) ✅ API仕様確認済み

| 判定項目 | 評価 | 詳細 |
|---------|------|------|
| **技術的実現性** | ⭐⭐⭐⭐⭐ 5/5 | FAL `/merge-videos` API使用（仕様確認済み） |
| **実装工数** | ⭐⭐⭐☆☆ 3/5 | 4-8時間（新規実装） |
| **信頼性** | ⭐⭐⭐⭐☆ 4/5 | FAL.ai既存実績あり |
| **コスト** | ⭐⭐⭐☆☆ 3/5 | API課金あり（商用利用可） |
| **処理時間** | ⭐⭐⭐⭐☆ 4/5 | 推定30-60秒 |
| **保守性** | ⭐⭐⭐⭐⭐ 5/5 | ファイルシステム制約なし |

**メリット**:
- ✅ ファイルシステムアクセス制約なし
- ✅ サーバーレスで実行可能
- ✅ 既存FAL API認証情報再利用可能
- ✅ Phase4a/bとAPI基盤統一
- ✅ **API仕様確認済み（merge-videos）**

**デメリット**:
- ❌ 新規実装が必要
- ❌ API課金コスト（商用利用）

**API仕様詳細（2025-11-12 WebSearch調査済み）**:

**エンドポイント**: `https://fal.run/fal-ai/ffmpeg-api/merge-videos`

**Input Parameters**:
```yaml
video_urls: ["string1", "string2", ...]  # 必須: 2個以上の動画URL（順序保持）
target_fps: float                         # オプション: 1-60 fps
resolution: string|object                 # オプション: プリセットまたはカスタム
  # プリセット: "square_hd|square|portrait_4_3|portrait_16_9|landscape_4_3|landscape_16_9"
  # カスタム: {"width": 512-2048, "height": 512-2048}
```

**Output Response**:
```json
{
  "video": {
    "url": "string",
    "content_type": "video/mp4",
    "file_name": "string",
    "file_size": integer
  },
  "metadata": {
    // 元動画情報を含む詳細メタデータ
  }
}
```

**要件定義**:
```yaml
Phase4c_FAL_FFmpeg_Requirements:
  API_Endpoint: "https://fal.run/fal-ai/ffmpeg-api/merge-videos"

  Input:
    script_id: string (必須)
    videos_metadata: array (必須、7要素)
      - section: string
      - video_url: string
      - duration: number

  Output:
    success: boolean (必須)
    script_id: string (必須)
    final_video_url: string (必須)
    final_video_metadata:
      content_type: string
      file_name: string
      file_size: number
    total_duration: number
    video_size_mb: number

  Processing:
    - 7動画のURLを配列に変換
    - FAL `merge-videos` APIに送信
      {
        "video_urls": ["url1", "url2", ..., "url7"],
        "target_fps": 30,
        "resolution": "landscape_16_9"
      }
    - fal.subscribe()でポーリング（最大5分）
    - 完成動画URL取得（video.url）
    - エラーハンドリング（リトライ最大3回）

  Implementation_Steps:
    1. ✅ FAL `merge-videos` API仕様確認完了（WebSearch済み）
    2. 🔲 HTTP Request Nodeでテスト実装（2動画結合）
    3. 🔲 7動画結合実装
    4. 🔲 ポーリング・リトライロジック実装
    5. 🔲 E2E統合テスト

  Client_Implementation_Example:
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
      video_size_mb: (result.video.file_size / 1024 / 1024).toFixed(2)
    };
    ```

  Estimated_Implementation_Time: 4-6時間（API仕様確認済みのため短縮）
```

**代替API情報（参考）**:
- **FAL `/compose` API**: トラック構造（タイムスタンプ付き）で動画合成
  - より高度な制御が必要な場合に使用
  - 複雑なキーフレーム設定が可能
  - Phase4cの要件（シーケンシャル結合）には`merge-videos`が最適

#### オプション2: Railway FFmpeg (Execute Command)

| 判定項目 | 評価 | 詳細 |
|---------|------|------|
| **技術的実現性** | ⭐⭐⭐⭐⭐ 5/5 | FFmpegコマンド直接実行 |
| **実装工数** | ⭐⭐⭐☆☆ 3/5 | 8-12時間（FFmpegコマンド実装） |
| **信頼性** | ⭐⭐⭐⭐⭐ 5/5 | FFmpeg標準機能 |
| **コスト** | ⭐⭐⭐⭐⭐ 5/5 | Railway計算リソースのみ |
| **処理時間** | ⭐⭐⭐⭐⭐ 5/5 | 推定10-30秒 |
| **保守性** | ⭐⭐⭐☆☆ 3/5 | FFmpegコマンド習得必要 |

**メリット**:
- ✅ 完全なコントロール
- ✅ 外部API依存なし
- ✅ コスト最小
- ✅ 処理速度最速

**デメリット**:
- ❌ FFmpegコマンド実装が必要
- ❌ Railway上での動画処理負荷
- ❌ ファイルシステム管理必要

**要件定義**:
```yaml
Phase4c_Railway_FFmpeg_Requirements:
  Method: "Execute Command Node with FFmpeg"
  Input:
    script_id: string (必須)
    videos_metadata: array (必須、7要素)

  Output:
    success: boolean (必須)
    final_video_url: string (Cloudinary/Google Drive)

  Processing:
    - 7動画をRailwayにダウンロード
    - FFmpeg concatフィルタで結合
    - 最終動画をCloudinary/Google Driveにアップロード
    - 一時ファイル削除

  FFmpeg_Command_Example:
    ```bash
    ffmpeg -i video1.mp4 -i video2.mp4 ... -i video7.mp4 \
      -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v]concat=n=7:v=1:a=0[outv]" \
      -map "[outv]" output.mp4
    ```

  Implementation_Steps:
    1. Execute Commandノード追加
    2. 動画ダウンロードロジック実装
    3. FFmpegコマンド実装
    4. 最終動画アップロードロジック実装
    5. 一時ファイルクリーンアップ実装

  Estimated_Implementation_Time: 8-12時間
```

#### オプション3: FastAPI Python Script

| 判定項目 | 評価 | 詳細 |
|---------|------|------|
| **技術的実現性** | ⭐⭐⭐⭐⭐ 5/5 | Pythonスクリプト実装 |
| **実装工数** | ⭐⭐☆☆☆ 2/5 | 12-16時間（FastAPI実装） |
| **信頼性** | ⭐⭐⭐⭐⭐ 5/5 | Python FFmpegライブラリ使用 |
| **コスト** | ⭐⭐⭐⭐⭐ 5/5 | Railway計算リソースのみ |
| **処理時間** | ⭐⭐⭐⭐⭐ 5/5 | 推定10-30秒 |
| **保守性** | ⭐⭐⭐⭐⭐ 5/5 | Pythonコード管理 |

**メリット**:
- ✅ 既存FastAPIサーバー利用可能
- ✅ Pythonライブラリ（moviepy等）使用可能
- ✅ エラーハンドリング充実
- ✅ テストが容易

**デメリット**:
- ❌ FastAPIエンドポイント実装必要
- ❌ 実装工数大きい

**要件定義**:
```yaml
Phase4c_FastAPI_Python_Requirements:
  Method: "FastAPI endpoint /webhook/wf7-phase4c-ffmpeg-concat"
  Framework: "FastAPI + moviepy/ffmpeg-python"

  Input (HTTP POST):
    script_id: string (必須)
    videos_metadata: array (必須、7要素)
      - video_url: string
      - duration: number

  Output (HTTP Response):
    success: boolean
    script_id: string
    final_video_url: string
    total_duration: number
    video_size_mb: number

  Implementation_Steps:
    1. FastAPIエンドポイント追加
    2. moviepy/ffmpeg-pythonライブラリ実装
    3. 動画ダウンロードロジック
    4. 動画結合ロジック
    5. Cloudinary/Google Driveアップロードロジック
    6. Railway redeploy

  Estimated_Implementation_Time: 12-16時間
```

---

## 🎯 最終推奨判定

### Phase4b: 動画生成

**判定結果**: ✅ **FAL.ai継続使用**

**理由**:
1. ✅ 既存実装あり（実装工数0時間）
2. ✅ 動作実績あり（信頼性確認済み）
3. ✅ Cloudinaryより高信頼性
4. ✅ 即座に本番利用可能
5. ✅ リスク最小

**要件定義**: Option 1の要件定義を適用

---

### Phase4c: 動画結合

**判定結果**: ✅ **FAL FFmpeg `merge-videos` API使用（確定）**

#### 最終選択: FAL FFmpeg `merge-videos` API ✅ 仕様確認済み

**理由**:
1. ✅ Phase4a/bとAPI基盤統一（保守性向上）
2. ✅ ファイルシステム制約なし
3. ✅ 実装工数適度（4-6時間、API仕様確認済みのため短縮）
4. ✅ サーバーレス実行
5. ✅ **API仕様完全確認済み（WebSearch 2025-11-12）**

**要件定義**: Option 1の要件定義を適用（上記の詳細仕様参照）

**実装ステップ（更新版）**:
1. ✅ FAL `merge-videos` API仕様確認完了（WebSearch済み）
2. 🔲 HTTP Request Nodeでテスト実装開始（2動画結合）
3. 🔲 7動画結合実装
4. 🔲 ポーリング・リトライロジック実装
5. 🔲 E2E統合テスト

#### 第二選択: Railway FFmpeg

**理由**:
1. ✅ FAL API仕様不明時のフォールバック
2. ✅ 完全なコントロール
3. ✅ コスト最小
4. ✅ 処理速度最速

**要件定義**: Option 2の要件定義を適用

---

## 📋 実装優先順位

### ✅ 完了（2025-11-12）

1. ✅ **Phase4b FAL.ai継続使用の確定**
   - 既存ワークフロー `wHaKi98mTlUvFIOR` 使用決定
   - データ契約確認済み

2. ✅ **Phase4c実装方法の決定**
   - FAL `merge-videos` API仕様調査完了（WebSearch）
   - **FAL FFmpeg `merge-videos` API使用に確定**

### 🔲 次のアクション（即座に実施）

3. 🔲 **Phase4b既存ワークフロー動作確認**
   - Workflow ID `wHaKi98mTlUvFIOR` の動作検証
   - データ契約インターフェース確認
   - エラーハンドリング・リトライロジック確認

4. 🔲 **Phase4c実装開始（FAL merge-videos API）**
   - HTTP Request Nodeでテスト実装（2動画結合）
   - ポーリング・リトライロジック実装
   - 7動画結合実装
   - 単体テスト実施

### 短期実施（1週間以内）

5. 🔲 **親フロー統合**
   - Phase4a/b/c統合
   - E2Eテスト実施（実際のNotionデータ使用）

6. 🔲 **本番デプロイ準備**
   - エラーハンドリング検証
   - パフォーマンステスト
   - ドキュメント更新

---

## ⚠️ リスク管理

### Phase4b: FAL.ai継続使用のリスク

| リスク | 影響度 | 対策 |
|--------|--------|------|
| API呼び出し回数多い | 中 | コスト監視、月次レビュー |
| 処理時間長い | 低 | ユーザー期待値管理 |
| 外部API依存 | 中 | FAL.aiサービス状態監視 |

### Phase4c: FAL FFmpeg APIのリスク

| リスク | 影響度 | 対策 |
|--------|--------|------|
| API仕様不明確 | 高 | WebSearch調査→不明ならOption 2 |
| 新規実装バグ | 中 | 十分な単体テスト実施 |
| 処理時間予測誤差 | 低 | 実測でパフォーマンス確認 |

### Phase4c: Railway FFmpegのリスク

| リスク | 影響度 | 対策 |
|--------|--------|------|
| FFmpegコマンド実装難易度 | 中 | 段階的実装（1動画→3動画→7動画） |
| Railway計算リソース負荷 | 中 | リソース使用量監視 |
| ファイルシステム管理 | 低 | 一時ファイルクリーンアップ実装 |

---

## 📊 コスト比較

### Phase4b: FAL.ai vs Cloudinary

| 項目 | FAL.ai | Cloudinary Delivery URL |
|------|--------|-------------------------|
| **初期実装コスト** | 0時間 | 8-16時間 |
| **API課金** | 有料 | 無料枠内 |
| **処理時間** | 120-150秒 | 60-90秒（推定） |
| **信頼性** | 高 | 不明 |
| **総合評価** | ✅ 推奨 | ⚠️ 調査コスト高 |

### Phase4c: 3オプション比較

| 項目 | FAL FFmpeg | Railway FFmpeg | FastAPI Python |
|------|------------|----------------|----------------|
| **実装工数** | 4-8時間 | 8-12時間 | 12-16時間 |
| **API課金** | 有料 | なし | なし |
| **処理時間** | 30-60秒 | 10-30秒 | 10-30秒 |
| **保守性** | 高 | 中 | 高 |
| **総合評価** | ✅ 第一選択 | ✅ 第二選択 | ⚠️ 工数大 |

---

## 📝 決定事項サマリー

### ✅ 確定事項（2025-11-12）

1. ✅ **Phase4b: FAL.ai継続使用（確定）**
   - 既存実装利用（Workflow ID: `wHaKi98mTlUvFIOR`）
   - 実装工数0時間
   - 即座に本番利用可能

2. ✅ **Phase4c: FAL FFmpeg `merge-videos` API使用（確定）**
   - API仕様確認完了（WebSearch 2025-11-12）
   - エンドポイント: `https://fal.run/fal-ai/ffmpeg-api/merge-videos`
   - 実装工数: 4-6時間
   - Input: `video_urls` array（7要素）
   - Output: 結合された動画URL

### 🔲 次のアクション（即座に実施）

1. 🔲 Phase4b既存ワークフロー動作確認（Workflow ID: `wHaKi98mTlUvFIOR`）
2. 🔲 Phase4c実装開始（FAL `merge-videos` API）
3. 🔲 HTTP Request Nodeでテスト実装（2動画結合）
4. 🔲 7動画結合実装＋E2E統合テスト

### 🎯 実装完了目標

- **Phase4b**: ✅ 既存実装確認のみ（0時間）
- **Phase4c**: 4-6時間（API仕様確認済み）
- **統合テスト**: 2-4時間
- **合計**: 6-10時間で完全実装完了

---

**Document Version**: 2.0
**Author**: AI Assistant
**Created**: 2025-11-12T09:30:00Z
**Last Updated**: 2025-11-12T10:15:00Z
**Status**: ✅ Phase4b Confirmed | ✅ Phase4c API Confirmed | 🔲 Implementation Pending

**変更履歴**:
- v2.0 (2025-11-12 10:15): FAL `merge-videos` API仕様確認完了、Phase4c実装方法確定
- v1.0 (2025-11-12 09:30): 初版作成、Phase4b確定、Phase4c調査中
