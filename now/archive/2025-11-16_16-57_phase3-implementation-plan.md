# WF7 Phase3 セグメント別音声生成 - 実装計画

**作成日時**: 2025-11-16 16:57:33 JST
**設計書**: `2025-11-16_16-57_phase3-segment-audio-design.md`

## 📋 実装概要

Phase3ワークフロー（ID: 4Oo5LL3KMKVn8gUJ）を修正して、7つの個別セグメント音声ファイルを生成します。

## 🎯 実装戦略

### アプローチ

n8nの大規模修正は、**n8n UIで直接行う**ことを推奨します。理由：

1. **ノード接続の視覚的確認**: ワークフロー全体の構造を視覚的に確認しながら作業できる
2. **即座のテスト実行**: 各ステップで動作確認が可能
3. **エラーの早期発見**: n8n UIのバリデーション機能でエラーを即座に検出
4. **ロールバックの容易さ**: 問題があればすぐに元に戻せる

### 実装フロー

```
1. 現在のワークフローをバックアップ（JSONエクスポート）
2. テスト用ワークフローを作成（Phase3 v2）
3. ノードを段階的に修正
4. 各ステップでテスト実行
5. 全体の統合テスト
6. 本番ワークフローに反映（または切り替え）
```

## 📝 詳細実装手順

### ステップ0: バックアップ作成

**目的**: 現在のワークフローを保存して、問題発生時にロールバックできるようにする

**手順**:
1. n8n UIでPhase3ワークフロー（ID: 4Oo5LL3KMKVn8gUJ）を開く
2. 右上の「⋮」メニュー → 「Download」をクリック
3. JSONファイルを保存: `wf7-phase3-backup-2025-11-16.json`

**確認**:
- JSONファイルがダウンロードされたことを確認
- ファイルサイズが数KB以上であることを確認

---

### ステップ1: Script JSON解析ノードの修正

**対象ノード**: "Script JSON解析" (ID: b2c3d4e5-f6a7-8901-bcde-f12345678901)

**現在のコード**:
```javascript
const notionPage = $input.first().json;
const prevData = $('ナレーション抽出').first().json;

const scriptJsonProperty = notionPage.properties['Script JSON'];
if (!scriptJsonProperty || !scriptJsonProperty.rich_text || scriptJsonProperty.rich_text.length === 0) {
  throw new Error('Script JSON property not found in Notion page');
}

const scriptJsonString = scriptJsonProperty.rich_text[0].text.content;
const scriptData = JSON.parse(scriptJsonString);

if (!scriptData.segments || !Array.isArray(scriptData.segments)) {
  throw new Error('Invalid script data structure: segments array not found');
}

const narrationText = scriptData.segments
  .map(segment => segment.narration)
  .filter(Boolean)
  .join(' ');

if (!narrationText) {
  throw new Error('No narration text found in script segments');
}

return {
  json: {
    ...prevData,
    narrationText,
    scriptData
  }
};
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
- `narrationText`（全セグメント結合）を削除
- 各セグメントを個別のアイテムとして出力
- セグメント情報（type, narration, subtitle等）を各アイテムに含める

**テスト方法**:
1. ノードを修正して保存
2. ワークフローを実行
3. "Script JSON解析"ノードの出力を確認
   - 7つのアイテムが出力されることを確認
   - 各アイテムに`segmentType`, `segmentNarration`, `segmentSubtitle`が含まれることを確認

---

### ステップ2: Split In Batchesノードの追加

**位置**: "Script JSON解析"ノードの後

**ノード設定**:
```yaml
Node Type: n8n-nodes-base.splitInBatches
Node Name: "Split Segments"
Parameters:
  Batch Size: 1
  Options:
    Reset: false
