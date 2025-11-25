# WF7 Phase4: Creatomate統合実装計画

**作成日時**: 2025-11-16 03:14:19 JST

## 1. 概要

### 1.1 目的
WF7（SNS動画自動生成パイプライン）Phase4において、Creatomate APIを使用した動画レンダリング機能を実装する。

### 1.2 スコープ
- **Phase4の役割**: Phase2（素材取得）とPhase3（音声・字幕生成）のデータを統合し、Creatomate APIを呼び出して最終動画を生成
- **入力**: Phase2の画像データ + Phase3の音声・字幕データ + Phase1のScript JSON
- **出力**: Creatomate レンダリング動画URL + Notion Hub更新

---

## 2. Phase 0-1C 検証結果サマリー

### 2.1 Phase 0: 日本語テキスト + TTS検証
**実施日**: 2025-01-16 10:30:00 JST

#### 検証内容
- 日本語テキストレンダリングの動作確認
- Creatomate TTS機能の品質評価
- Ken Burns効果の動作確認

#### 結果
- ✅ **日本語テキスト**: Noto Sans JPフォント使用、正常表示確認
- ❌ **Creatomate TTS**: `invalid URL error`により使用不可
- ✅ **Ken Burns効果**: Scale animation正常動作（120% → 100%、3秒）

#### 判定
- **TTS対応**: 外部サービス（ElevenLabs等）を使用する方針に変更
- **音声ファイル**: 事前生成した音声ファイルをCreatomateに渡す方式

---

### 2.2 Phase 1: 3セグメント構成テスト
**実施日**: 2025-11-16 02:58:51 JST

#### 検証内容
- 複数セグメント（3セグメント: hook, intro, point1）の構成確認
- 各セグメントのduration設定
- Ken Burns効果の連続適用
- 日本語テキストオーバーレイの連続表示

#### 結果
- ✅ **3セグメント構成**: 26秒動画（3+10+13秒）のレンダリング成功
- ✅ **Ken Burns効果**: 各セグメントで独立して動作
- ✅ **日本語字幕**: セグメント別に正しく切り替わり
- ✅ **レンダリング時間**: 約15-20秒（26秒動画）

#### テストスクリプト
`/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_02-58_phase1-3segment-test.py`

---

### 2.3 Phase 1B: 7セグメント完全構成テスト
**実施日**: 2025-11-16 03:03:08 JST

#### 検証内容
- WF7 Script JSONに基づく完全な7セグメント構成（合計80秒）
- hook → intro → point1 → point2 → point3 → summary → cta
- 各セグメントの時間設定とstart_time制御

#### 結果
- ✅ **7セグメント構成**: 80秒動画のレンダリング成功
- ✅ **セグメント時間**: 各セグメントの時間設定が正確
- ✅ **連続アニメーション**: 7セグメント連続でKen Burns効果が動作
- ✅ **レンダリング時間**: 約26秒（80秒動画）

#### セグメント構成
```python
segments = [
    {"type": "hook", "duration": 3, "start_time": 0},
    {"type": "intro", "duration": 10, "start_time": 3},
    {"type": "point1", "duration": 13, "start_time": 13},
    {"type": "point2", "duration": 13, "start_time": 26},
    {"type": "point3", "duration": 14, "start_time": 39},
    {"type": "summary", "duration": 20, "start_time": 53},
    {"type": "cta", "duration": 7, "start_time": 73}
]
```

#### テストスクリプト
`/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_03-03_phase1b-7segment-test.py`

---

### 2.4 Phase 1C: 7枚異なる画像統合テスト
**実施日**: 2025-11-16 03:08:09 JST

#### 検証内容
- WF7 Phase2で取得した7枚の異なる画像を使用
- assetTagマッピングによる画像とセグメントの対応付け
- 外部画像URL（Pexels）からの画像読み込み検証

#### 結果
- ✅ **7枚異なる画像**: 各セグメントで異なる画像を正しく表示
- ✅ **assetTagマッピング**: 正確に対応（例: "SNS 動画制作" → Pexels Photo ID=7193859）
- ⚠️ **Google Drive URL**: HTTP 404エラー（Creatomateは直接アクセス不可）
- ✅ **Pexels URL**: 直接アクセス可能、レンダリング成功
- ✅ **レンダリング時間**: 26.5秒（80秒動画、7枚の異なる外部画像）

#### 重要な発見
**Google Drive URLの問題**:
- Creatomate APIはGoogle Drive直接ダウンロードリンク（`driveWebContentLink`）にアクセスできない
- エラー: `An HTTP 404 status was received while trying to download the file`

**解決策**:
- **短期**: Pexels `originalUrl`を使用（Phase 1Cで検証済み）
- **長期**: Cloudinary等のCDNに画像をアップロードしてURLを取得

