# WF7 Phase4c 調査と実装計画

**作成日**: 2025-01-12
**目的**: Phase4a/4b の完成成果とナレッジを活用した Phase4c 実装計画の策定

---

## 📊 Executive Summary

### 現状
- **Phase4a** (LYPbvJfkMzLlhc6t): ✅ 完成（10ノード）- スライド生成
- **Phase4b** (mfRdJJFJRKmeBjKv): ✅ 完成（13ノード）- 画像→動画変換
- **Phase4c** (chPw11OY5sex6d9I): ⚠️ 要改善（26ノード）- 動画結合

### 主要課題
- Phase4c が目標の 2.6 倍（26ノード vs 目標10ノード）に膨張
- 4つの異なる動画URL抽出アプローチで複雑化
- テスト実行が失敗（webhook モード vs Pin Data の問題）

### 提案
- Phase4b の成功パターンを適用し、10ノードに簡素化
- FAL FFmpeg API を使用した統一実装
- リトライループと明確なエラーハンドリング

---

## 1. Phase4a/4b 完成状況の確認

### 1.1 Phase4a: Slide Generator ✅

**Workflow ID**: `LYPbvJfkMzLlhc6t`
**Status**: Active, 10 nodes
**成功のポイント**:

```yaml
アーキテクチャ:
  - Webhook Trigger → Notion API → Pillow Code → Binary Conversion
  - → Cloudinary Upload → Metadata Merge → Aggregate
  - → Phase4b Input Preparation → Webhook Response + Execute Phase4b

データフロー:
  入力:
    - script_id (string, required)
    - articleId (string, required)
    - text_content (array, 7要素)

  出力:
    - slides_metadata (array, 7要素)
      - slide_index, section, text, image_url, cloudinary_public_id

実装パターン:
  1. 単一責任: スライド画像生成のみ
  2. Aggregate パターン: 7スライドを統合
  3. Cloudinary 一括アップロード
  4. 明確なデータ契約
```

### 1.2 Phase4b: Image-to-Video Generator ✅

**Workflow ID**: `mfRdJJFJRKmeBjKv`
**Version**: v43 (Fixed)
**Status**: Active, 13 nodes
**Critical Success Pattern**:

```yaml
アーキテクチャ:
  - Webhook/Execute Trigger → Input Processing → FAL Payload Preparation
  - → FAL API Submit → Status Check → IF Completed?
  - → [True] Result Extraction → Metadata Building → Response
  - → [False] Retry Counter → IF Retry Limit → [Continue] Status Check Loop

重要な学習 - IFノードのリトライループ:
  IF ノードは常に output[0] に True、output[1] に False のデータを流す
  → リトライループでは接続を逆にする必要がある!

  "IF - Check Retry Limit": {
    "main": [
      [{"node": "Code - Timeout Error"}],      // output[0] → timeout (REVERSED!)
      [{"node": "HTTP Request - Check Status"}] // output[1] → retry (REVERSED!)
    ]
  }

データフロー:
  入力:
    - script_id, articleId, slide_index, section, text
    - image_url, duration, motion_prompt

  出力:
    - success, section, duration, video_url
    - fal_request_id, filename

FAL API パターン:
  1. Submit (POST) → request_id 取得
  2. Wait 2秒
  3. Check Status (GET) → status 確認
  4. IF status == "COMPLETED" → Extract URL
  5. ELSE → Retry (最大10回、5秒間隔)

動画URL抽出の優先順位:
  1. resultData.video?.url (最優先)
  2. resultData.outputs?.[0] (フォールバック)
  3. response.data?.video_url (最終手段)
```

### 1.3 Phase4a/4b から抽出した重要なナレッジ

#### ナレッジ1: IFノードのリトライループパターン（Phase4b）

**問題**: n8n の IF ノードは常に output[0] に True、output[1] に False のデータを流す

**解決**: リトライループでは接続を**逆にする**
```json
{
  "main": [
    [{"node": "Error Handler"}],  // output[0] → 失敗時の処理（逆！）
    [{"node": "Retry Node"}]       // output[1] → 再試行（逆！）
  ]
}
```

**適用先**: Phase4c のリトライループにも同じパターンを適用

#### ナレッジ2: FAL API ステータスポーリングパターン（Phase4b）