```

**接続**:
- **Input**: "Script JSON解析"ノードから
- **Output**: 新しい"セグメント音声生成"ノードへ

**設定方法（n8n UI）**:
1. "Script JSON解析"ノードの右側の「+」ボタンをクリック
2. "Split In Batches"ノードを検索して選択
3. ノード名を"Split Segments"に変更
4. Batch Sizeを`1`に設定
5. Options → Reset を`false`に設定

**テスト方法**:
1. ワークフローを実行
2. "Split Segments"ノードの出力を確認
   - 1つずつセグメントが処理されることを確認
   - 7回ループすることを確認

---

### ステップ3: OpenAI TTS音声生成ノードの修正と配置

**対象ノード**: "OpenAI TTS音声生成" (ID: 0ec0d8ad-a6bd-4d0d-bbe0-e8153f1424b6)

**ノード名変更**: "OpenAI TTS音声生成" → "セグメント音声生成"

**現在の jsonBody**:
```json
{
  "model": "tts-1",
  "input": "={{ $json.narrationText }}",
  "voice": "nova",
  "response_format": "wav"
}
```

**修正後の jsonBody**:
```json
{
  "model": "tts-1",
  "input": "={{ $json.segmentNarration }}",
  "voice": "nova",
  "response_format": "wav"
}
```

**変更点**:
- `$json.narrationText` → `$json.segmentNarration`

**位置調整**:
- "Split Segments"ノードの次に配置
- 既存の位置から移動させる

**テスト方法**:
1. ワークフローを実行
2. 各セグメントで音声が生成されることを確認
3. 生成された音声ファイルのサイズが妥当であることを確認（数KB〜数MB）

---

### ステップ4: 音声ファイル保存ノードの修正

**対象ノード**: "音声ファイル保存" (ID: 9a0908dd-abeb-45b3-83b7-802584867aba)

**ノード名変更**: "音声ファイル保存" → "セグメント音声保存"

**現在の fileName**:
```
={{ '/tmp/voice_' + $('Script JSON解析').first().json.articleId + '.wav' }}
```

**修正後の fileName**:
```
={{ '/tmp/voice_' + $json.articleId + '_' + $json.segmentType + '.wav' }}
```

**変更点**:
- ファイル名にセグメントタイプを含める
- `$('Script JSON解析').first().json.articleId` → `$json.articleId`

**テスト方法**:
1. ワークフローを実行
2. `/tmp/`ディレクトリに7つの音声ファイルが作成されることを確認
   - `voice_xxx_hook.wav`
   - `voice_xxx_intro.wav`
   - `voice_xxx_point1.wav`
   - `voice_xxx_point2.wav`
   - `voice_xxx_point3.wav`
   - `voice_xxx_summary.wav`
   - `voice_xxx_cta.wav`
3. 各ファイルのサイズが妥当であることを確認

---

### ステップ5: セグメントメタデータ蓄積ノードの追加

**位置**: "セグメント音声保存"ノードの後

**ノード設定**:
```yaml
Node Type: n8n-nodes-base.code
Node Name: "セグメントメタデータ蓄積"
Mode: Run Once for Each Item
```

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

**接続**:
- **Input**: "セグメント音声保存"ノードから
- **Output**: ループバックして"Split Segments"ノードへ

**ループバック接続の設定**:
1. "セグメントメタデータ蓄積"ノードの出力コネクタをクリック
2. "Split Segments"ノードの入力コネクタ（ループバック用）にドラッグ
3. n8nが自動的にループ接続として認識する

**テスト方法**:
1. ワークフローを実行
2. 各セグメントのメタデータが生成されることを確認
3. `audioUrl`にセグメントタイプが含まれることを確認

---

### ステップ6: 音声メタデータ最終化ノードの追加

**位置**: "Split Segments"ノードのループ完了後

**ノード設定**:
```yaml
Node Type: n8n-nodes-base.code
Node Name: "音声メタデータ最終化"
Mode: Run Once for All Items
```

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

**接続**:
- **Input**: "Split Segments"ノードのループ完了出力から
- **Output**: "SRT字幕生成"ノードへ（既存の字幕処理フローに合流）

**Split Segments完了出力の設定**:
- "Split Segments"ノードには2つの出力があります：
  1. ループ中の出力（各セグメント）
  2. ループ完了後の出力（全セグメント）
- "音声メタデータ最終化"ノードは、2番目の出力（ループ完了後）に接続します

**テスト方法**:
1. ワークフローを実行
2. "音声メタデータ最終化"ノードの出力を確認
3. `Audio.segments`配列に7つのセグメントが含まれることを確認
4. 各セグメントに`assetTag`, `audioUrl`, `subtitle`が含まれることを確認

---

### ステップ7: 既存の音声メタデータ保存ノードの削除

**対象ノード**: "音声メタデータ保存" (ID: 08a4623b-56e6-4cad-8b3e-c45057d8876e)

**理由**: このノードは単一音声ファイルのメタデータを生成していたため、セグメント別処理では不要

**削除方法**:
1. "音声メタデータ保存"ノードを選択
2. Deleteキーを押すか、右クリック → "Delete"
3. 接続が切れることを確認

**注意**: 削除前に、このノードを参照している他のノードがないか確認してください。

---

### ステップ8: Notionペイロード作成ノードの修正

**対象ノード**: "Notionペイロード作成" (ID: db641470-3012-4ed5-b543-9e8882957bc5)

**現在のコード**:
```javascript
const { notionPageId, voiceFileUrl, subtitleFileUrl } = $input.first().json;

