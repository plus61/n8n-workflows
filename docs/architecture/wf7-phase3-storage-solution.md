# WF7 Phase3: ファイルストレージ完全解決策

**作成日**: 2025-10-31
**問題**: Railway n8n環境でのファイルストレージ制約

---

## 🚨 現在の制約条件

### 利用不可能なサービス

1. **Google Drive/Sheets**
   - **理由**: Railway環境でのGoogle OAuth認証問題
   - **影響**: Phase1で使用していたDriveアップロードが使用不可

2. **Cloudflare R2**
   - **理由**: Cloudflare環境設定問題
   - **影響**: 低コスト・高速ストレージが使用不可

3. **Notion API**
   - **理由**: ファイルアップロード非対応（URLプロパティのみ）
   - **影響**: 音声・字幕ファイルの直接保存不可

---

## 💡 完全解決策の提案

### Option 1: Railway Volume + 静的ファイル配信 ⭐ **推奨**

**アーキテクチャ**:
```
VOICEVOX音声合成 (バイナリ生成)
  ↓
Railway Persistent Volume に保存
  ↓
n8n内蔵HTTP Server経由で配信
  ↓
公開URL生成 (https://n8n-instance.railway.app/files/voice_xxx.wav)
  ↓
NotionにURLを保存
```

**実装方法**:

#### 1. Railway Volume設定
```yaml
# railway.toml
[volumes]
  [volumes.n8n_files]
    mount_path = "/data/files"
    size = 10  # GB
```

#### 2. n8n Code Node: ファイル保存
```javascript
// 音声メタデータ保存ノード
const fs = require('fs');
const path = require('path');

const articleId = $('ナレーション抽出').first().json.articleId;
const notionPageId = $('ナレーション抽出').first().json.notionPageId;

// バイナリデータを取得
const binaryData = $binary.data;

// ファイルパス
const filesDir = '/data/files/audio';
const fileName = `voice_${articleId}.wav`;
const filePath = path.join(filesDir, fileName);

// ディレクトリ作成（存在しない場合）
if (!fs.existsSync(filesDir)) {
  fs.mkdirSync(filesDir, { recursive: true });
}

// ファイル保存
fs.writeFileSync(filePath, binaryData);

// 公開URL生成
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';
const voiceFileUrl = `${baseUrl}/files/audio/${fileName}`;

return {
  json: {
    articleId,
    notionPageId,
    voiceFileUrl
  }
};
```

#### 3. n8n静的ファイル配信設定
```bash
# Railway環境変数
N8N_STATIC_FILES_PATH=/data/files
N8N_STATIC_FILES_BASE_URL=/files
```

**メリット**:
- ✅ 追加コストなし（Railwayボリューム料金のみ）
- ✅ 認証不要（n8n内で完結）
- ✅ 低レイテンシー（同一サーバー）
- ✅ 実装がシンプル

**デメリット**:
- ❌ スケーラビリティ制限（単一インスタンス）
- ❌ CDN非対応（グローバル配信不可）

---

### Option 2: Vercel Blob Storage

**アーキテクチャ**:
```
VOICEVOX音声合成
  ↓
Vercel Blob API でアップロード
  ↓
公開URL取得
  ↓
NotionにURLを保存
```

**実装方法**:

#### 1. Vercel Blob認証設定
```bash
# Railway環境変数
BLOB_READ_WRITE_TOKEN=vercel_blob_xxxxx
```

#### 2. n8n HTTP Request Node: アップロード
```javascript
// ペイロード作成ノード
const articleId = $('ナレーション抽出').first().json.articleId;
const binaryData = $binary.data;

return {
  json: {
    articleId,
    pathname: `audio/voice_${articleId}.wav`,
    contentType: 'audio/wav',
    binaryData: binaryData.toString('base64')
  }
};
```

```javascript
// HTTP Request Node
{
  "method": "PUT",
  "url": "=https://blob.vercel-storage.com/{{ $json.pathname }}",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "={{ 'Bearer ' + $env.BLOB_READ_WRITE_TOKEN }}"
      },
      {
        "name": "x-content-type",
        "value": "={{ $json.contentType }}"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "file",
        "value": "={{ $json.binaryData }}"
      }
    ]
  },
  "options": {
    "timeout": 30000,
    "retry": {
      "enabled": true,
      "maxTries": 3,
      "waitBetween": 2000
    }
  }
}
```

**メリット**:
- ✅ Vercelアカウントで利用可能
- ✅ CDN配信（グローバル高速化）
- ✅ スケーラブル
- ✅ 無料枠あり（1GB/月）

**デメリット**:
- ❌ 追加サービス依存
- ❌ 無料枠超過時のコスト

---

### Option 3: AWS S3 + IAM認証

**前提**: AWSアカウントが利用可能な場合

**実装方法**:
```javascript
// HTTP Request Node (S3 PUT)
{
  "method": "PUT",
  "url": "=https://your-bucket.s3.amazonaws.com/audio/voice_{{ $('ナレーション抽出').first().json.articleId }}.wav",
  "authentication": "genericCredentialType",
  "genericAuthType": "awsCredential",
  "sendBody": true,
  "body": "={{ $binary.data }}",
  "options": {
    "timeout": 30000,
    "retry": {
      "enabled": true,
      "maxTries": 3,
      "waitBetween": 2000
    }
  }
}
```

