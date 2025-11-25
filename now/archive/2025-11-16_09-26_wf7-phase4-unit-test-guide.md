# WF7 Phase4 - Creatomate統合 単体テスト実行ガイド

**作成日時**: 2025-11-16 09:26:32 JST

## 📋 テスト概要

### 目的
Phase4ワークフロー（Creatomate統合）をモックデータで単体テストし、Phase1/2/3との統合前に動作を検証する。

### テスト範囲
- **対象フェーズ**: フェーズ1: 単体テスト（Phase4のみ）
- **使用データ**: モックデータ（phase1/2/3-mock-output.json）
- **検証対象**: 10ノードすべての動作
- **実行環境**: Railway n8nインスタンス（本番環境）

### テストシナリオ
- **TC-001**: Happy Path - 正常系での完全フロー実行
- **RenderScript生成**: 21要素（7セグメント×3要素）の正確な生成
- **Creatomate API呼び出し**: POST /v1/renders の成功
- **ポーリングループ**: 最大60回×5秒のステータス確認
- **Notion更新**: VideoURL, Status, CompletedAtの正確な更新

---

## 📂 事前準備

### 1. 必要なファイルの確認

#### Phase4ワークフローファイル
```bash
ls -lh /Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_08-59_wf7-phase4-creatomate-integration.json
```
**期待値**: 16KB、10ノード構成のn8n JSONファイル

#### モックデータファイル（3ファイル）
```bash
ls -lh /Users/yuichiroooosuger/Desktop/n8n-workflows/now/phase*.json
```

**期待される3ファイル**:
- `phase1-mock-output.json` - TaskID + 7セグメント（Script JSON）
- `phase2-mock-output.json` - 7画像（Assets配列）
- `phase3-mock-output.json` - 7音声（Audio.segments配列）

### 2. モックデータ整合性の確認

すべてのファイルで **7つのassetTag** が一致していることを確認:
- test-hook-001
- test-intro-001
- test-point1-001
- test-point2-001
- test-point3-001
- test-summary-001
- test-cta-001

### 3. n8nアクセス情報

**Railway n8nインスタンス**:
```bash
railway open --service n8n-python
```

**認証情報**: Railway Secretsに保存されているn8n認証情報を使用

---

## 🔧 ワークフローインポート手順

### Step 1: n8n UIを開く

1. Railway Dashboardから `n8n-python` サービスを開く
2. サービスURLをクリックしてn8n UIにアクセス
3. 認証情報でログイン

### Step 2: 新しいワークフローを作成

1. 左サイドバーの「Workflows」をクリック
2. 右上の「+ Add Workflow」ボタンをクリック
3. 空のワークフローが開かれる

### Step 3: JSONからインポート

1. 右上の「⋮」（三点メニュー）をクリック
2. 「Import from File...」を選択
3. ファイル選択ダイアログで以下のファイルを選択:
   ```
   /Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-16_08-59_wf7-phase4-creatomate-integration.json
   ```
4. 「Open」をクリック
5. ワークフローがインポートされる（10ノードが配置される）

### Step 4: ワークフロー名の確認

- インポート後のワークフロー名: 「WF7 Phase4 - Creatomate Integration」
- 必要に応じて名前を変更: 「WF7 Phase4 - Unit Test」

### Step 5: ワークフローの保存

1. 右上の「Save」ボタンをクリック
2. ワークフローIDが生成される
3. 保存完了を確認

---

## 📌 モックデータ設定方法

### Step 1: Manual Triggerノードを選択

1. キャンバス上の「Manual Trigger」ノードをクリック
2. 右パネルに設定画面が表示される

### Step 2: モックデータのピン留め

#### Phase1データのピン留め

1. Manual Triggerノードの「Execute Node」をクリック
2. 出力タブで「Edit Output」をクリック
3. 以下のJSONを貼り付け:

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

4. 「Pin data」ボタンをクリック
5. Phase1データがピン留めされる

#### Phase2データの追加

**重要**: n8nのManual Triggerは単一の出力しか持たないため、Phase2/3データを同じ出力に統合する必要があります。

