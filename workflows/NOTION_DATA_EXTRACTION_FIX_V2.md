# Notionデータ抽出ノード 修正手順 V2

## 問題
- `$helpers.httpRequest()` も n8n Code環境では使用できない
- URL型プロパティから直接JSONデータを取得する必要がある

## 解決策
**アーキテクチャ変更**: 1つのCodeノードを複数のノードに分割

### 新しいフロー構造

```
Notion API呼び出し
    ↓
URL抽出（Code）
    ↓
Script JSON取得（HTTP Request）
    ↓
Assets JSON取得（HTTP Request）
    ↓
データ統合（Code）
    ↓
Split Out
```

---

## 修正手順

### 1. 既存の「Notionデータ抽出」ノードを削除

### 2. 新しいCodeノード「URL抽出」を追加

**位置**: Notion API呼び出し → URL抽出

**コード**:
```javascript
const notionPage = $input.first().json;
const props = notionPage.properties;

// URL型プロパティから直接取得
const scriptJsonUrl = props['Script JSON']?.url;
if (!scriptJsonUrl) {
  throw new Error('Script JSON URL not found in Notion page properties');
}

const assetsJsonUrl = props['Assets JSON']?.url;
if (!assetsJsonUrl) {
  throw new Error('Assets JSON URL not found in Notion page properties');
}

// Article ID取得
const articleId = props['Article ID']?.rich_text?.[0]?.text?.content
  || props['Article ID']?.url
  || notionPage.id;

return {
  json: {
    notionPageId: notionPage.id,
    articleId,
    scriptJsonUrl,
    assetsJsonUrl
  }
};
```

### 3. HTTP Requestノード「Script JSON取得」を追加

**位置**: URL抽出 → Script JSON取得

**設定**:
- **Method**: GET
- **URL**: `={{ $json.scriptJsonUrl }}`
- **Authentication**: None
- **Options** → Response → Response Format: **Text** (JSONではなくText)

### 4. HTTP Requestノード「Assets JSON取得」を追加

**位置**: Script JSON取得 → Assets JSON取得

**設定**:
- **Method**: GET
- **URL**: `={{ $('URL抽出').item.json.assetsJsonUrl }}`
- **Authentication**: None
- **Options** → Response → Response Format: **Text**

### 5. Codeノード「データ統合」を追加

**位置**: Assets JSON取得 → データ統合

**コード**:
```javascript
const urlExtractNode = $('URL抽出').item.json;
const scriptJsonText = $('Script JSON取得').item.json.data;
const assetsJsonText = $json.data;

// assetsJsonから driveFileId と assetTag を抽出
const driveFileIdRegex = /"driveFileId":\s*"([^"]+)"/g;
const driveFileIds = [];
let match;
while ((match = driveFileIdRegex.exec(assetsJsonText)) !== null) {
  driveFileIds.push(match[1]);
}

const assetTagRegex = /"assetTag":\s*"([^"]+)"/g;
const assetTags = [];
while ((match = assetTagRegex.exec(assetsJsonText)) !== null) {
  assetTags.push(match[1]);
}

const assetsArray = driveFileIds.map((id, idx) => ({
  driveFileId: id,
  assetTag: assetTags[idx] || `asset${idx}`,
  assetIndex: idx
}));

return {
  json: {
    notionPageId: urlExtractNode.notionPageId,
    articleId: urlExtractNode.articleId,
    scriptData: JSON.parse(scriptJsonText),
    assetsData: assetsArray
  }
};
```

### 6. 接続を再構築

```
Notion API呼び出し → URL抽出 → Script JSON取得 → Assets JSON取得 → データ統合 → Split Out
```

### 7. 保存してテスト

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "2a368d5c29868185a10ece6a9fedcdd4"}'
```

---

## ノード構成まとめ

| ノード名 | タイプ | 役割 |
|---------|--------|------|
| Notion API呼び出し | HTTP Request | Notion APIからページデータ取得 |
| **URL抽出** | Code | URL型プロパティからURLを抽出 |
| **Script JSON取得** | HTTP Request | Script JSONデータをURL先から取得 |
| **Assets JSON取得** | HTTP Request | Assets JSONデータをURL先から取得 |
| **データ統合** | Code | 取得したデータを統合・パース |
| Split Out | Split Out | assetsDataを個別アイテムに分割 |

---

## 重要なポイント

1. **HTTP RequestのResponse Format**: **Text** を指定（JSONではなく生テキストで取得）
2. **ノード参照**: `$('ノード名').item.json` で他ノードのデータを参照
3. **データフィールド**: HTTP RequestのTextレスポンスは `$json.data` に格納される
4. **URL型プロパティ**: `props['Script JSON']?.url` で直接アクセス

---

## トラブルシューティング

### エラー: "data is not defined"
→ HTTP RequestノードのResponse Formatが **Text** になっているか確認

### エラー: "Cannot read property 'json' of undefined"
→ ノード名が正確に一致しているか確認（全角・半角、スペースに注意）

### エラー: "scriptJsonUrl is not defined"
→ 「URL抽出」ノードが正常に実行されているか確認