**メリット**:
- ✅ 業界標準
- ✅ 高い信頼性
- ✅ 豊富な機能

**デメリット**:
- ❌ AWS認証設定が複雑
- ❌ コスト（最低$0.023/GB/月）

---

## 🎯 推奨実装: Option 1 (Railway Volume)

### 理由

1. **既存環境で完結**: Railway + n8nのみで実装可能
2. **認証不要**: 追加のAPI認証設定が不要
3. **実装が簡単**: Code Nodeとfs操作のみ
4. **コスト効率**: ボリューム料金のみ（~$0.25/GB/月）

### 実装手順

#### Step 1: Railway Volume追加
```bash
# Railway Dashboard
Project → Settings → Volumes
  Name: n8n-files
  Mount Path: /data/files
  Size: 10GB
```

#### Step 2: n8n環境変数設定
```bash
N8N_STATIC_FILES_PATH=/data/files
N8N_STATIC_FILES_BASE_URL=/files
N8N_HOST=https://n8n-python-production-344b.up.railway.app
```

#### Step 3: Phase3ノード更新

**「音声メタデータ保存」ノード**:
```javascript
const fs = require('fs');
const path = require('path');

const articleId = $('ナレーション抽出').first().json.articleId;
const notionPageId = $('ナレーション抽出').first().json.notionPageId;

// バイナリデータ取得
const binaryData = $input.first().binary.data;

// ファイル保存
const filesDir = '/data/files/audio';
const fileName = `voice_${articleId}.wav`;
const filePath = path.join(filesDir, fileName);

// ディレクトリ作成
if (!fs.existsSync(filesDir)) {
  fs.mkdirSync(filesDir, { recursive: true });
}

// ファイル書き込み
fs.writeFileSync(filePath, Buffer.from(binaryData, 'base64'));

// 公開URL
const baseUrl = $env.N8N_HOST;
const voiceFileUrl = `${baseUrl}/files/audio/${fileName}`;

return {
  json: {
    articleId,
    notionPageId,
    voiceFileUrl
  }
};
```

**「字幕メタデータ保存」ノード**:
```javascript
const fs = require('fs');
const path = require('path');

const prevData = $input.first().json;
const srtContent = prevData.srtContent;
const articleId = prevData.articleId;

// ファイル保存
const filesDir = '/data/files/subtitles';
const fileName = `subtitle_${articleId}.srt`;
const filePath = path.join(filesDir, fileName);

if (!fs.existsSync(filesDir)) {
  fs.mkdirSync(filesDir, { recursive: true });
}

fs.writeFileSync(filePath, srtContent, 'utf8');

// 公開URL
const baseUrl = $env.N8N_HOST;
const subtitleFileUrl = `${baseUrl}/files/subtitles/${fileName}`;

return {
  json: {
    ...prevData,
    subtitleFileUrl
  }
};
```

#### Step 4: n8n再起動
```bash
railway up
```

---

## 🧪 テスト計画

### テストケース1: ファイル保存確認
```bash
# Railway Shell
railway shell

# ファイル確認
ls -lah /data/files/audio/
ls -lah /data/files/subtitles/
```

### テストケース2: URL配信確認
```bash
curl https://n8n-python-production-344b.up.railway.app/files/audio/voice_test-article-001.wav
```

### テストケース3: Notion統合確認
- Notion DBでVoice File URLをクリック
- ブラウザで音声再生確認

---

## 📊 代替案比較

| 項目 | Railway Volume | Vercel Blob | AWS S3 | Google Drive |
|-----|---------------|-------------|--------|-------------|
| 初期設定 | 簡単 ⭐ | 中程度 | 複雑 | **不可能** |
| 追加認証 | 不要 ⭐ | 必要 | 必要 | **不可能** |
| コスト/月 | $2.5 (10GB) | $5 (10GB) | $0.23 (10GB) | **不可能** |
| CDN配信 | なし | あり ⭐ | あり | **不可能** |
| スケール性 | 低 | 高 ⭐ | 高 | **不可能** |
| 実装難易度 | 低 ⭐ | 中 | 高 | **不可能** |
| Railway統合 | 完璧 ⭐ | 外部 | 外部 | **不可能** |

---

## ✅ 結論

**Phase3では Railway Volume + 静的ファイル配信を採用**

1. Railway環境に10GB Volumeを追加
2. n8n環境変数で静的ファイル配信を有効化
3. Code Nodeでfs経由でファイル保存
4. 公開URLをNotionに保存

**この方式により**:
- Google Drive認証問題を回避
- Cloudflare設定不要
- 追加コストを最小化（$2.5/月）
- 実装がシンプルで保守しやすい

---

**次のステップ**:
1. Railway Volumeを追加
2. n8n環境変数を設定
3. Phase3ノードを更新
4. E2Eテスト実行

---

**最終更新**: 2025-10-31
**ステータス**: 💡 解決策提案完了