```yaml
パターン:
  1. Submit → request_id 取得
  2. Wait 2秒（初回）
  3. Status Check → status 確認
  4. IF completed:
       - True → Extract result
       - False → Wait 5秒 → Retry (最大10回)

実装:
  - 初回待機: 2秒（最小待機）
  - リトライ間隔: 5秒（適度な間隔）
  - 最大リトライ: 10回（50秒タイムアウト）
  - カウンター: $json.retry_count + 1
```

**適用先**: Phase4c の FAL FFmpeg API にも同じポーリングパターンを適用

#### ナレッジ3: Pin Data テスティングの問題と解決（Phase4c）

**問題**: Pin Data 使用時に `$('Previous Node').item.json.field` が動作しない

**原因**: Pin Data 設定時は前のノードが実行されないため、参照できない

**解決**:
```javascript
// ❌ 間違い: 前のノードを参照
$('Set - Phase4a Payload New').item.json.articleId

// ✅ 正しい: 現在のノードのデータを参照
$json.articleId
```

**適用先**: Phase4c の全ノードで Pin Data テスト対応

#### ナレッジ4: データ契約の明確化（Phase4a/4b共通）

```yaml
Phase4a 出力契約:
  slides_metadata: array[7]
    - slide_index: number (0-6)
    - section: string (hook/intro/point1/point2/point3/summary/cta)
    - text: string
    - image_url: string (Cloudinary URL)
    - cloudinary_public_id: string

Phase4b 入力契約:
  script_id: string (required)
  articleId: string (required)
  slide_index: number (required)
  section: string (required)
  text: string (required)
  image_url: string (required, Cloudinary URL)
  duration: number (required, 秒)
  motion_prompt: string (required)

Phase4b 出力契約:
  success: boolean (required)
  section: string (required)
  duration: number (required)
  video_url: string (required, FAL media URL)
  fal_request_id: string (optional)
  filename: string (optional)
```

**適用先**: Phase4c の入出力契約を明確に定義

---

## 2. Phase4c 現状分析

### 2.1 現在の Phase4c 構造（26ノード）

```yaml
Workflow ID: chPw11OY5sex6d9I
Status: Active, 26 nodes
Target: ~10 nodes (62% 削減が必要)

現在のフロー:
  1. Webhook/Execute Trigger
  2. Aggregate Videos (7本を集約)
  3. ペイロード構築
  4. Submit to FAL FFmpeg API
  5. Wait (初回待機)
  6. Fetch Status
  7. Render Completed? (IF)

  # ここから複雑化 - 4つの異なるアプローチ
  8-11. Extract URL Attempt 1 → Needs Get Request? (IF)
  12-15. Get Result Approach 2 → Extract URL Attempt 2 → Needs POST? (IF)
  16-19. Convert to Tracks → Get Result Approach 4 → Extract URL Attempt 4
  20-22. Needs Status URL? (IF) → Get Status URL Approach 3 → Extract URL Attempt 3
  23. Merge Video URL (複数の分岐から統合)
  24. Download Video
  25. Build Filename
  26. Upload to Drive → Update Notion → Respond to Webhook
```

### 2.2 主要な課題

#### 課題1: 過度な複雑化（26ノード）
- **問題**: 4つの異なる動画URL抽出アプローチが存在
- **原因**: トライ&エラーで追加したフォールバック処理が残留
- **影響**: メンテナンス困難、デバッグが複雑、テスト不可能

#### 課題2: 不明確なフロー
- **問題**: どのアプローチが実際に機能しているか不明
- **原因**: 複数の IF ノードによる分岐が複雑に絡み合う
- **影響**: トラブルシューティングが困難

#### 課題3: テスト実行の失敗
- **問題**: Executions 916, 917, 924 が全て失敗
- **原因1**: Webhook モードでは Notion page ID が必要（Pin Data 未使用）
- **原因2**: Pin Data モードでの前ノード参照エラー
- **影響**: 動作確認ができない状態

#### 課題4: Phase4b パターンの未適用
- **問題**: Phase4b で学習した成功パターンが未適用
- **特に**: リトライループの IF ノード接続が正しくない可能性
- **影響**: タイムアウトエラーやリトライ失敗の可能性

---

## 3. Phase4c 技術要件定義

### 3.1 機能要件