**統合されたモックデータ**（Phase1/2/3すべてを含む）:

```json
{
  "Phase1": {
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
  },
  "Phase2": {
    "Assets": [
      {
        "assetTag": "test-hook-001",
        "originalUrl": "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-hook-001.jpg"
      },
      {
        "assetTag": "test-intro-001",
        "originalUrl": "https://images.pexels.com/photos/1181345/pexels-photo-1181345.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-intro-001.jpg"
      },
      {
        "assetTag": "test-point1-001",
        "originalUrl": "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-point1-001.jpg"
      },
      {
        "assetTag": "test-point2-001",
        "originalUrl": "https://images.pexels.com/photos/7947664/pexels-photo-7947664.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-point2-001.jpg"
      },
      {
        "assetTag": "test-point3-001",
        "originalUrl": "https://images.pexels.com/photos/8849295/pexels-photo-8849295.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-point3-001.jpg"
      },
      {
        "assetTag": "test-summary-001",
        "originalUrl": "https://images.pexels.com/photos/3183186/pexels-photo-3183186.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-summary-001.jpg"
      },
      {
        "assetTag": "test-cta-001",
        "originalUrl": "https://images.pexels.com/photos/3183190/pexels-photo-3183190.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1731726000/test-cta-001.jpg"
      }
    ]
  },
  "Phase3": {
    "Audio": {
      "segments": [
        {
          "assetTag": "test-hook-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-hook-001.mp3",
          "subtitle": "これが未来の動画制作"
        },
        {
          "assetTag": "test-intro-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-intro-001.mp3",
          "subtitle": "効率化がもたらす変革"
        },
        {
          "assetTag": "test-point1-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-point1-001.mp3",
          "subtitle": "作業時間を70%削減した実例"
        },
        {
          "assetTag": "test-point2-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-point2-001.mp3",
          "subtitle": "品質を保ちながら高速化"
        },
        {
          "assetTag": "test-point3-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-point3-001.mp3",
          "subtitle": "AIがもたらす新しい価値"
        },
        {
          "assetTag": "test-summary-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-summary-001.mp3",
          "subtitle": "自動化で変わる未来の働き方"
        },
        {
          "assetTag": "test-cta-001",
          "audioUrl": "https://storage.googleapis.com/elevenlabs-test/audio/test-cta-001.mp3",
          "subtitle": "今すぐ試してみよう！"
        }
      ]
    }
  }
}
```

### Step 3: Generate RenderScriptノードの修正

**重要**: RenderScript生成ロジックを統合データ構造に対応させる必要があります。

「Generate RenderScript」Code Nodeの入力アクセスを以下のように変更:

```javascript
// 修正前（個別Phase参照）
const phase1Data = $input.first().json.TaskID;
const phase2Data = $input.all()[1].json.Assets;
const phase3Data = $input.all()[2].json.Audio.segments;

// 修正後（統合データ構造参照）
const phase1Data = $input.first().json.Phase1;
const phase2Data = $input.first().json.Phase2;
const phase3Data = $input.first().json.Phase3;

// 以降の処理は同じ
const segments = phase1Data.Script.segments;
const assets = phase2Data.Assets;
const audioSegments = phase3Data.Audio.segments;
```

---

## ▶️ 実行手順

### Step 1: ワークフロー実行の開始

1. Manual Triggerノードを選択
2. 右パネル上部の「Execute Node」ボタンをクリック
3. ワークフロー実行が開始される

### Step 2: 実行状況の監視

#### UI上での確認
- 各ノードが緑色（成功）またはオレンジ色（実行中）になる
- 赤色（エラー）の場合は即座に停止して原因調査

#### ノード実行順序
1. ✅ Manual Trigger
2. 🔄 Generate RenderScript
3. 🔄 Call Creatomate API
4. 🔄 Init Polling Counter
5. 🔄 Wait 5 Seconds（ループ開始）
6. 🔄 Check Render Status
7. 🔄 Increment Counter
8. 🔄 Check If Succeeded（条件分岐）
   - **TRUE**: Extract Video URL → Update Notion Hub → END
   - **FALSE**: Check If Continue Polling（条件分岐2）
     - **TRUE**: Wait 5 Secondsに戻る（ループ継続）
     - **FALSE**: END（タイムアウトまたは失敗）

