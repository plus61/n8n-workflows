# WF7 Phase3 セグメント別音声生成 - 設計書

**作成日時**: 2025-11-16 16:57:33 JST

## 📋 概要

Phase3ワークフローを修正して、単一の音声ファイルではなく、7つの個別セグメント音声ファイルを生成するように変更します。これによりPhase4との統合が可能になります。

## 🎯 目的

### 現状の課題

**Phase3現在の出力**:
```json
{
  "voiceFileUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=xxx"
}
```
- 全セグメントを1つの音声ファイルに結合
- Phase4が期待する形式と不一致

**Phase4が期待する入力**:
```json
{
  "Audio": {
    "segments": [
      {
        "assetTag": "segment-hook",
        "audioUrl": "https://.../audio?articleId=xxx&segment=hook",
        "subtitle": "これが未来の動画制作"
      },
      {
        "assetTag": "segment-intro",
        "audioUrl": "https://.../audio?articleId=xxx&segment=intro",
        "subtitle": "効率化がもたらす変革"
      }
      // ... 7セグメント分（hook, intro, point1, point2, point3, summary, cta）
    ]
  }
}
```

### 目標

1. **7つの個別音声ファイル生成**: 各セグメント（hook, intro, point1, point2, point3, summary, cta）ごとに個別の音声ファイル
2. **Phase4互換の出力形式**: セグメント配列形式での出力
3. **後方互換性の維持**: 既存のNotionプロパティ更新も継続

## 🏗️ アーキテクチャ設計

### 現在のワークフロー構造

```
WF7-Phase3 Webhook
  ↓
音声必要性判定（if）
  ↓ (true)
ナレーション抽出（code）
  ↓
Notionページ取得（httpRequest）
  ↓
Script JSON解析（code）← 全セグメントのnarrationを結合
  ↓
OpenAI TTS音声生成（httpRequest）← 1回のAPI呼び出し
  ↓
音声ファイル保存（writeBinaryFile）← 1つのファイル
  ↓
音声メタデータ保存（code）← 1つのURL
  ↓
SRT字幕生成（code）
  ↓
字幕ファイル保存（writeBinaryFile）
  ↓
字幕メタデータ保存（code）
  ↓
Notionペイロード作成（code）
  ↓
Notionページ更新（httpRequest）
  ↓
Respond to Webhook（respondToWebhook）
```

### 修正後のワークフロー構造（推奨案）

```
WF7-Phase3 Webhook
  ↓
音声必要性判定（if）
  ↓ (true)
ナレーション抽出（code）
  ↓
Notionページ取得（httpRequest）
  ↓
Script JSON解析 v2（code）← セグメント配列を個別に出力
  ↓
Split In Batches（splitInBatches）← 新規：セグメントごとに処理
  ↓
セグメント音声生成（httpRequest）← 修正：個別セグメントのnarration使用
  ↓
セグメント音声保存（writeBinaryFile）← 修正：セグメント別ファイル名
  ↓
セグメントメタデータ蓄積（code）← 新規：配列に追加
  ↓
Loop Back to Split In Batches（全セグメント処理完了まで）
  ↓
音声メタデータ最終化（code）← 新規：Phase4形式で出力
  ↓
【字幕処理は既存のまま維持】
SRT字幕生成（code）
  ↓
字幕ファイル保存（writeBinaryFile）
  ↓
字幕メタデータ保存（code）
  ↓
Notionペイロード作成 v2（code）← 修正：セグメント配列を含める
  ↓
Notionページ更新（httpRequest）
  ↓
Respond to Webhook v2（respondToWebhook）← 修正：Phase4形式で返却
```

## 🔧 ノード別修正詳細

### 1. Script JSON解析 v2（修正）

**現在のコード**:
```javascript
const narrationText = scriptData.segments
  .map(segment => segment.narration)
  .filter(Boolean)
  .join(' ');  // ← 全セグメント結合
```

**修正後のコード**:
```javascript
const notionPage = $input.first().json;
const prevData = $('ナレーション抽出').first().json;

// Script JSONプロパティからJSON文字列を取得
const scriptJsonProperty = notionPage.properties['Script JSON'];
if (!scriptJsonProperty || !scriptJsonProperty.rich_text || scriptJsonProperty.rich_text.length === 0) {
  throw new Error('Script JSON property not found in Notion page');
}

const scriptJsonString = scriptJsonProperty.rich_text[0].text.content;
const scriptData = JSON.parse(scriptJsonString);

if (!scriptData.segments || !Array.isArray(scriptData.segments)) {
  throw new Error('Invalid script data structure: segments array not found');
}

// セグメント配列を個別に出力（結合しない）
const segments = scriptData.segments.map((segment, index) => ({
  ...prevData,
  segmentIndex: index,
  segmentType: segment.type,
  segmentNarration: segment.narration,
  segmentSubtitle: segment.subtitle || segment.narration,
  segmentDuration: segment.duration,
  segmentAssetTag: segment.assetTag
}));

return segments.map(seg => ({ json: seg }));
```

