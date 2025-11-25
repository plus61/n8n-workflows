# WF7 Phase1/2/3 統合テスト計画

**作成日時**: 2025-11-16 09:15:52 JST

## 📋 テスト概要

WF7 Phase4（Creatomate統合ワークフロー）の実装完了に伴い、Phase1（台本生成）、Phase2（素材取得）、Phase3（音声・字幕生成）との統合テストを実施する。

### テスト目的
1. **データ契約の検証**: Phase1/2/3の出力がPhase4の入力要件を満たすことを確認
2. **assetTagマッピングの検証**: Phase1のassetTagがPhase2/3で正しく紐付けられることを確認
3. **エンドツーエンド動作確認**: 台本生成から動画生成までの完全フローが動作することを確認
4. **エラーハンドリング検証**: 各フェーズでのエラーケースが適切に処理されることを確認
5. **Notion Hub連携検証**: 動画生成完了後のNotion更新が正しく動作することを確認

---

## 🔍 Phase1/2/3 出力要件

### Phase1（台本生成）出力要件

**必須フィールド**:
```javascript
{
  TaskID: "notion-page-id",           // NotionページID（Notion更新時に使用）
  Script: {
    title: "動画タイトル",             // 動画タイトル（Notion更新時に使用）
    segments: [
      {
        type: "hook",                  // セグメントタイプ（hook/intro/point1/point2/point3/summary/cta）
        duration: 3,                   // 秒数（整数）
        subtitle: "動画制作の時短術",   // 字幕テキスト（非空文字列）
        assetTag: "SNS 動画制作"       // 素材識別子（Phase2/3とのマッピングに使用）
      },
      // ... 合計7セグメント（hook, intro, point1, point2, point3, summary, cta）
    ]
  }
}
```

**検証項目**:
- ✅ TaskIDが有効なNotion Page IDであること
- ✅ Script.titleが非空文字列であること
- ✅ Script.segmentsが7要素の配列であること
- ✅ 各セグメントにtype, duration, subtitle, assetTagが存在すること
- ✅ durationが正の整数であること
- ✅ assetTagが一意であること（重複なし）
- ✅ セグメントタイプが正しい順序であること（hook → intro → point1 → point2 → point3 → summary → cta）

---

### Phase2（素材取得）出力要件

**必須フィールド**:
```javascript
{
  Assets: [
    {
      assetTag: "SNS 動画制作",                // Phase1のassetTagと一致
      originalUrl: "https://images.pexels.com/...",  // Pexels直接URL（必須）
      cloudinaryUrl: "https://res.cloudinary.com/..." // Cloudinary URL（オプション）
    },
    // ... 合計7画像（Phase1の7セグメントに対応）
  ]
}
```

**検証項目**:
- ✅ Assetsが7要素の配列であること
- ✅ 各AssetにassetTag, originalUrlが存在すること
- ✅ assetTagがPhase1のassetTagと完全一致すること（全7個）
- ✅ originalUrlが有効なHTTP(S) URLであること
- ✅ originalUrlがアクセス可能であること（404エラーなし）
- ⚠️ cloudinaryUrlは存在しなくても可（Phase4はoriginalUrlを優先使用）

**重要な制約**:
- **Google Drive URLは使用不可**: `drive.google.com`のURLは404エラーになるため、Pexels直接URLを使用すること
- **originalUrl必須**: Phase4はoriginalUrlを最優先で使用するため、必ず有効なURLを設定すること

---

### Phase3（音声・字幕生成）出力要件

**必須フィールド**:
```javascript
{
  Audio: {
    segments: [
      {
        assetTag: "SNS 動画制作",              // Phase1のassetTagと一致
        audioUrl: "https://elevenlabs.io/...",  // TTS音声URL
        subtitle: "動画制作の時短術"            // 字幕テキスト（Phase1と同じでも可）
      },
      // ... 合計7音声（Phase1の7セグメントに対応）
    ]
  }
}
```

**検証項目**:
- ✅ Audio.segmentsが7要素の配列であること
- ✅ 各SegmentにassetTag, audioUrl, subtitleが存在すること
- ✅ assetTagがPhase1のassetTagと完全一致すること（全7個）
- ✅ audioUrlが有効なHTTP(S) URLであること
- ✅ audioUrlがアクセス可能であること（音声ファイルが存在）
- ✅ subtitleが非空文字列であること

---

## 🔗 データ契約とassetTagマッピング

### assetTagの役割