### Step 3: 実行完了の確認

#### 成功パターン
- Extract Video URLノードが緑色（実行成功）
- Update Notion Hubノードが緑色（実行成功）
- 実行時間: 約3〜10分（Creatomate動画生成時間による）

#### タイムアウトパターン
- Check If Continue Pollingの「FALSE」パスが実行される
- ポーリング回数が60回を超えた場合
- 実行時間: 約5分（60回×5秒 = 300秒）

---

## ✅ 検証ポイント（10ノード分）

### 1. Manual Trigger
**検証項目**:
- ✅ ピン留めされたモックデータが正しく出力される
- ✅ Phase1/2/3のデータがすべて含まれている

**期待される出力**:
```json
{
  "Phase1": { ... },
  "Phase2": { ... },
  "Phase3": { ... }
}
```

---

### 2. Generate RenderScript (Code Node)

**検証項目**:
- ✅ 7セグメント×3要素 = 21要素が正しく生成される
- ✅ assetTagマッピングが正確に動作する
- ✅ 時間整合性（currentTime計算）が正確
- ✅ Creatomate Template IDが正しい
- ✅ output_format、width、height、durationが正確

**期待される出力構造**:
```json
{
  "renderScript": {
    "template_id": "40ff626c-9e09-4769-b8b9-66e859ecafa9",
    "modifications": {
      "output_format": "mp4",
      "width": 1080,
      "height": 1920,
      "duration": 80,
      "elements": [
        // 21要素（7セグメント×3要素）
      ]
    }
  },
  "metadata": {
    "totalSegments": 7,
    "totalDuration": 80,
    "totalElements": 21,
    "generatedAt": "2025-11-16T..."
  }
}
```

**詳細検証**:

#### セグメント1（hook、0〜3秒）
```json
// 画像要素
{
  "type": "image",
  "source": "https://images.pexels.com/photos/7193859/...",
  "track": 1,
  "time": 0,
  "duration": 3,
  "animations": [...]
}

// テキスト要素
{
  "type": "text",
  "text": "これが未来の動画制作",
  "font_family": "Noto Sans JP",
  "font_size": "60 px",
  "color": "#FFFFFF",
  "y": "50%",
  "x": "50%",
  "track": 2,
  "time": 0,
  "duration": 3
}

// 音声要素
{
  "type": "audio",
  "source": "https://storage.googleapis.com/elevenlabs-test/audio/test-hook-001.mp3",
  "track": 3,
  "time": 0,
  "duration": 3
}
```

#### 時間計算の確認
- セグメント1（hook）: time=0, duration=3 → 0〜3秒
- セグメント2（intro）: time=3, duration=10 → 3〜13秒
- セグメント3（point1）: time=13, duration=13 → 13〜26秒
- セグメント4（point2）: time=26, duration=13 → 26〜39秒
- セグメント5（point3）: time=39, duration=14 → 39〜53秒
- セグメント6（summary）: time=53, duration=20 → 53〜73秒
- セグメント7（cta）: time=73, duration=7 → 73〜80秒

**合計時間**: 80秒（3+10+13+13+14+20+7）

---

### 3. Call Creatomate API (HTTP Request Node)

**検証項目**:
- ✅ HTTP POST /v1/renders が正常に実行される
- ✅ Bearer認証ヘッダーが正しく送信される
- ✅ RenderScript JSONが正しくリクエストボディに設定される
- ✅ レスポンスにrender IDが含まれる

**期待されるHTTPリクエスト**:
```http
POST https://api.creatomate.com/v1/renders
Authorization: Bearer ed4e53b1e12240b7b8cc010b71a7bb0f8c25b81e73d14b7a837b4fc6d5da5d30
Content-Type: application/json

{
  "template_id": "40ff626c-9e09-4769-b8b9-66e859ecafa9",
  "modifications": { ... }
}
```