if (!notionPageId) {
  throw new Error('notionPageId is required');
}

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
- `voiceFileUrl` → `firstAudioUrl`（後方互換性のため最初のセグメント）
- 新しいNotionプロパティ `Audio Segments` を追加（JSON文字列）
- `audioData`を出力に含めて、Webhook返却で使用

**注意**:
- Notionデータベースに `Audio Segments` プロパティを事前に追加する必要があります
- プロパティタイプ: `Text` または `Rich Text`

**テスト方法**:
1. Notionデータベースに `Audio Segments` プロパティを追加
2. ワークフローを実行
3. Notionページが更新されることを確認
4. `Audio Segments` プロパティにJSON配列が保存されることを確認

---

### ステップ9: Respond to Webhookノードの修正

**対象ノード**: "Respond to Webhook" (ID: 5c176c26-8c97-4b96-886d-cd041f04d4f2)

**現在の responseBody**:
```
={{ {status: 'success', message: 'WF7 Phase3 completed', articleId: $('Script JSON解析').first().json.articleId, notionPageId: $('Script JSON解析').first().json.notionPageId, voiceFileUrl: $('音声メタデータ保存').first().json.voiceFileUrl, subtitleFileUrl: $('字幕メタデータ保存').first().json.subtitleFileUrl} }}
```

**修正後の responseBody**:
```
={{ {status: 'success', message: 'WF7 Phase3 completed', articleId: $('Notionペイロード作成').first().json.audioData.articleId, notionPageId: $('Notionペイロード作成').first().json.notionPageId, Audio: $('Notionペイロード作成').first().json.audioData.Audio, subtitleFileUrl: $('字幕メタデータ保存').first().json.subtitleFileUrl} }}
```

**変更点**:
- `voiceFileUrl` → `Audio.segments` 配列
- Phase4が期待する形式で返却

**テスト方法**:
1. ワークフローを実行
2. Webhook Responseを確認
3. `Audio.segments`配列が含まれることを確認
4. 各セグメントに`assetTag`, `audioUrl`, `subtitle`が含まれることを確認

---

### ステップ10: ファイル配信Webhookの修正

**対象ワークフロー**: WF7-Files-Audio Webhook（別ワークフロー）

**現在の実装（想定）**:
```javascript
const articleId = $json.query.articleId;
const filePath = `/tmp/voice_${articleId}.wav`;

// ファイルを読み込んで返却
const fs = require('fs');
const fileData = fs.readFileSync(filePath);

return {
  binary: {
    data: {
      data: fileData.toString('base64'),
      mimeType: 'audio/wav',
      fileName: `voice_${articleId}.wav`
    }
  }
};
```