**変更点**:
- セグメントを結合せず、個別のアイテムとして出力
- 各セグメントに必要な情報を含める

### 2. Split In Batches（新規追加）

**ノード設定**:
- **Node Type**: `n8n-nodes-base.splitInBatches`
- **Batch Size**: 1（1セグメントずつ処理）
- **Options**: `reset: false`（全セグメント処理完了まで継続）

**目的**:
- セグメント配列を1つずつ処理
- 各セグメントに対してOpenAI TTS API呼び出し

### 3. セグメント音声生成（修正）

**現在の設定**:
```json
{
  "jsonBody": "={{ {\n  \"model\": \"tts-1\",\n  \"input\": $json.narrationText,\n  \"voice\": \"nova\",\n  \"response_format\": \"wav\"\n} }}"
}
```

**修正後の設定**:
```json
{
  "jsonBody": "={{ {\n  \"model\": \"tts-1\",\n  \"input\": $json.segmentNarration,\n  \"voice\": \"nova\",\n  \"response_format\": \"wav\"\n} }}"
}
```

**変更点**:
- `$json.narrationText` → `$json.segmentNarration`
- 個別セグメントのnarrationのみを音声化

### 4. セグメント音声保存（修正）

**現在の設定**:
```json
{
  "fileName": "={{ '/tmp/voice_' + $('Script JSON解析').first().json.articleId + '.wav' }}"
}
```

**修正後の設定**:
```json
{
  "fileName": "={{ '/tmp/voice_' + $json.articleId + '_' + $json.segmentType + '.wav' }}"
}
```

**変更点**:
- ファイル名にセグメントタイプを含める
- 例: `voice_xxx_hook.wav`, `voice_xxx_intro.wav`

### 5. セグメントメタデータ蓄積（新規追加）

**ノード設定**:
- **Node Type**: `n8n-nodes-base.code`
- **Mode**: `runOnceForEachItem`

**コード**:
```javascript
const articleId = $json.articleId;
const notionPageId = $json.notionPageId;
const segmentType = $json.segmentType;
const segmentAssetTag = $json.segmentAssetTag;
const segmentSubtitle = $json.segmentSubtitle;

const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';
const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;

// セグメント別のWebhook URL生成
const audioUrl = `${fullBaseUrl}/webhook/wf7-files-audio?articleId=${articleId}&segment=${segmentType}`;

return {
  json: {
    articleId,
    notionPageId,
    segmentType,
    assetTag: segmentAssetTag,
    audioUrl,
    subtitle: segmentSubtitle,
    audioFileName: `voice_${articleId}_${segmentType}.wav`
  }
};
```

**目的**:
- 各セグメントのメタデータを生成
- Phase4互換の形式で出力

### 6. 音声メタデータ最終化（新規追加）

**ノード設定**:
- **Node Type**: `n8n-nodes-base.code`
- **Mode**: `runOnceForAllItems`（全セグメント処理完了後に1回実行）

**配置場所**: Split In Batchesのループ完了後

**コード**:
```javascript
// Split In Batchesから渡された全セグメントのメタデータを集約
const allSegments = $input.all().map(item => ({
  assetTag: item.json.assetTag,
  audioUrl: item.json.audioUrl,
  subtitle: item.json.subtitle
}));

const articleId = $input.first().json.articleId;
const notionPageId = $input.first().json.notionPageId;

return {
  json: {
    articleId,
    notionPageId,
    Audio: {
      segments: allSegments
    }
  }
};
```

**目的**:
- 全セグメントのメタデータを配列に集約
- Phase4が期待する形式で出力

### 7. Notionペイロード作成 v2（修正）

**現在のコード**:
```javascript
return {
  json: {
    notionPageId,
    notionPayload: {
      properties: {
        'Voice URL': {url: voiceFileUrl || ''},
        'Subtitle URL': {url: subtitleFileUrl || ''},
        'Status': {select: {name: 'VoiceReady'}}
      }
    }
  }
};
```