#### assetTag → Pexels URL マッピング例
```python
IMAGE_URLS = {
    "SNS 動画制作": "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "動画編集 自動化": "https://images.pexels.com/photos/1181345/pexels-photo-1181345.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "作業時間 削減": "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "テンプレート 活用": "https://images.pexels.com/photos/7947664/pexels-photo-7947664.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "AI 台本生成": "https://images.pexels.com/photos/8849295/pexels-photo-8849295.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "動画制作 効率化": "https://images.pexels.com/photos/3183186/pexels-photo-3183186.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "シェアする": "https://images.pexels.com/photos/3183190/pexels-photo-3183190.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
}
```

#### 動画URL
成功したレンダリング: https://f002.backblazeb2.com/file/creatomate-c8xg3hsxdu/566c7cdd-ea36-452f-b889-36e6039f2f56.mp4

#### テストスクリプト
`/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_03-08_phase1c-7images-integration.py`

---

## 3. WF7 Phase4 Creatomate統合アーキテクチャ

### 3.1 システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                         WF7 Phase4                          │
│                   (動画レンダリング統合)                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌────────────────┐   ┌─────────────────┐
│  Phase1 出力  │   │  Phase2 出力   │   │  Phase3 出力    │
│  (Script JSON)│   │ (画像7枚データ) │   │ (音声・字幕)     │
└───────────────┘   └────────────────┘   └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ RenderScript     │
                    │ 生成ロジック      │
                    │ (Code Node)      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Creatomate API   │
                    │ Call (HTTP Node) │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Polling Loop     │
                    │ (Wait Node)      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ 動画URL取得       │
                    │ + Notion更新     │
                    └──────────────────┘
```

### 3.2 データフロー詳細

#### 3.2.1 入力データソース

**Phase1 Script JSON**:
```json
{
  "segments": [
    {
      "type": "hook",
      "duration": 3,
      "subtitle": "動画制作の時短術",
      "assetTag": "SNS 動画制作"
    },
    ...
  ]
}
```

**Phase2 Assets JSON** (`/tmp/wf7-phase2-webhook-test.txt`参照):
```json
{
  "Assets": [
    {
      "assetTag": "SNS 動画制作",
      "originalUrl": "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?...",
      "driveWebContentLink": "https://drive.google.com/uc?id=...",  // ⚠️ 使用不可
      "driveFileId": "13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg"
    },
    ...
  ]
}
```

**Phase3 Audio/Subtitle JSON**:
```json
{
  "segments": [
    {
      "assetTag": "SNS 動画制作",
      "audioUrl": "https://elevenlabs.io/...",  // 例: ElevenLabs生成音声
      "subtitle": "動画制作の時短術"
    },
    ...
  ]
}
```

#### 3.2.2 RenderScript生成ロジック

**責務**: 上記3つの入力データから、Creatomate RenderScriptを動的に生成

**出力例**:
```json
{
  "template_id": "40ff626c-9e09-4769-b8b9-66e859ecafa9",
  "modifications": {
    "output_format": "mp4",
    "width": 1080,
    "height": 1920,
    "duration": 80,
    "elements": [
      {
        "type": "image",
        "source": "https://images.pexels.com/photos/7193859/...",
        "track": 1,
        "time": 0,
        "duration": 3,
        "animations": [
          {
            "type": "scale",
            "start_scale": "120%",
            "end_scale": "100%",
            "duration": 3,
            "easing": "cubic-in-out",
            "scope": "element"
          }
        ]
      },
      {
        "type": "text",
        "text": "動画制作の時短術",
        "font_family": "Noto Sans JP",
        "font_size": "60 px",
        "color": "#FFFFFF",
        "y": "50%",
        "x": "50%",
        "x_anchor": "50%",
        "y_anchor": "50%",
        "track": 2,
        "time": 0,
        "duration": 3
      },
      {
        "type": "audio",
        "source": "https://elevenlabs.io/...",
        "track": 3,
        "time": 0,
        "duration": 3
      }
    ]
  }
}
```

**重要なルール**:
1. **画像URL**: `originalUrl`を使用（`driveWebContentLink`は使用不可）
2. **Track分離**: track 1=画像、track 2=テキスト、track 3=音声
3. **時間整合性**: `start_time`と`duration`を正確に設定
4. **assetTagマッピング**: Phase1のassetTagでPhase2/3のデータを検索

---

## 4. 実装ステップ

### Step 1: Phase4 Code Node - RenderScript生成
**ファイル**: 新規作成 `workflows/wf7-phase4-creatomate-renderscript.js`

**入力**:
- `$('Phase1').item.json.Script` (Script JSON)
- `$('Phase2').item.json.Assets` (画像7枚データ)
- `$('Phase3').item.json.Audio` (音声・字幕データ)

**処理**:
1. Script JSONから7セグメント構成を読み込み
2. 各セグメントのassetTagでPhase2/3のデータを検索
3. RenderScript elementsを動的生成
   - 画像要素（Ken Burns効果付き）
   - テキスト要素（字幕）
   - 音声要素（TTS生成音声URL）
4. 合計時間を計算
5. RenderScript JSONを返す

**出力**:
```json
{
  "renderScript": { ... }
}
```

---

### Step 2: HTTP Request Node - Creatomate API呼び出し

**エンドポイント**: `POST https://api.creatomate.com/v1/renders`

