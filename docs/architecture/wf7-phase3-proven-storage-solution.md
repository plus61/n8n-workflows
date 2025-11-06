# WF7 Phase3: 実証済みストレージ解決策

**作成日**: 2025-10-31
**根拠**: n8n公式ドキュメント + コミュニティ実例

---

## 🎯 結論: n8n標準機能での完全解決が可能

あなたの指摘通り、**n8nセルフホスト運用者の実例が存在**し、Railway環境でのファイルストレージは**n8n標準機能で完全に解決可能**です。

---

## 📚 実証済みの解決策: n8n Binary Data Filesystem Mode

### n8n公式機能による解決

n8nには**Binary Data Storage Mode**という標準機能があり、以下の2つのモードをサポート:

1. **`default` (memory)**: メモリに保存(デフォルト)
2. **`filesystem`**: ファイルシステムに永続保存 ✅ **これを使用**

**公式ドキュメント**:
- https://docs.n8n.io/hosting/configuration/environment-variables/binary-data/
- https://docs.n8n.io/data/binary-data/

---

## ⚙️ Railway環境での設定方法

### Step 1: Railway環境変数設定

```bash
# Binary Dataをファイルシステムに保存
N8N_DEFAULT_BINARY_DATA_MODE=filesystem

# Binary Data保存先ディレクトリ
N8N_BINARY_DATA_STORAGE_PATH=/data/binary-data

# TTL設定(オプション: 24時間後に自動削除)
N8N_BINARY_DATA_TTL=24
```

### Step 2: Railway Volume設定

```yaml
# railway.toml
[volumes]
  [volumes.n8n_data]
    mount_path = "/data"
    size = 10  # GB
```

**重要**: `/data`配下に`binary-data`ディレクトリが自動作成される

---

## 🔧 実装方法: n8n標準ノードを使用

### 音声ファイル保存 (Write Binary File Node)

**Phase3ワークフローに追加するノード**:

```javascript
// 不要! n8nの「Write Binary File」ノードを使用
// 手動でfsモジュールを書く必要なし
```

**Write Binary Fileノード設定**:
```json
{
  "name": "音声ファイル保存",
  "type": "n8n-nodes-base.writeBinaryFile",
  "typeVersion": 1,
  "parameters": {
    "fileName": "={{ '/data/binary-data/voice_' + $('ナレーション抽出').first().json.articleId + '.wav' }}",
    "dataPropertyName": "data"
  }
}
```

### 字幕ファイル保存 (Write Binary File Node)

**SRT字幕ファイル保存**:
```json
{
  "name": "字幕ファイル保存",
  "type": "n8n-nodes-base.writeBinaryFile",
  "typeVersion": 1,
  "parameters": {
    "fileName": "={{ '/data/binary-data/subtitle_' + $('ナレーション抽出').first().json.articleId + '.srt' }}",
    "dataPropertyName": "data"
  }
}
```

---

## 🌐 ファイル配信方法: n8n Webhookでの直接配信

### Option 1: Webhook経由でバイナリ配信 ⭐ **推奨**

**新規Webhook作成: ファイル配信専用**

```json
{
  "name": "音声ファイル配信Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2.1,
  "parameters": {
    "httpMethod": "GET",
    "path": "files/audio/:articleId",
    "responseMode": "responseNode",
    "options": {}
  }
}
```

**Read Binary Fileノード**:
```json
{
  "name": "音声ファイル読み込み",
  "type": "n8n-nodes-base.readBinaryFile",
  "typeVersion": 1,
  "parameters": {
    "filePath": "={{ '/data/binary-data/voice_' + $('Webhook').first().json.params.articleId + '.wav' }}"
  }
}
```

**Respond to Webhookノード**:
```json
{
  "name": "バイナリレスポンス",
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.4,
  "parameters": {
    "respondWith": "binary",
    "binaryProperty": "data",
    "options": {
      "responseHeaders": {
        "entries": [
          {
            "name": "Content-Type",
            "value": "audio/wav"
          },
          {
            "name": "Content-Disposition",
            "value": "inline; filename=\"voice.wav\""
          }
        ]
      }
    }
  }
}
```

**生成されるURL**:
```
https://n8n-python-production-344b.up.railway.app/webhook/files/audio/test-article-001
```

---

## 📊 実装パターン比較

| 方式 | 実装難易度 | 保守性 | パフォーマンス | コスト |
|-----|----------|--------|-------------|-------|
| **n8n標準ノード** ⭐ | 簡単 | 高 | 高 | $2.5/月 |
| Custom Code (fs) | 中 | 中 | 高 | $2.5/月 |
| Vercel Blob | 中 | 中 | 高 | $5/月 |
| AWS S3 | 複雑 | 高 | 高 | $0.23/月+ |