**期待されるレスポンス**:
```json
{
  "id": "abc123def456ghi789",
  "status": "rendering",
  "created_at": "2025-11-16T09:30:00Z",
  "template_id": "40ff626c-9e09-4769-b8b9-66e859ecafa9"
}
```

**エラーパターン**:
- ステータスコード 401: API KEY不正
- ステータスコード 400: リクエストボディ不正
- ステータスコード 404: Template ID不正

---

### 4. Init Polling Counter (Code Node)

**検証項目**:
- ✅ render IDが正しく抽出される
- ✅ pollCounter=0で初期化される
- ✅ maxPolls=60が設定される

**期待される出力**:
```json
{
  "renderId": "abc123def456ghi789",
  "pollCounter": 0,
  "maxPolls": 60,
  "status": "rendering"
}
```

---

### 5. Wait 5 Seconds (Wait Node)

**検証項目**:
- ✅ 5秒間正確に待機する
- ✅ webhook ID `poll-wait-webhook` が正しく設定されている

**注意点**:
- ループ中は複数回実行される（最大60回）
- 各実行で5秒間待機

---

### 6. Check Render Status (HTTP Request Node)

**検証項目**:
- ✅ HTTP GET /v1/renders/{renderId} が正常に実行される
- ✅ Bearer認証ヘッダーが正しく送信される
- ✅ render IDが正しくURLに含まれる
- ✅ レスポンスにstatusフィールドが含まれる

**期待されるHTTPリクエスト**:
```http
GET https://api.creatomate.com/v1/renders/abc123def456ghi789
Authorization: Bearer ed4e53b1e12240b7b8cc010b71a7bb0f8c25b81e73d14b7a837b4fc6d5da5d30
```

**期待されるレスポンス（レンダリング中）**:
```json
{
  "id": "abc123def456ghi789",
  "status": "rendering",
  "progress": 45,
  "created_at": "2025-11-16T09:30:00Z"
}
```

**期待されるレスポンス（成功時）**:
```json
{
  "id": "abc123def456ghi789",
  "status": "succeeded",
  "progress": 100,
  "url": "https://f002.backblazeb2.com/file/creatomate-renders/abc123/video.mp4",
  "snapshot_url": "https://f002.backblazeb2.com/file/creatomate-renders/abc123/snapshot.jpg",
  "created_at": "2025-11-16T09:30:00Z",
  "completed_at": "2025-11-16T09:35:00Z"
}
```

---

### 7. Increment Counter (Code Node)

**検証項目**:
- ✅ pollCounterが正しくインクリメントされる
- ✅ statusが保持される
- ✅ 動画URLが成功時に保持される

**期待される出力（レンダリング中）**:
```json
{
  "renderId": "abc123def456ghi789",
  "pollCounter": 1,
  "maxPolls": 60,
  "status": "rendering",
  "progress": 45
}
```

**期待される出力（成功時）**:
```json
{
  "renderId": "abc123def456ghi789",
  "pollCounter": 15,
  "maxPolls": 60,
  "status": "succeeded",
  "url": "https://f002.backblazeb2.com/file/creatomate-renders/abc123/video.mp4",
  "snapshot_url": "https://f002.backblazeb2.com/file/creatomate-renders/abc123/snapshot.jpg"
}
```

---

### 8. Check If Succeeded (IF Node)

**検証項目**:
- ✅ 条件式 `status === "succeeded"` が正しく評価される
- ✅ TRUE時にExtract Video URLパスに進む
- ✅ FALSE時にCheck If Continue Pollingパスに進む

**条件設定**:
```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.status }}",
        "operation": "equals",
        "value2": "succeeded"
      }
    ]
  }
}
```

---

### 9. Check If Continue Polling (IF Node)

**検証項目**:
- ✅ 条件式 `pollCounter <= maxPolls AND status === "rendering"` が正しく評価される
- ✅ TRUE時にWait 5 Secondsに戻る（ループ継続）
- ✅ FALSE時にENDパスに進む（タイムアウトまたは失敗）