**ヘッダー**:
```json
{
  "Authorization": "Bearer f7b348f69c3447ee983285fec11bd47e8b10a63e77eeb8f716fd097a8b06a8641c2bae8eb7c47d63a63b36cfeaaef1b7",
  "Content-Type": "application/json"
}
```

**ボディ**:
```json
{{ $json.renderScript }}
```

**出力**:
```json
{
  "id": "566c7cdd-ea36-452f-b889-36e6039f2f56",
  "status": "planned"
}
```

---

### Step 3: Wait Node - ポーリングループ

**目的**: レンダリング完了まで待機

**設定**:
- **待機時間**: 5秒
- **最大試行回数**: 60回（合計300秒 = 5分）
- **条件**: `status === "succeeded"` で終了

**ロジック**:
1. Wait 5秒
2. `GET https://api.creatomate.com/v1/renders/{{ $json.id }}`
3. ステータス確認:
   - `"succeeded"` → 次のノードへ
   - `"failed"` → エラーハンドリング
   - `"rendering"` → Step 3に戻る

---

### Step 4: Code Node - 動画URL抽出 + Notion更新

**入力**:
- Creatomate API レスポンス（`status: "succeeded"`）

**処理**:
1. 動画URLを抽出: `$json.url`
2. Notion Hubデータベースを更新
   - `VideoURL` プロパティに動画URLをセット
   - `Status` を "Phase4完了" に更新

**出力**:
```json
{
  "videoUrl": "https://f002.backblazeb2.com/file/creatomate-c8xg3hsxdu/566c7cdd-ea36-452f-b889-36e6039f2f56.mp4",
  "notionUpdated": true
}
```

---

## 5. エラーハンドリング戦略

### 5.1 Google Drive URL問題

**問題**: Creatomateは`driveWebContentLink`に直接アクセスできない（HTTP 404）

**解決策**:
- **短期**: Pexels `originalUrl`を使用（Phase 1Cで検証済み）
- **中期**: Cloudinary等のCDNに画像をアップロード
- **長期**: WF7 Phase2でCloudinary URLを生成する実装

**実装**:
```javascript
// RenderScript生成時
const imageUrl = asset.originalUrl || asset.cloudinaryUrl;
if (!imageUrl) {
  throw new Error(`画像URLが見つかりません: assetTag=${segment.assetTag}`);
}
```

---

### 5.2 レンダリングタイムアウト

**問題**: ポーリングが300秒経過しても完了しない

**対策**:
1. **タイムアウト検知**: 60回ポーリング後、エラーを返す
2. **Notion更新**: `Status`を"Phase4失敗"に更新
3. **通知**: LINE通知でエラーを報告

**実装**:
```javascript
if (pollCount >= 60) {
  return {
    error: "レンダリングタイムアウト（300秒経過）",
    renderId: renderId,
    status: "timeout"
  };
}
```

---

### 5.3 レンダリング失敗

**問題**: Creatomate APIが`status: "failed"`を返す

**対策**:
1. **エラーメッセージ取得**: `error_message`を記録
2. **Notion更新**: エラー内容を`ErrorLog`プロパティに記録
3. **リトライ不可**: 手動で原因調査が必要

**実装**:
```javascript
if (status === "failed") {
  return {
    error: "レンダリング失敗",
    errorMessage: $json.error_message,
    renderId: renderId
  };
}
```

---

## 6. テスト計画

### 6.1 Unit Test（ローカルPython検証）

**目的**: 各コンポーネントの単体動作確認

#### Test 1: RenderScript生成ロジック
- **入力**: Phase1/2/3のモックデータ
- **出力**: 正しいRenderScript JSON
- **検証項目**:
  - ✅ 7セグメント全て含まれるか
  - ✅ assetTagマッピングが正確か
  - ✅ 時間設定（start_time, duration）が正確か

#### Test 2: Creatomate API呼び出し
- **Phase 0-1C完了**: ✅
- **検証項目**:
  - ✅ 日本語テキスト表示
  - ✅ 7セグメント構成
  - ✅ 7枚異なる画像統合

---

### 6.2 Integration Test（n8nワークフロー全体）

**目的**: Phase1-4の完全な統合動作確認