**assetTag**は、Phase1/2/3のデータを紐付けるための**一意な識別子**です。

**マッピングルール**:
```
Phase1.segments[i].assetTag
  ↓
Phase2.Assets.find(asset => asset.assetTag === Phase1.segments[i].assetTag)
  ↓
Phase3.Audio.segments.find(segment => segment.assetTag === Phase1.segments[i].assetTag)
  ↓
Phase4: 3つのデータを統合してCreatomate RenderScriptを生成
```

### データフロー図

```
[Phase1] TaskID, Script JSON (7 segments)
    ├─ assetTag: "SNS 動画制作" → duration: 3, subtitle: "..."
    ├─ assetTag: "動画編集 自動化" → duration: 10, subtitle: "..."
    ├─ ... (合計7セグメント)
    ↓
[Phase2] Assets (7 images)
    ├─ assetTag: "SNS 動画制作" → originalUrl: "https://images.pexels.com/..."
    ├─ assetTag: "動画編集 自動化" → originalUrl: "https://images.pexels.com/..."
    ├─ ... (合計7画像)
    ↓
[Phase3] Audio.segments (7 audios)
    ├─ assetTag: "SNS 動画制作" → audioUrl: "https://elevenlabs.io/...", subtitle: "..."
    ├─ assetTag: "動画編集 自動化" → audioUrl: "https://elevenlabs.io/...", subtitle: "..."
    ├─ ... (合計7音声)
    ↓
[Phase4] RenderScript生成 → Creatomate API → 動画URL → Notion更新
```

### データ整合性チェック

**Phase4のGenerate RenderScriptノードで実施される検証**:

1. **Phase1データ検証**:
   - Script JSONが存在するか
   - segments配列が存在するか
   - セグメント数が7個か

2. **Phase2データ検証**:
   - Assets配列が存在するか
   - 各セグメントのassetTagに対応するAssetが存在するか
   - originalUrlが存在するか

3. **Phase3データ検証**:
   - Audio.segments配列が存在するか
   - 各セグメントのassetTagに対応するAudio Segmentが存在するか
   - audioUrlが存在するか

4. **エラーハンドリング**:
   - 不足しているデータがある場合、`NodeOperationError`を投げてワークフロー停止
   - エラーメッセージには不足しているassetTagを含める

---

## 🧪 テストシナリオ

### 正常系シナリオ

#### TC-001: 完全なデータフロー（Happy Path）

**前提条件**:
- Phase1が正常に7セグメントのScript JSONを生成
- Phase2が7画像の素材を取得（originalUrl有効）
- Phase3が7音声の素材を生成（audioUrl有効）
- Notion HubにTaskIDに対応するページが存在

**テストステップ**:
1. Phase1を実行してScript JSONとTaskIDを取得
2. Phase2を実行して7画像を取得
3. Phase3を実行して7音声を生成
4. Phase4を実行してRenderScriptを生成
5. Creatomate APIを呼び出してレンダリング開始
6. ポーリングループでレンダリング完了を待機
7. 動画URLを抽出
8. Notion Hubを更新

**期待結果**:
- ✅ RenderScriptが21要素（7セグメント×3要素）で生成される
- ✅ Creatomate APIが正常に応答（render IDを返す）
- ✅ ポーリングループが最大60回以内で完了
- ✅ statusが"succeeded"になる
- ✅ 動画URLが取得できる
- ✅ Notion Hubの以下プロパティが更新される:
  - VideoURL: 動画URL
  - Status: "Phase4完了"
  - CompletedAt: ISO 8601形式の日時

---

### 異常系シナリオ

#### TC-002: Phase1データ不足（segments配列が空）

**前提条件**:
- Phase1のScript JSONにsegments配列が存在しない、または空配列

**期待結果**:
- ❌ Generate RenderScriptノードで`NodeOperationError`が発生
- エラーメッセージ: "Phase1のScript JSONにセグメントが含まれていません。"

---

#### TC-003: Phase2データ不足（assetTagマッピング失敗）

**前提条件**:
- Phase1が7セグメントを生成
- Phase2が5画像のみ取得（2個のassetTagに対応する画像が不足）

**期待結果**:
- ❌ Generate RenderScriptノードで`NodeOperationError`が発生
- エラーメッセージ: `assetTag="XXX"に対応する画像データがPhase2に見つかりません。`

---

#### TC-004: Phase3データ不足（audioUrl欠損）