**条件設定**:
```json
{
  "conditions": {
    "boolean": [
      {
        "value1": "={{ $json.pollCounter <= $json.maxPolls }}",
        "value2": true
      },
      {
        "value1": "={{ $json.status === 'rendering' }}",
        "value2": true
      }
    ],
    "combineOperation": "all"
  }
}
```

**タイムアウトパターン**:
- pollCounter > 60（60回×5秒 = 300秒 = 5分）
- status !== "rendering"（失敗またはキャンセル）

---

### 10. Extract Video URL (Code Node)

**検証項目**:
- ✅ 動画URLが正しく抽出される
- ✅ Phase1からTaskID、Titleが正しく取得される
- ✅ Notion更新用のデータが正しく準備される

**期待される出力**:
```json
{
  "videoUrl": "https://f002.backblazeb2.com/file/creatomate-renders/abc123/video.mp4",
  "taskId": "1234567890abcdef12345678",
  "title": "【テスト】SNS動画自動生成フロー検証",
  "status": "Phase4完了",
  "completedAt": "2025-11-16T09:35:00+09:00"
}
```

---

### 11. Update Notion Hub (Notion Node)

**⚠️ 注意**: このノードは本番環境のNotion Hubデータベースを更新します。単体テスト時は **実行をスキップ** するか、テスト用データベースを使用してください。

**検証項目**（テスト用データベース使用時のみ）:
- ✅ Notion credentialsが正しく設定されている
- ✅ resource: `databasePage`, operation: `update`
- ✅ 3つのプロパティが正しく更新される

**更新プロパティ**:
```json
{
  "VideoURL": "https://f002.backblazeb2.com/file/creatomate-renders/abc123/video.mp4",
  "Status": "Phase4完了",
  "CompletedAt": "2025-11-16T09:35:00+09:00"
}
```

**単体テスト時の推奨対応**:
1. **オプション1**: Update Notion Hubノードを無効化（Disable Node）
2. **オプション2**: テスト用Notionデータベースを作成して使用
3. **オプション3**: Notion Node設定を確認するだけで実行しない

---

## 📊 期待される全体フロー

### 正常系（Happy Path）の実行フロー

```
Manual Trigger（モックデータ読み込み）
    ↓
Generate RenderScript（21要素生成、約1秒）
    ↓
Call Creatomate API（POST /v1/renders、約1秒）
    ↓
Init Polling Counter（カウンター初期化、<1秒）
    ↓
┌───Wait 5 Seconds（5秒待機）←──────────────┐
│   ↓                                        │
│ Check Render Status（GET /v1/renders/{id}、約1秒）
│   ↓                                        │
│ Increment Counter（カウンター+1、<1秒）   │
│   ↓                                        │
│ Check If Succeeded                         │
│   ├─[status === "succeeded"]               │
│   │    ↓                                   │
│   │  Extract Video URL（URL抽出、<1秒）   │
│   │    ↓                                   │
│   │  Update Notion Hub（Notion更新、約2秒）
│   │    ↓                                   │
│   │   END（成功）                          │
│   │                                        │
│   └─[status !== "succeeded"]               │
│         ↓                                  │
│       Check If Continue Polling            │
│         ├─[counter <= 60 AND status === "rendering"]
│         │                                  │
│         └─────────────────────────────────┘ (ループ継続)
│         │
│         └─[counter > 60 OR status !== "rendering"]
│               ↓
│              END（タイムアウトまたは失敗）
```

### 所要時間の見積もり

**最短パターン**（1回目のポーリングで成功）:
- RenderScript生成: 1秒
- API呼び出し: 1秒
- ポーリング初期化: <1秒
- 待機: 5秒
- ステータス確認: 1秒
- カウンター更新: <1秒
- URL抽出: <1秒
- Notion更新: 2秒
- **合計**: 約11秒