#### Test Scenario 1: 正常系
1. Phase1でScript JSONを生成
2. Phase2で画像7枚を取得（Pexels `originalUrl`使用）
3. Phase3で音声・字幕を生成
4. Phase4でCreatomate呼び出し
5. 動画URLを取得してNotion更新

**期待結果**:
- ✅ 80秒動画が生成される
- ✅ 7枚の異なる画像が表示される
- ✅ 日本語字幕が各セグメントで切り替わる
- ✅ 音声が正しく再生される
- ✅ Notion Hubに動画URLが記録される

#### Test Scenario 2: エラーケース
- **画像URL取得失敗**: Phase2でPexels APIエラー
- **音声生成失敗**: Phase3でElevenLabs APIエラー
- **レンダリングタイムアウト**: 300秒経過
- **Creatomateレンダリング失敗**: invalid URL error

**期待結果**:
- ❌ エラーメッセージをNotionに記録
- ❌ LINE通知でエラー報告
- ❌ `Status`を"Phase4失敗"に更新

---

### 6.3 Performance Test

**目的**: レンダリング時間とリソース使用量の測定

#### ベンチマーク（Phase 1C検証結果）
- **80秒動画**: 26.5秒でレンダリング完了
- **7枚の異なる外部画像**: レンダリング時間に大きな影響なし
- **Creatomate API応答**: 初回レスポンス<1秒、ポーリング間隔5秒

#### 目標値
- **レンダリング時間**: <60秒（80秒動画）
- **API呼び出し回数**: <15回（ポーリング）
- **合計処理時間**: <90秒（Phase4全体）

---

## 7. リスクと対策

### 7.1 高リスク

#### リスク1: Google Drive URL問題
**影響度**: 🔴 高
**発生確率**: 🔴 高（Phase 1Cで確認済み）
**対策**: Pexels `originalUrl`使用 → Cloudinary移行

#### リスク2: Creatomate API制限
**影響度**: 🔴 高
**発生確率**: 🟡 中
**対策**: レート制限確認、エラーハンドリング強化

---

### 7.2 中リスク

#### リスク3: レンダリング時間変動
**影響度**: 🟡 中
**発生確率**: 🟡 中
**対策**: タイムアウト値を余裕を持って設定（300秒）

#### リスク4: assetTagマッピングミス
**影響度**: 🟡 中
**発生確率**: 🟢 低
**対策**: Unit Testで厳密に検証

---

## 8. 次のアクション

### 8.1 即座に実施
- [ ] **Step 1実装**: RenderScript生成ロジック（Code Node）
- [ ] **Step 2実装**: HTTP Request Node設定
- [ ] **Step 3実装**: Wait Node + ポーリングループ
- [ ] **Step 4実装**: 動画URL抽出 + Notion更新

### 8.2 検証・テスト
- [ ] **Unit Test**: RenderScript生成ロジックのローカルテスト
- [ ] **Integration Test**: Phase1-4完全統合テスト（n8n）
- [ ] **Performance Test**: レンダリング時間測定

### 8.3 ドキュメント化
- [ ] **エラーログ**: Notion Hubにエラー記録フィールド追加
- [ ] **運用手順書**: Phase4エラー発生時の対処手順

---

## 9. 参考資料

### 9.1 検証済みスクリプト
- Phase 0: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-01-16_10-30_phase0-creatomate-test.py`
- Phase 0A: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-01-16_10-55_phase0-text-only-test.py`
- Phase 1: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_02-58_phase1-3segment-test.py`
- Phase 1B: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_03-03_phase1b-7segment-test.py`
- Phase 1C: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_03-08_phase1c-7images-integration.py`

### 9.2 外部リソース
- Creatomate API ドキュメント: https://creatomate.com/docs/api/introduction
- Creatomate RenderScript リファレンス: https://creatomate.com/docs/json/introduction
- WF7 Phase2 出力データ: `/tmp/wf7-phase2-webhook-test.txt`

### 9.3 Creatomate認証情報
- **API Key**: `f7b348f69c3447ee983285fec11bd47e8b10a63e77eeb8f716fd097a8b06a8641c2bae8eb7c47d63a63b36cfeaaef1b7`
- **Template ID**: `40ff626c-9e09-4769-b8b9-66e859ecafa9`

---

## 10. まとめ

Phase 0-1Cの検証により、Creatomate APIを使用した動画レンダリング機能の実装が可能であることが確認されました。

**主要な成果**:
- ✅ 日本語テキスト表示機能の動作確認
- ✅ 7セグメント構成（80秒動画）のレンダリング成功
- ✅ 7枚の異なる画像統合の成功
- ✅ assetTagマッピングの動作確認
- ⚠️ Google Drive URL問題の発見と対策確立

**次のステップ**:
WF7 Phase4の実装に進み、Phase1-3のデータを統合してCreatomate APIを呼び出す完全なワークフローを構築します。