**前提条件**:
- Phase1が7セグメントを生成
- Phase2が7画像を取得
- Phase3が7音声を生成するが、1つのaudioUrlがnull

**期待結果**:
- ❌ Generate RenderScriptノードで`NodeOperationError`が発生
- エラーメッセージ: `assetTag="XXX"の音声URLが見つかりません。`

---

#### TC-005: Creatomate API呼び出し失敗（認証エラー）

**前提条件**:
- Phase1/2/3が正常に完了
- Creatomate API KEYが無効または期限切れ

**期待結果**:
- ❌ Call Creatomate APIノードで401 Unauthorized エラー
- ワークフロー停止

---

#### TC-006: Creatomate レンダリング失敗（status="failed"）

**前提条件**:
- Creatomate APIがrender IDを返すが、レンダリング中にエラー発生

**期待結果**:
- ⚠️ Check Render Statusノードでstatus="failed"を検出
- Check If Succeededノードがfalseを出力
- Check If Continue Pollingノードがfalseを出力（ループ終了）
- ワークフロー終了（Notion更新なし）

---

#### TC-007: Creatomate レンダリングタイムアウト（60回ポーリング後もrendering）

**前提条件**:
- Creatomate APIがrender IDを返すが、300秒（5分）経過してもレンダリング完了しない

**期待結果**:
- ⚠️ Increment CounterノードでpollCounterが60に到達
- Check If Continue Pollingノードがfalseを出力（ループ終了）
- ワークフロー終了（Notion更新なし）

---

#### TC-008: Notion更新失敗（TaskID不正）

**前提条件**:
- Phase1/2/3/4が正常に完了し、動画URLを取得
- Phase1のTaskIDがNotion Hubに存在しない、またはアクセス権限なし

**期待結果**:
- ❌ Update Notion Hubノードで404 Not Found または 403 Forbidden エラー
- ワークフロー停止

---

### 境界値シナリオ

#### TC-009: 最小セグメント時間（1秒）

**前提条件**:
- Phase1が1秒のセグメントを含む（例: duration=1）

**期待結果**:
- ✅ RenderScriptが正常に生成される
- ✅ Creatomate APIがエラーなく処理

---

#### TC-010: 最大セグメント時間（120秒）

**前提条件**:
- Phase1が120秒のセグメントを含む（例: summary duration=120）

**期待結果**:
- ✅ RenderScriptが正常に生成される（totalDuration=200秒程度）
- ✅ Creatomate APIがエラーなく処理

---

#### TC-011: 日本語字幕の最大文字数（100文字）

**前提条件**:
- Phase1のsubtitleに100文字の日本語テキスト

**期待結果**:
- ✅ RenderScriptが正常に生成される
- ✅ Creatomate APIで日本語フォント（Noto Sans JP）が正しく適用される

---

## 📦 モックデータ仕様

### Phase1 モックデータ

**ファイル名**: `phase1-mock-output.json`

```json
{
  "TaskID": "1234567890abcdef12345678",
  "Script": {
    "title": "【テスト】SNS動画自動生成フロー検証",
    "segments": [
      {
        "type": "hook",
        "duration": 3,
        "subtitle": "これが未来の動画制作",
        "assetTag": "test-hook-001"
      },
      {
        "type": "intro",
        "duration": 10,
        "subtitle": "効率化がもたらす変革",
        "assetTag": "test-intro-001"
      },
      {
        "type": "point1",
        "duration": 13,
        "subtitle": "作業時間を70%削減した実例",
        "assetTag": "test-point1-001"
      },
      {
        "type": "point2",
        "duration": 13,
        "subtitle": "品質を保ちながら高速化",
        "assetTag": "test-point2-001"
      },
      {
        "type": "point3",
        "duration": 14,
        "subtitle": "AIがもたらす新しい価値",
        "assetTag": "test-point3-001"
      },
      {
        "type": "summary",
        "duration": 20,
        "subtitle": "自動化で変わる未来の働き方",
        "assetTag": "test-summary-001"
      },
      {
        "type": "cta",
        "duration": 7,
        "subtitle": "今すぐ試してみよう！",
        "assetTag": "test-cta-001"
      }
    ]
  }
}
```

---

### Phase2 モックデータ

**ファイル名**: `phase2-mock-output.json`