**修正後のコード**:
```javascript
const audioData = $('音声メタデータ最終化').first().json;
const subtitleData = $input.first().json;

const notionPageId = audioData.notionPageId;
const audioSegments = audioData.Audio.segments;

// 後方互換性のため、最初のセグメントのURLをVoice URLとして設定
const firstAudioUrl = audioSegments.length > 0 ? audioSegments[0].audioUrl : '';

return {
  json: {
    notionPageId,
    audioData,
    notionPayload: {
      properties: {
        'Voice URL': {url: firstAudioUrl},
        'Subtitle URL': {url: subtitleData.subtitleFileUrl || ''},
        'Audio Segments': {
          rich_text: [
            {
              text: {
                content: JSON.stringify(audioSegments, null, 2)
              }
            }
          ]
        },
        'Status': {select: {name: 'VoiceReady'}}
      }
    }
  }
};
```

**変更点**:
- 新しいNotionプロパティ `Audio Segments` を追加（セグメント配列をJSON文字列として保存）
- 後方互換性のため `Voice URL` プロパティは維持（最初のセグメントのURL）

### 8. Respond to Webhook v2（修正）

**現在のコード**:
```json
{
  "responseBody": "={{ {status: 'success', message: 'WF7 Phase3 completed', articleId: $('Script JSON解析').first().json.articleId, notionPageId: $('Script JSON解析').first().json.notionPageId, voiceFileUrl: $('音声メタデータ保存').first().json.voiceFileUrl, subtitleFileUrl: $('字幕メタデータ保存').first().json.subtitleFileUrl} }}"
}
```

**修正後のコード**:
```json
{
  "responseBody": "={{ {status: 'success', message: 'WF7 Phase3 completed', articleId: $('Notionペイロード作成 v2').first().json.audioData.articleId, notionPageId: $('Notionペイロード作成 v2').first().json.notionPageId, Audio: $('Notionペイロード作成 v2').first().json.audioData.Audio, subtitleFileUrl: $('字幕メタデータ保存').first().json.subtitleFileUrl} }}"
}
```

**変更点**:
- `voiceFileUrl` → `Audio.segments` 配列に変更
- Phase4が期待する形式で返却

## 🔗 ファイル配信Webhookの対応

### WF7-Files-Audio Webhook修正

**現在の実装**（想定）:
```
GET /webhook/wf7-files-audio?articleId=xxx
→ /tmp/voice_xxx.wav を返却
```

**修正後の実装**:
```
GET /webhook/wf7-files-audio?articleId=xxx&segment=hook
→ /tmp/voice_xxx_hook.wav を返却

GET /webhook/wf7-files-audio?articleId=xxx&segment=intro
→ /tmp/voice_xxx_intro.wav を返却

... 全7セグメント対応
```

**実装方法**:
- クエリパラメータ `segment` を追加
- `segment` が指定されている場合は `voice_{articleId}_{segment}.wav` を返却
- `segment` が未指定の場合は後方互換性のため `voice_{articleId}.wav` を返却（存在する場合）

## 📊 実行フロー例

### 入力データ

**Webhook Body**:
```json
{
  "articleId": "test-123",
  "notionPageId": "notion-456",
  "needsNarration": true
}
```

**Notion Script JSON**:
```json
{
  "segments": [
    {
      "type": "hook",
      "narration": "これが未来の動画制作",
      "subtitle": "これが未来の動画制作",
      "assetTag": "hook-001",
      "duration": 3
    },
    {
      "type": "intro",
      "narration": "効率化がもたらす変革",
      "subtitle": "効率化がもたらす変革",
      "assetTag": "intro-001",
      "duration": 10
    }
    // ... 5セグメント（point1, point2, point3, summary, cta）
  ]
}
```

### 処理フロー

1. **Script JSON解析 v2**: 7アイテム出力（セグメントごと）
2. **Split In Batches**: 1セグメントずつ処理開始
3. **Loop 1 (hook)**:
   - OpenAI TTS: `narration="これが未来の動画制作"` → `binary_data`
   - 音声保存: `/tmp/voice_test-123_hook.wav`
   - メタデータ: `{ assetTag: "hook-001", audioUrl: "https://.../audio?articleId=test-123&segment=hook", subtitle: "これが未来の動画制作" }`
4. **Loop 2 (intro)**: 同様に処理
5. **Loop 3-7**: 残りのセグメントを処理
6. **音声メタデータ最終化**: 7セグメント分を配列に集約
7. **Notion更新**: セグメント配列をNotionに保存
8. **Webhook返却**: Phase4互換形式で返却