**修正後の実装**:
```javascript
const articleId = $json.query.articleId;
const segment = $json.query.segment;

// セグメント指定がある場合はセグメント別ファイル、ない場合は単一ファイル（後方互換性）
let filePath;
if (segment) {
  filePath = `/tmp/voice_${articleId}_${segment}.wav`;
} else {
  filePath = `/tmp/voice_${articleId}.wav`;
}

// ファイルを読み込んで返却
const fs = require('fs');
const fileData = fs.readFileSync(filePath);

const fileName = segment ? `voice_${articleId}_${segment}.wav` : `voice_${articleId}.wav`;

return {
  binary: {
    data: {
      data: fileData.toString('base64'),
      mimeType: 'audio/wav',
      fileName: fileName
    }
  }
};
```

**変更点**:
- クエリパラメータ `segment` を追加
- セグメント別ファイル名でファイル読み込み
- 後方互換性のため、`segment`未指定時は単一ファイルを返却

**テスト方法**:
1. ワークフローを修正
2. ブラウザまたはcurlでテスト
   ```bash
   curl "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=xxx&segment=hook" -o test-hook.wav
   ```
3. 音声ファイルがダウンロードできることを確認
4. 7セグメント全てをテスト

---

## 🧪 統合テスト手順

### テスト1: Phase3単体テスト

**目的**: Phase3ワークフローが正常に動作することを確認

**テストデータ**:
```json
{
  "articleId": "test-segment-001",
  "notionPageId": "existing-notion-page-id",
  "needsNarration": true
}
```

**事前準備**:
1. Notionデータベースに `Audio Segments` プロパティを追加
2. テスト用のNotionページを作成
3. `Script JSON` プロパティに7セグメントのJSONを設定

**実行手順**:
1. n8n UIでPhase3ワークフローを開く
2. Webhook URLをコピー
3. curlまたはPostmanでWebhookを実行
   ```bash
   curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio" \
     -H "Content-Type: application/json" \
     -d '{"articleId": "test-segment-001", "notionPageId": "existing-notion-page-id", "needsNarration": true}'
   ```

**期待される結果**:
1. ワークフローが正常に完了
2. 7つの音声ファイルが生成される
3. Notionページが更新される（`Audio Segments`プロパティに配列が保存）
4. Webhook Responseに`Audio.segments`配列が含まれる

**確認項目**:
- [ ] ワークフロー実行が成功
- [ ] 7つの音声ファイルが `/tmp/` に作成
- [ ] Notionページの `Voice URL` が更新
- [ ] Notionページの `Audio Segments` に7セグメントのJSON配列が保存
- [ ] Webhook Responseに `Audio.segments` 配列が含まれる
- [ ] 各セグメントに `assetTag`, `audioUrl`, `subtitle` が含まれる

### テスト2: ファイル配信Webhook単体テスト

**目的**: セグメント別音声ファイルがダウンロードできることを確認

**実行手順**:
1. 7セグメント全てのURLにアクセス
   ```bash
   curl "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=test-segment-001&segment=hook" -o test-hook.wav
   curl "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=test-segment-001&segment=intro" -o test-intro.wav
   # ... 残りのセグメント
   ```

**確認項目**:
- [ ] 7つの音声ファイルがダウンロードできる
- [ ] 各ファイルが再生可能
- [ ] 各ファイルの音声内容が正しい（セグメントのnarrationと一致）

### テスト3: Phase3 → Phase4統合テスト

**目的**: Phase3の出力がPhase4で正常に処理されることを確認

**実行手順**:
1. Phase3を実行（テスト1の手順）
2. Phase3のWebhook Responseを取得
3. Phase4 Unit Testワークフローを開く
4. Phase3の出力をPhase4の入力として設定
5. Phase4を実行

**期待される結果**:
1. Phase4がPhase3の出力を正常に処理
2. Creatomate APIへのリクエストが成功
3. RenderScriptに7つの音声URLが含まれる
4. レンダリングが開始される