```json
{
  "Assets": [
    {
      "assetTag": "test-hook-001",
      "originalUrl": "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-hook-001.jpg"
    },
    {
      "assetTag": "test-intro-001",
      "originalUrl": "https://images.pexels.com/photos/1181345/pexels-photo-1181345.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-intro-001.jpg"
    },
    {
      "assetTag": "test-point1-001",
      "originalUrl": "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-point1-001.jpg"
    },
    {
      "assetTag": "test-point2-001",
      "originalUrl": "https://images.pexels.com/photos/7947664/pexels-photo-7947664.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-point2-001.jpg"
    },
    {
      "assetTag": "test-point3-001",
      "originalUrl": "https://images.pexels.com/photos/8849295/pexels-photo-8849295.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-point3-001.jpg"
    },
    {
      "assetTag": "test-summary-001",
      "originalUrl": "https://images.pexels.com/photos/3183186/pexels-photo-3183186.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-summary-001.jpg"
    },
    {
      "assetTag": "test-cta-001",
      "originalUrl": "https://images.pexels.com/photos/3183190/pexels-photo-3183190.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/test-cta-001.jpg"
    }
  ]
}
```

---

### Phase3 モックデータ

**ファイル名**: `phase3-mock-output.json`

```json
{
  "Audio": {
    "segments": [
      {
        "assetTag": "test-hook-001",
        "audioUrl": "https://storage.example.com/audio/test-hook-001.mp3",
        "subtitle": "これが未来の動画制作"
      },
      {
        "assetTag": "test-intro-001",
        "audioUrl": "https://storage.example.com/audio/test-intro-001.mp3",
        "subtitle": "効率化がもたらす変革"
      },
      {
        "assetTag": "test-point1-001",
        "audioUrl": "https://storage.example.com/audio/test-point1-001.mp3",
        "subtitle": "作業時間を70%削減した実例"
      },
      {
        "assetTag": "test-point2-001",
        "audioUrl": "https://storage.example.com/audio/test-point2-001.mp3",
        "subtitle": "品質を保ちながら高速化"
      },
      {
        "assetTag": "test-point3-001",
        "audioUrl": "https://storage.example.com/audio/test-point3-001.mp3",
        "subtitle": "AIがもたらす新しい価値"
      },
      {
        "assetTag": "test-summary-001",
        "audioUrl": "https://storage.example.com/audio/test-summary-001.mp3",
        "subtitle": "自動化で変わる未来の働き方"
      },
      {
        "assetTag": "test-cta-001",
        "audioUrl": "https://storage.example.com/audio/test-cta-001.mp3",
        "subtitle": "今すぐ試してみよう!"
      }
    ]
  }
}
```

---

## 🏗️ Notion Hub スキーマ要件

### 必須プロパティ

Notion Hubデータベースには以下のプロパティが必要です：

| プロパティ名 | タイプ | 説明 | Phase4での使用 |
|------------|-------|------|----------------|
| **VideoURL** | URL または Text | 生成された動画のURL | Phase4で書き込み |
| **Status** | Select | ワークフロー進捗状態 | Phase4で"Phase4完了"に更新 |
| **CompletedAt** | Date | Phase4完了日時 | Phase4で書き込み（ISO 8601形式） |
| **Title** | Title | タスクタイトル | Phase1で設定、Phase4で参照 |
| **TaskID** | （ページID） | NotionページID | Phase1で生成、Phase4で参照 |

### Statusプロパティの選択肢

**Status**プロパティには以下の選択肢が必要です：

- "Phase1完了"
- "Phase2完了"
- "Phase3完了"
- **"Phase4完了"** ← Phase4で設定
- "エラー"
- "進行中"

### Phase4でのNotion更新処理

**Update Notion Hubノード**の設定:

```json
{
  "resource": "databasePage",
  "operation": "update",
  "pageId": "={{ $json.taskId }}",  // Phase1から引き継いだTaskID
  "propertiesUi": {
    "propertyValues": [
      {
        "key": "VideoURL",
        "textValue": "={{ $json.videoUrl }}"  // Creatomateから取得した動画URL
      },
      {
        "key": "Status",
        "selectValue": "Phase4完了"
      },
      {
        "key": "CompletedAt",
        "dateValue": "={{ $json.completedAt }}"  // ISO 8601形式の日時
      }
    ]
  }
}
```

### Notion Credentials設定

**必須設定**:
- Notion統合の作成（Notion Workspace Settings → Integrations）
- データベースへのアクセス権限付与
- n8nでのNotion Credentials設定（OAuth2またはInternal Integration Token）
- データベースIDの取得と設定