**標準パターン**（15回のポーリングで成功）:
- 初期処理: 3秒
- ポーリングループ: (5秒待機 + 2秒処理) × 15回 = 105秒
- 後処理: 3秒
- **合計**: 約111秒（約2分）

**タイムアウトパターン**（60回のポーリング）:
- 初期処理: 3秒
- ポーリングループ: (5秒待機 + 2秒処理) × 60回 = 420秒
- **合計**: 約423秒（約7分）

---

## 🐛 トラブルシューティング

### エラーパターン1: Generate RenderScriptでエラー

**症状**:
- Code Nodeが赤色（エラー）
- エラーメッセージ: `Cannot read property 'segments' of undefined`

**原因**:
- Phase1データの構造が期待と異なる
- Manual Triggerのピン留めデータが正しくない

**対処法**:
1. Manual Triggerノードの出力データを確認
2. `Phase1.Script.segments` の存在を確認
3. モックデータのJSONが正しくピン留めされているか確認

---

### エラーパターン2: Call Creatomate APIで401エラー

**症状**:
- HTTP Request Nodeが赤色（エラー）
- レスポンス: `401 Unauthorized`

**原因**:
- Creatomate API KEYが不正または期限切れ

**対処法**:
1. HTTP Request Nodeの認証設定を確認
2. Bearer TokenにAPI KEYが正しく設定されているか確認
3. Creatomate Dashboardで新しいAPI KEYを発行

---

### エラーパターン3: Call Creatomate APIで400エラー

**症状**:
- HTTP Request Nodeが赤色（エラー）
- レスポンス: `400 Bad Request`
- エラーメッセージ: `Invalid template_id` または `Invalid modifications`

**原因**:
- Template IDが不正
- RenderScript JSONの構造が不正

**対処法**:
1. Generate RenderScriptノードの出力を確認
2. `template_id` が正しいか確認（`40ff626c-9e09-4769-b8b9-66e859ecafa9`）
3. RenderScript JSONをCreatomate Playgroundで検証

---

### エラーパターン4: ポーリングループが無限ループ

**症状**:
- Wait 5 Secondsノードが60回以上実行される
- Check If Continue Pollingの条件が常にTRUE

**原因**:
- maxPolls設定が不正
- pollCounterがインクリメントされていない

**対処法**:
1. Increment Counterノードの出力を確認
2. `pollCounter` が正しくインクリメントされているか確認
3. Check If Continue Pollingの条件式を確認

---

### エラーパターン5: Update Notion Hubで403エラー

**症状**:
- Notion Nodeが赤色（エラー）
- レスポンス: `403 Forbidden`

**原因**:
- Notion credentialsが不正
- Hubデータベースへのアクセス権限がない

**対処法**:
1. Notion credentialsを再設定
2. Hubデータベースのアクセス権限を確認
3. **単体テスト時**: Notion Nodeを無効化して実行

---

### エラーパターン6: assetTagマッピングエラー

**症状**:
- RenderScript生成時に一部の要素が欠落
- エラーメッセージ: `Asset not found for tag: test-xxx-001`

**原因**:
- Phase2またはPhase3のassetTagが一致しない
- モックデータのassetTagが不整合

**対処法**:
1. 3つのモックデータファイル（phase1/2/3-mock-output.json）でassetTagを確認
2. すべてのファイルで以下の7つのassetTagが存在するか確認:
   - test-hook-001
   - test-intro-001
   - test-point1-001
   - test-point2-001
   - test-point3-001
   - test-summary-001
   - test-cta-001

---

## 📝 テスト結果記録フォーマット

### テスト実行報告書