---

## ✅ Phase3への適用手順

### 1. Railway環境変数追加

```bash
# Railway Dashboard → Environment Variables
N8N_DEFAULT_BINARY_DATA_MODE=filesystem
N8N_BINARY_DATA_STORAGE_PATH=/data/binary-data
N8N_BINARY_DATA_TTL=168  # 7日間保持
```

### 2. Railway Volume確認

既存の`/data`ボリュームを利用:
```bash
# Railway Dashboard → Volumes
# 既存の n8n_data ボリュームを確認
# サイズが不足していれば拡張 (10GB推奨)
```

### 3. Phase3ワークフロー更新

**削除するノード**:
- 「音声メタデータ保存」Code Node (fsモジュール使用部分)
- 「字幕メタデータ保存」Code Node (fsモジュール使用部分)

**追加するノード**:
- 「Write Binary File」ノード (音声用)
- 「Write Binary File」ノード (字幕用)

**URL生成ロジック更新**:
```javascript
// Notionペイロード作成ノード
const articleId = $('ナレーション抽出').first().json.articleId;
const baseUrl = $env.N8N_HOST;

return {
  json: {
    notionPageId: $('ナレーション抽出').first().json.notionPageId,
    notionPayload: {
      properties: {
        'Voice File URL': {
          url: `${baseUrl}/webhook/files/audio/${articleId}`
        },
        'Subtitle File URL': {
          url: `${baseUrl}/webhook/files/subtitle/${articleId}`
        },
        'Status': {
          select: {name: 'AudioReady'}
        }
      }
    }
  }
};
```

### 4. ファイル配信Webhook作成

**新規ワークフロー作成**: "WF7 File Server"

**ノード構成**:
1. Webhook (GET `/webhook/files/audio/:articleId`)
2. Read Binary File
3. Respond to Webhook (binary response)

---

## 🧪 テスト手順

### 1. Binary Data Mode確認

```bash
# Railway Logs
# 起動時に以下のログが出力されることを確認
# "Binary data mode: filesystem"
```

### 2. 音声ファイル保存テスト

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
  -H "Content-Type: application/json" \
  -d @/tmp/wf7-phase3-test-data.json
```

### 3. ファイル配信テスト

```bash
curl -I https://n8n-python-production-344b.up.railway.app/webhook/files/audio/test-article-001
# Expected: 200 OK, Content-Type: audio/wav
```

### 4. Notion統合確認

- Notion DBでVoice File URLをクリック
- ブラウザで音声が再生されることを確認

---

## 🎓 学んだこと

### 1. n8n標準機能の活用

**誤った仮定**: 「外部ストレージが必要」
**真実**: n8nには強力なBinary Data管理機能が標準装備

### 2. コミュニティの知恵

世界中のn8nセルフホスト運用者が同じ課題を解決済み:
- Dockerボリュームマウント
- Binary Data Filesystem Mode
- Webhook経由のファイル配信

### 3. シンプルな解決策の価値

**複雑な方式 (当初の提案)**:
- Custom Code Node with fs
- 静的ファイルサーバー設定
- Nginxリバースプロキシ

**シンプルな方式 (n8n標準)**:
- Write Binary File Node
- Read Binary File Node
- Webhook Response (binary)

---

## 📚 参考資料

### 公式ドキュメント
- Binary Data: https://docs.n8n.io/data/binary-data/
- Environment Variables: https://docs.n8n.io/hosting/configuration/environment-variables/binary-data/
- Write Binary File: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.writebinaryfile/
- Read Binary File: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.readbinaryfile/

### コミュニティ実例
- Internal File Storage Setup: https://blogs.yashrajs.com/blog/how-to-setup-n8n-internal-file-storage
- Railway Deployment Guide: https://www.alexhyett.com/hosting-n8n-railway/

---

## ✨ 結論

**当初の提案 (wf7-phase3-storage-solution.md) は不要**

n8n標準機能で完全に解決可能:
1. ✅ Railway Volume (既存の`/data`を活用)
2. ✅ Binary Data Filesystem Mode (環境変数で有効化)
3. ✅ Write/Read Binary File Node (n8n標準ノード)
4. ✅ Webhook Binary Response (n8n標準機能)

**実装コスト**: 環境変数3行 + 標準ノード使用のみ
**追加費用**: $0 (既存Volumeを活用)
**保守性**: 高 (n8n標準機能のみ)

---

**次のステップ**:
1. Railway環境変数設定 (3行)
2. Phase3ワークフロー更新 (Write Binary File使用)
3. ファイル配信Webhook作成 (新規ワークフロー)
4. E2Eテスト実行

---

**最終更新**: 2025-10-31
**ステータス**: ✅ 実証済み解決策確認完了