```yaml
入力データ:
  script_id: string (required) - スクリプトID
  articleId: string (required) - 記事ID
  phase4b_success: boolean (required) - Phase4b成功フラグ
  videos_count: number (required, value: 7) - 動画本数
  total_duration: number (required) - 合計秒数
  videos_metadata: array[7] (required)
    - section: string (required)
    - duration: number (required, 秒)
    - video_url: string (required, FAL media URL)
    - fal_request_id: string (optional)
    - filename: string (optional)

処理要件:
  1. 7本の動画URLを検証（全て有効か確認）
  2. FAL FFmpeg API でMP4形式に結合
  3. ステータスポーリング（Phase4bパターン適用）
  4. 結合動画のダウンロード
  5. Google Drive へアップロード
  6. Notion データベース更新
  7. エラーハンドリングとリトライ

出力データ:
  success: boolean (required) - 成功フラグ
  script_id: string (required) - スクリプトID
  final_video_path: string (optional) - Google Driveパス
  final_video_url: string (optional) - 動画URL
  total_duration: number (required) - 合計秒数
  video_size_mb: number (optional) - ファイルサイズ
  error_message: string (optional) - エラー時のメッセージ
```

### 3.2 非機能要件

```yaml
パフォーマンス:
  - 動画結合: 最大60秒以内
  - ステータスチェック: 5秒間隔でリトライ
  - 最大実行時間: 90秒（タイムアウト）

信頼性:
  - リトライ回数: 最大10回（50秒）
  - エラーハンドリング: 全ての失敗ケースをカバー
  - ログ出力: エラー詳細を記録

保守性:
  - ノード数: 最大12ノード（Phase4bと同等）
  - 命名規則: 統一された命名規則
  - コメント: 全Codeノードにコメント追加

テスト性:
  - Pin Data対応: 全ノードでPin Dataテスト可能
  - マニュアル実行: n8n UI上で単独実行可能
  - データ検証: 各ステップで出力検証
```

---

## 4. Phase4c 実装戦略

### 4.1 簡素化アーキテクチャ（目標10ノード）

#### Phase4b 成功パターンを適用した新構造

```yaml
# 提案: 10ノード構成（Phase4bパターン適用）

1. Webhook/Execute Workflow Trigger
   - 入力: script_id, articleId, videos_metadata[7]
   - 検証: videos_count == 7, 全URLが有効

2. Code - Prepare FAL FFmpeg Payload
   - videos_metadata から video_url を抽出
   - FAL FFmpeg API 用のペイロードを構築
   - エラーチェック: URL未設定、動画数不正

3. HTTP Request - Submit to FAL FFmpeg API
   - POST https://queue.fal.run/fal-ai/ffmpeg
   - Body: {"inputs": [url1, url2, ...], "output_format": "mp4"}
   - Response: request_id 取得

4. Wait - Initial (2秒)
   - Phase4b パターン: 最初は2秒待機

5. HTTP Request - Check Status
   - GET https://queue.fal.run/fal-ai/ffmpeg/{request_id}/status
   - Response: status, result

6. IF - Render Completed? (Phase4bパターン適用)
   - 条件: $json.status === "COMPLETED"
   - True → output[0] → Result Extraction
   - False → output[1] → Retry Counter

7. [True分岐] Code - Extract Video URL
   - 優先順位（Phase4bパターン）:
     1. $json.result?.video?.url
     2. $json.result?.output
     3. $json.data?.video_url
   - エラー: URL抽出失敗

8. [False分岐] Code - Set Retry Counter
   - retry_count = ($json.retry_count || 0) + 1
   - Phase4b パターン適用

9. [False分岐] IF - Check Retry Limit
   - 条件: $json.retry_count > 10
   - ⚠️ 重要: Phase4b で学習した接続を逆にする!
   - output[0] → Code - Timeout Error (逆!)
   - output[1] → Wait 5秒 → HTTP Request - Check Status (逆!)

10. Code - Build Response + Respond to Webhook
    - 出力データ構築
    - success, final_video_url, total_duration, video_size_mb
    - Webhook Response

削減: 26ノード → 10ノード (62%削減)
```

### 4.2 FAL FFmpeg API 使用方法

```yaml
API エンドポイント:
  Submit: POST https://queue.fal.run/fal-ai/ffmpeg
  Status: GET https://queue.fal.run/fal-ai/ffmpeg/{request_id}/status

リクエスト形式:
  {
    "inputs": [
      "https://v3b.fal.media/files/b/penguin/video1.mp4",
      "https://v3b.fal.media/files/b/rabbit/video2.mp4",
      // ... 7本の動画URL
    ],
    "output_format": "mp4",
    "concat_method": "auto"  // 自動結合
  }

レスポンス形式:
  Submit:
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "IN_QUEUE"
    }

  Status (Processing):
    {
      "status": "IN_PROGRESS",
      "progress": 0.45
    }

  Status (Completed):
    {
      "status": "COMPLETED",
      "result": {
        "video": {
          "url": "https://v3b.fal.media/files/output.mp4",
          "file_size": 15728640,
          "duration": 80.5
        }
      }
    }

エラーハンドリング:
  - 400: Invalid input (動画URL検証)
  - 429: Rate limit (リトライ)
  - 500: Server error (リトライ)
```