---

## 🔌 n8nワークフロー接続戦略

### Phase4ワークフローのインポート

**ファイル**: `2025-11-16_08-59_wf7-phase4-creatomate-integration.json`

**インポート手順**:
1. Railway n8n-pythonサービスにアクセス
2. ワークフロー管理 → インポート
3. JSONファイルをアップロード
4. インポート後、以下を設定:
   - Creatomate API KEY（現在ハードコード、本番環境ではCredentials化推奨）
   - Notion Credentials（Update Notion Hubノード）

---

### Phase1/2/3との接続方法

**オプション1: Manual Triggerで個別実行（推奨：テスト段階）**

**メリット**:
- 各フェーズの出力を個別に確認可能
- デバッグが容易
- 段階的な検証が可能

**手順**:
1. Phase1を手動実行 → 出力をコピー
2. Phase4のManual Triggerに出力を貼り付け（Phase1, Phase2, Phase3データをシミュレート）
3. Phase4を実行して検証

**デメリット**:
- 手動操作が必要
- 本番運用には不向き

---

**オプション2: Execute Workflow Nodeで連鎖実行（推奨：本番環境）**

**メリット**:
- 完全自動化
- エンドツーエンドフロー実現
- エラー時の自動停止

**手順**:
1. Phase1ワークフローの最後に**Execute Workflow Node**を追加
   - Target Workflow: Phase2
   - Source Data: Phase1の出力をPhase2に渡す

2. Phase2ワークフローの最後に**Execute Workflow Node**を追加
   - Target Workflow: Phase3
   - Source Data: Phase1 + Phase2の出力をPhase3に渡す

3. Phase3ワークフローの最後に**Execute Workflow Node**を追加
   - Target Workflow: Phase4
   - Source Data: Phase1 + Phase2 + Phase3の出力をPhase4に渡す

**データ受け渡しパターン**:
```javascript
// Phase1 → Phase2
$('Phase1').item.json

// Phase2 → Phase3
{
  Phase1: $('Phase1').item.json,
  Phase2: $json
}

// Phase3 → Phase4
{
  Phase1: $('Phase1').item.json,
  Phase2: $('Phase2').item.json,
  Phase3: $json
}
```

---

**オプション3: Webhook Triggerで非同期実行（推奨：マイクロサービス型）**

**メリット**:
- フェーズ間の疎結合
- 各フェーズの独立性
- スケーラビリティ

**手順**:
1. Phase4のManual TriggerをWebhook Triggerに変更
2. Phase3の最後にHTTP Request Nodeを追加
   - URL: Phase4のWebhook URL
   - Method: POST
   - Body: Phase1 + Phase2 + Phase3の出力

**デメリット**:
- Webhook URL管理が必要
- 認証設定が必要（本番環境）

---

## 📝 テスト実施計画

### フェーズ1: 単体テスト（Phase4のみ）

**目的**: Phase4ワークフローが正しく動作することを確認

**手順**:
1. モックデータ（phase1/2/3-mock-output.json）を用意
2. Phase4をn8nにインポート
3. Manual Triggerにモックデータを設定
4. Phase4を実行
5. 以下を検証:
   - ✅ RenderScriptが21要素で生成される
   - ✅ Creatomate APIが正常応答
   - ✅ ポーリングループが動作
   - ✅ 動画URLが取得できる
   - ✅ Notion Hubが更新される

**期間**: 1日

---

### フェーズ2: Phase3 → Phase4統合テスト

**目的**: Phase3の実際の出力でPhase4が動作することを確認

**手順**:
1. Phase3を実行して実際の音声データを生成
2. Phase3の出力をPhase4に渡す
3. Phase4を実行
4. データマッピングを検証

**期間**: 1日

---

### フェーズ3: Phase2 → Phase3 → Phase4統合テスト

**目的**: Phase2の実際の出力でPhase3/4が動作することを確認

**手順**:
1. Phase2を実行して実際の画像データを取得
2. Phase2の出力をPhase3に渡す
3. Phase3の出力をPhase4に渡す
4. データマッピングを検証

**期間**: 1日

---

### フェーズ4: エンドツーエンドテスト（Phase1 → Phase2 → Phase3 → Phase4）

**目的**: 完全なフローが動作することを確認

**手順**:
1. Phase1を実行して台本生成
2. Phase1の出力をPhase2に渡す
3. Phase2の出力をPhase3に渡す
4. Phase3の出力をPhase4に渡す
5. Notion Hubの最終状態を確認