```markdown
# WF7 Phase4 単体テスト実行報告書

**実行日時**: YYYY-MM-DD HH:MM:SS JST
**実行者**: [名前]
**n8nインスタンス**: Railway n8n-python
**ワークフローID**: [ワークフローID]

## テスト結果サマリー

| 項目 | 結果 |
|------|------|
| 総実行時間 | XX分XX秒 |
| ノード実行数 | 10ノード |
| 成功ノード数 | X / 10 |
| エラーノード数 | X / 10 |
| ポーリング回数 | XX回 |
| 最終ステータス | ✅ 成功 / ❌ 失敗 |

## ノード別検証結果

### 1. Manual Trigger
- **ステータス**: ✅ 成功 / ❌ 失敗
- **検証項目**: モックデータ読み込み
- **備考**: [メモ]

### 2. Generate RenderScript
- **ステータス**: ✅ 成功 / ❌ 失敗
- **検証項目**: 21要素生成、assetTagマッピング
- **生成要素数**: XX / 21
- **合計時間**: XX秒 / 80秒
- **備考**: [メモ]

### 3. Call Creatomate API
- **ステータス**: ✅ 成功 / ❌ 失敗
- **検証項目**: POST /v1/renders
- **HTTPステータスコード**: XXX
- **render ID**: [render ID]
- **備考**: [メモ]

### 4. Init Polling Counter
- **ステータス**: ✅ 成功 / ❌ 失敗
- **検証項目**: カウンター初期化
- **pollCounter**: 0
- **maxPolls**: 60
- **備考**: [メモ]

### 5-9. ポーリングループ（5ノード）
- **ステータス**: ✅ 成功 / ❌ 失敗
- **ポーリング回数**: XX回
- **最終status**: [succeeded/rendering/failed]
- **備考**: [メモ]

### 10. Extract Video URL
- **ステータス**: ✅ 成功 / ❌ 失敗 / ⏭️ スキップ
- **動画URL**: [動画URL]
- **TaskID**: [TaskID]
- **備考**: [メモ]

### 11. Update Notion Hub
- **ステータス**: ✅ 成功 / ❌ 失敗 / ⏭️ スキップ
- **更新対象ページ**: [ページID]
- **更新プロパティ**: VideoURL, Status, CompletedAt
- **備考**: [メモ]

## エラー詳細

[エラーが発生した場合のみ記録]

- **ノード名**: [ノード名]
- **エラーメッセージ**: [エラーメッセージ]
- **原因**: [原因]
- **対処法**: [対処法]

## 検証合格基準

- ✅ RenderScript生成: 21要素すべて生成
- ✅ Creatomate API呼び出し: HTTPステータスコード 200
- ✅ ポーリングループ: 最大60回以内で成功
- ✅ 動画URL抽出: 有効なBackblaze B2 URLを取得
- ⏭️ Notion更新: スキップ（単体テストのため）

## 総合判定

- ✅ **合格**: すべての検証項目をクリア
- ❌ **不合格**: 1つ以上の検証項目で失敗

## 次のステップ

[合格時]
- フェーズ2: Phase1/2/3との接続テストに進む

[不合格時]
- エラー原因の調査と修正
- 再テスト実施
```

---

## 🎯 次のステップ

### 単体テスト成功後

1. **フェーズ2**: Phase1/2/3との接続テスト
   - Phase1/2/3ワークフローの実行
   - 実際の出力データでPhase4を実行
   - データ整合性の検証

2. **フェーズ3**: エンドツーエンドテスト
   - Notion Hubからトリガー
   - Phase1→2→3→4の完全フロー実行
   - 最終動画の品質確認

3. **フェーズ4**: エラーハンドリングテスト
   - 異常系シナリオの実行
   - エラーリカバリーの確認

4. **フェーズ5**: パフォーマンステスト
   - 複数動画の同時生成
   - リソース使用量の監視

5. **フェーズ6**: 本番デプロイ
   - 本番環境への移行
   - 監視体制の構築

---

## 📚 参考資料

- **Phase4実装計画**: `2025-11-16_08-59_wf7-phase4-integration-plan.md`
- **Phase4完成検証**: `2025-11-16_09-11_wf7-phase4-完成検証.md`
- **統合テスト計画**: `2025-11-16_09-15_wf7-phase123-integration-test-plan.md`
- **RenderScriptロジック**: `2025-11-16_03-19_wf7-phase4-renderscript.js`
- **Phase4ワークフローJSON**: `2025-11-16_08-59_wf7-phase4-creatomate-integration.json`

---

**ドキュメント終了**