### 4.3 実装のポイント

#### ポイント1: Phase4b リトライループパターンの適用

```javascript
// IF - Check Retry Limit ノードの接続（Phase4b パターン）
{
  "main": [
    [{"node": "Code - Timeout Error"}],           // output[0] → タイムアウト（逆!）
    [{"node": "Wait", "index": 0},
     {"node": "HTTP Request - Check Status"}]    // output[1] → リトライ（逆!）
  ]
}

// IF 条件
{
  "conditions": {
    "number": [
      {
        "value1": "={{ $json.retry_count }}",
        "operation": "larger",
        "value2": 10
      }
    ]
  }
}
```

#### ポイント2: 動画URL抽出の優先順位（Phase4b から学習）

```javascript
// Code - Extract Video URL
const resultData = $input.all()[0].json;

// 優先順位1: video?.url（Phase4bで最も信頼性が高い）
let videoUrl = resultData.result?.video?.url;

// 優先順位2: outputs配列
if (!videoUrl) {
  videoUrl = resultData.result?.outputs?.[0];
}

// 優先順位3: 直接のvideo_url
if (!videoUrl) {
  videoUrl = resultData.result?.video_url || resultData.data?.video_url;
}

// エラーチェック
if (!videoUrl) {
  throw new Error('動画URL抽出失敗: result構造が不正です');
}

return {
  json: {
    ...resultData,
    final_video_url: videoUrl
  }
};
```

#### ポイント3: Pin Data テスト対応（Phase4c から学習）

```javascript
// ❌ 間違い: 前のノードを参照（Pin Data使用時に失敗）
const articleId = $('Set - Phase4b Payload').item.json.articleId;

// ✅ 正しい: 現在のノードのデータを参照
const articleId = $json.articleId;

// ✅ より安全: デフォルト値付き
const articleId = $json.articleId || 'unknown';
```

---

## 5. 実装ロードマップ

### Phase 1: コアロジックの実装（1-2日）

```yaml
タスク:
  1. ✅ Phase4c workflow バックアップ作成
  2. 🔄 新しい Phase4c workflow 作成（10ノード構成）
  3. Code - Prepare FAL FFmpeg Payload 実装
  4. HTTP Request - Submit to FAL 実装
  5. Wait + Status Check 実装

検証:
  - FAL API Submit が成功するか
  - Status Check が正常に動作するか
  - Pin Data テスト実施
```

### Phase 2: リトライループの実装（1日）

```yaml
タスク:
  1. IF - Render Completed? 実装
  2. Code - Set Retry Counter 実装
  3. IF - Check Retry Limit 実装（Phase4b パターン適用）
  4. 接続を逆にする設定

検証:
  - リトライループが正常に動作するか
  - タイムアウトエラーが正しく処理されるか
  - 最大10回リトライが守られるか
```

### Phase 3: 結果処理の実装（1日）

```yaml
タスク:
  1. Code - Extract Video URL 実装（Phase4b 優先順位適用）
  2. HTTP Request - Download Video 実装
  3. Google Drive - Upload 実装
  4. Code - Build Response 実装

検証:
  - 動画URLが正しく抽出されるか
  - ダウンロードが成功するか
  - Google Drive アップロードが成功するか
```

### Phase 4: テストとデバッグ（2-3日）

```yaml
テストケース:
  1. 正常系: 7本の動画が正常に結合される
  2. 異常系1: 動画URL不正（エラーハンドリング）
  3. 異常系2: FAL APIタイムアウト（リトライ動作）
  4. 異常系3: 結合失敗（エラーメッセージ）
  5. Pin Data テスト: 全ノードで動作確認

検証:
  - 全ケースでエラーハンドリングが動作
  - エラーメッセージが明確
  - ログ出力が十分
```

### Phase 5: ドキュメント作成（1日）

```yaml
ドキュメント:
  1. Phase4c 実装ドキュメント
  2. テストガイド（Pin Data含む）
  3. トラブルシューティングガイド
  4. API リファレンス
```

---

## 6. リスク管理

### リスク1: FAL FFmpeg API の仕様不明