**確認項目**:
- [ ] Phase4がPhase3出力を受け入れる
- [ ] Creatomate APIリクエストが成功（201 Created）
- [ ] RenderScriptに7つの音声要素が含まれる
- [ ] 各音声要素のURLが正しい
- [ ] レンダリングステータスが "planned" → "rendering" に遷移

---

## 📋 チェックリスト

### 実装前

- [ ] Phase3ワークフローをバックアップ（JSONエクスポート）
- [ ] Notionデータベースに `Audio Segments` プロパティを追加
- [ ] テスト用Notionページを作成

### 実装中

- [ ] ステップ1: Script JSON解析ノード修正
- [ ] ステップ2: Split In Batchesノード追加
- [ ] ステップ3: OpenAI TTS音声生成ノード修正と配置
- [ ] ステップ4: 音声ファイル保存ノード修正
- [ ] ステップ5: セグメントメタデータ蓄積ノード追加
- [ ] ステップ6: 音声メタデータ最終化ノード追加
- [ ] ステップ7: 音声メタデータ保存ノード削除
- [ ] ステップ8: Notionペイロード作成ノード修正
- [ ] ステップ9: Respond to Webhookノード修正
- [ ] ステップ10: ファイル配信Webhook修正

### テスト

- [ ] Phase3単体テスト実行
- [ ] ファイル配信Webhook単体テスト実行
- [ ] Phase3 → Phase4統合テスト実行

### 本番反映

- [ ] テスト結果をレビュー
- [ ] 問題がないことを確認
- [ ] 本番ワークフローに反映（または切り替え）
- [ ] 本番環境でスモークテスト実行

---

## ⚠️ トラブルシューティング

### 問題1: Split In Batchesがループしない

**症状**: 1セグメントのみ処理されて終了

**原因**: ループバック接続が正しく設定されていない

**解決方法**:
1. "セグメントメタデータ蓄積"ノードの出力を確認
2. "Split Segments"ノードのループバック入力に接続されているか確認
3. 接続を削除して再接続

### 問題2: 音声メタデータ最終化で全セグメントが取得できない

**症状**: `$input.all()`で7つ未満のアイテムしか取得できない

**原因**: Split In Batchesの完了出力に接続されていない

**解決方法**:
1. "Split Segments"ノードの出力を確認（2つの出力があることを確認）
2. "音声メタデータ最終化"ノードが2番目の出力（完了出力）に接続されているか確認

### 問題3: Notionページ更新が失敗

**症状**: "Notionページ更新"ノードでエラー

**原因**: `Audio Segments`プロパティがNotionデータベースに存在しない

**解決方法**:
1. Notion UIでデータベースを開く
2. 新しいプロパティ `Audio Segments` を追加
3. プロパティタイプを `Text` に設定
4. ワークフローを再実行

### 問題4: OpenAI TTS APIレート制限エラー

**症状**: 3-4セグメント目でAPI呼び出しが失敗

**原因**: OpenAI APIのレート制限（1分間に3リクエスト等）

**解決方法**:
1. "セグメント音声生成"ノードの後に"Wait"ノードを追加
2. 待機時間を20秒に設定
3. ワークフローを再実行

---

## 📁 関連ファイル

- **設計書**: `2025-11-16_16-57_phase3-segment-audio-design.md`
- **Phase3ワークフロー**: WF7 Phase3: 音声・字幕生成(オプション) (ID: 4Oo5LL3KMKVn8gUJ)
- **Phase4ワークフロー**: WF7 Phase4 - Unit Test (Mock Data) (ID: JqqxjgeCdscqlf67)
- **バックアップJSON**: `wf7-phase3-backup-2025-11-16.json`（ステップ0で作成）

---

## 🎯 次のステップ

実装計画に従って、n8n UIでワークフローを修正してください。各ステップでテストを実行し、問題がないことを確認してから次のステップに進むことを推奨します。