**期間**: 2日

---

### フェーズ5: 異常系テスト

**目的**: エラーハンドリングが正しく動作することを確認

**手順**:
1. TC-002からTC-011までの異常系・境界値シナリオを実行
2. エラーメッセージとワークフロー停止を確認
3. エラーハンドリングの改善点を洗い出し

**期間**: 2日

---

### フェーズ6: 本番環境デプロイ準備

**目的**: 本番環境での動作を確認

**手順**:
1. Creatomate API KEYをCredentials化
2. Notion Credentialsを本番環境用に設定
3. ワークフロー連鎖設定（Execute Workflow Node または Webhook）
4. 本番環境でのスモークテスト実行

**期間**: 1日

---

## ✅ 検証基準

### 合格基準

**Phase4単体テスト**:
- ✅ 正常系シナリオ（TC-001）が成功する
- ✅ RenderScriptが正しく生成される（21要素）
- ✅ Creatomate APIが正常に応答する
- ✅ 動画URLが取得できる
- ✅ Notion Hubが正しく更新される

**Phase1/2/3統合テスト**:
- ✅ 各フェーズの出力がPhase4の入力要件を満たす
- ✅ assetTagマッピングが100%正確である
- ✅ エンドツーエンドフローが成功する

**異常系テスト**:
- ✅ 全ての異常系シナリオでエラーハンドリングが動作する
- ✅ エラーメッセージが明確で問題箇所が特定できる

---

## 📌 次のアクション

### 即座に実施すべきタスク

1. **モックデータの作成**
   - phase1-mock-output.json
   - phase2-mock-output.json
   - phase3-mock-output.json

2. **Notion Hub設定確認**
   - Hubデータベースのスキーマ確認
   - プロパティ名の一致確認（VideoURL, Status, CompletedAt）
   - Status選択肢の確認（"Phase4完了"が存在するか）

3. **Phase4のn8nインポート**
   - Railway n8n-pythonサービスへアクセス
   - `2025-11-16_08-59_wf7-phase4-creatomate-integration.json`をインポート
   - Creatomate API KEYの設定確認
   - Notion Credentialsの設定

4. **Phase4単体テスト実行（フェーズ1）**
   - モックデータでのドライラン
   - 各ノードの出力検証
   - エラーケースの確認

### 中期的なタスク

5. **Phase3統合テスト（フェーズ2）**
6. **Phase2統合テスト（フェーズ3）**
7. **エンドツーエンドテスト（フェーズ4）**
8. **異常系テスト（フェーズ5）**
9. **本番デプロイ準備（フェーズ6）**

---

## 📊 テスト進捗管理

### テスト進捗トラッカー

| テストID | テスト名 | ステータス | 実施日 | 結果 | 備考 |
|---------|---------|-----------|-------|------|------|
| TC-001 | 完全なデータフロー | 🔄 未実施 | - | - | - |
| TC-002 | Phase1データ不足 | 🔄 未実施 | - | - | - |
| TC-003 | Phase2データ不足 | 🔄 未実施 | - | - | - |
| TC-004 | Phase3データ不足 | 🔄 未実施 | - | - | - |
| TC-005 | Creatomate API認証エラー | 🔄 未実施 | - | - | - |
| TC-006 | Creatomate レンダリング失敗 | 🔄 未実施 | - | - | - |
| TC-007 | Creatomate タイムアウト | 🔄 未実施 | - | - | - |
| TC-008 | Notion更新失敗 | 🔄 未実施 | - | - | - |
| TC-009 | 最小セグメント時間 | 🔄 未実施 | - | - | - |
| TC-010 | 最大セグメント時間 | 🔄 未実施 | - | - | - |
| TC-011 | 日本語字幕最大文字数 | 🔄 未実施 | - | - | - |

**凡例**:
- 🔄 未実施
- ✅ 成功
- ❌ 失敗
- ⚠️ 警告あり

---

**ステータス**: ✅ Phase1/2/3統合テスト計画策定完了
**次のマイルストーン**: モックデータ作成 & Phase4単体テスト実施

---

**関連ドキュメント**:
- [Phase4完成検証ドキュメント](/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_09-11_wf7-phase4-完成検証.md)
- [Phase4ワークフローJSON](/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_08-59_wf7-phase4-creatomate-integration.json)
- [RenderScript生成ロジック](/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_03-19_wf7-phase4-renderscript.js)