### 出力データ

**Webhook Response**:
```json
{
  "status": "success",
  "message": "WF7 Phase3 completed",
  "articleId": "test-123",
  "notionPageId": "notion-456",
  "Audio": {
    "segments": [
      {
        "assetTag": "hook-001",
        "audioUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=test-123&segment=hook",
        "subtitle": "これが未来の動画制作"
      },
      {
        "assetTag": "intro-001",
        "audioUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=test-123&segment=intro",
        "subtitle": "効率化がもたらす変革"
      }
      // ... 5セグメント
    ]
  },
  "subtitleFileUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-subtitle?articleId=test-123"
}
```

## ⚠️ 考慮事項

### パフォーマンス

**実行時間の増加**:
- 現在: 1回のOpenAI TTS API呼び出し（約3-5秒）
- 修正後: 7回のOpenAI TTS API呼び出し（約21-35秒）
- **対策**: Split In Batchesで逐次処理は避けられないが、各API呼び出しは並列化不可（OpenAI APIの制限）

**APIレート制限**:
- OpenAI TTS APIのレート制限に注意
- 1分間に3リクエストの制限がある場合、7セグメントで約2.5分必要
- **対策**: 必要に応じてWaitノードを追加

### エラーハンドリング

**セグメント処理失敗時**:
- 1セグメントの音声生成が失敗した場合、全体を失敗とするか、成功したセグメントのみ返すか
- **推奨**: 1セグメントでも失敗したら全体を失敗として扱う（Phase4での動画生成に支障が出るため）

**ファイル保存失敗時**:
- `/tmp/` ディレクトリの容量制限に注意
- 7ファイル × 数MB = 数十MBの容量が必要
- **対策**: 古いファイルを定期的に削除するクリーンアップ処理

### 後方互換性

**既存のワークフローとの互換性**:
- Notionの `Voice URL` プロパティは維持（最初のセグメントのURL）
- 新しい `Audio Segments` プロパティを追加
- **移行期間**: 両方のプロパティを並行して更新

**既存のファイル配信Webhookとの互換性**:
- `segment` パラメータが未指定の場合は、従来の単一ファイルを返す
- 新しいクライアント（Phase4）は `segment` パラメータ付きでリクエスト

## 📝 実装手順

### ステップ1: ワークフロー修正

1. n8n UIでPhase3ワークフローを開く
2. 「Script JSON解析」ノードを修正（セグメント配列出力）
3. 「Split In Batches」ノードを追加
4. 「OpenAI TTS音声生成」ノードを修正（個別セグメント処理）
5. 「音声ファイル保存」ノードを修正（セグメント別ファイル名）
6. 「セグメントメタデータ蓄積」ノードを追加
7. 「音声メタデータ最終化」ノードを追加
8. 「Notionペイロード作成」ノードを修正（セグメント配列対応）
9. 「Respond to Webhook」ノードを修正（Phase4形式）

### ステップ2: ファイル配信Webhook修正

1. WF7-Files-Audio Webhookを探す（別ワークフロー）
2. クエリパラメータ `segment` を追加
3. セグメント別ファイル名でファイル読み込み

### ステップ3: テスト

1. テスト用のNotionページを作成
2. Phase3 Webhookを手動実行
3. 7つの音声ファイルが生成されることを確認
4. 各セグメントのURLにアクセスして音声ファイルがダウンロードできることを確認
5. Webhook ResponseがPhase4期待形式であることを確認

### ステップ4: Phase4統合テスト

1. Phase3実行結果をPhase4に渡す
2. Phase4が正常に動画生成できることを確認
3. Creatomateでレンダリングが成功することを確認

## 📁 関連ファイル

- Phase3ワークフロー: WF7 Phase3: 音声・字幕生成(オプション) (ID: 4Oo5LL3KMKVn8gUJ)
- Phase4ワークフロー: WF7 Phase4 - Unit Test (Mock Data) (ID: JqqxjgeCdscqlf67)
- モックデータ: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/all-phases-mock-data.json`
- Phase4検証レポート: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_13-06_wf7-phase4-unit-test-verification.md`

## 🎯 次のステップ

1. ✅ 設計書作成（このドキュメント）
2. 🔄 ワークフロー修正の実装
3. ⏳ ファイル配信Webhook修正
4. ⏳ テスト実行
5. ⏳ Phase4統合テスト