**リスク**: API の詳細な仕様が不明で、実装時に問題が発生する可能性
**影響度**: 高
**対策**:
- Phase4b で使用した FAL API パターンを適用
- 小規模なテストで API 動作を事前検証
- ドキュメント参照: https://fal.ai/models/ffmpeg

### リスク2: リトライループの実装ミス

**リスク**: Phase4b のパターンを正しく適用できない
**影響度**: 中
**対策**:
- Phase4b workflow (`mfRdJJFJRKmeBjKv`) を参照
- IF ノード接続を慎重に設定（逆接続パターン）
- 小規模なテストで動作確認

### リスク3: Pin Data テストの失敗

**リスク**: 前ノード参照で Pin Data テストが失敗する
**影響度**: 低
**対策**:
- 全てのノードで `$json.*` 参照を使用
- 前ノード参照 `$('NodeName').*` を排除
- Phase4c 既存の問題解決ドキュメント参照

---

## 7. 成功基準

### 定量的基準

```yaml
ノード数:
  - 現在: 26ノード
  - 目標: 10-12ノード
  - 削減率: ≥60%

実行時間:
  - 動画結合: ≤60秒
  - 総実行時間: ≤90秒

信頼性:
  - 成功率: ≥95%（正常ケース）
  - エラーハンドリング: 100%（全ケース）

テストカバレッジ:
  - 正常系: 100%
  - 異常系: ≥80%
  - Pin Data: 100%
```

### 定性的基準

```yaml
保守性:
  - コードが理解しやすい
  - 命名規則が統一されている
  - コメントが十分

拡張性:
  - 動画本数変更が容易
  - 新しいフォーマット追加が容易

運用性:
  - エラーメッセージが明確
  - ログ出力が十分
  - トラブルシューティングが容易
```

---

## 8. 参考資料

### 社内ドキュメント

```yaml
設計:
  - docs/design/WF7-Phase4-簡素化設計書.md
  - docs/design/WF7-Phase4-簡素化比較表.md
  - docs/implementation/WF7-Phase4-親フロー簡素化実装計画.md

Phase4a/4b:
  - docs/implementation/WF7-Phase4b-統合作業レポート_2025-01-11.md
  - docs/testing/WF7-Phase4a-テスト実行結果-LYPbvJfkMzLlhc6t.md

Phase4c 既存:
  - docs/testing/WF7-Phase4c-IFノード問題解決-v2.md
  - docs/testing/WF7-Phase4c-テスト実行結果記録.md
  - docs/testing/WF7-Phase4c-詳細デバッグ手順.md
  - docs/testing/WF7-Phase4c-テスト実行トラブルシューティング.md

ナレッジベース:
  - docs/knowledge/n8n-workflow-construction-knowledge.md
    - IFノードのリトライループパターン（Phase4b）
```

### 外部リソース

```yaml
n8n:
  - n8n Documentation: https://docs.n8n.io/
  - HTTP Request Node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/

FAL:
  - FAL API Documentation: https://fal.ai/docs
  - FFmpeg Model: https://fal.ai/models/ffmpeg
  - API Reference: https://fal.ai/docs/model-apis

FFmpeg:
  - FFmpeg Documentation: https://ffmpeg.org/documentation.html
  - Concat Demuxer: https://trac.ffmpeg.org/wiki/Concatenate
```

---

## 9. Next Steps

### Immediate Actions（今すぐ実行）

1. **Phase4c Backup 作成**
   ```bash
   # 現在の Phase4c をバックアップ
   # Workflow ID: chPw11OY5sex6d9I
   ```

2. **FAL FFmpeg API テスト**
   - 小規模なテスト（2-3本の動画）
   - API レスポンス構造の確認
   - エラーケースの確認

3. **Phase4b Workflow 詳細分析**
   - リトライループの IF ノード接続を確認
   - Code ノードのロジックを確認
   - データフローを確認

### Short-term Actions（1週間以内）

1. **新 Phase4c 実装開始**
   - 10ノード構成で新規作成
   - Phase4b パターンを適用
   - Pin Data テスト対応

2. **テスト実施**
   - Pin Data テスト
   - 正常系・異常系テスト
   - エラーハンドリング確認

3. **ドキュメント更新**
   - 実装ドキュメント
   - テストガイド
   - トラブルシューティング

---

**作成者**: Claude Code (SuperClaude)
**最終更新**: 2025-01-12
**Status**: Phase4c 実装計画完成、実装開始待ち
