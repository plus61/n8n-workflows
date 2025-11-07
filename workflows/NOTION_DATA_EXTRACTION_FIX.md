# Notionデータ抽出ノード 修正手順

## 問題
現在の「Notionデータ抽出」ノードは `rich_text` プロパティからデータを取得しようとしていますが、実際のNotionページでは "Script JSON" と "Assets JSON" は **URL型プロパティ** です。

## エラー
```
Script JSON not found in Notion page [line 6]
```

## 修正手順

### 1. n8n UIでワークフロー SDO8X6oR5W5y2s6A を開く

### 2. 「Notionデータ抽出」ノード（ID: 51161ca9-f078-4fee-a2e4-795ee6588bc8）をクリック

### 3. JavaScriptコードを以下に置き換え

```javascript
const notionPage = $input.first().json;
const props = notionPage.properties;

// URL型プロパティから直接取得（rich_textではなくurl）
const scriptJsonUrl = props['Script JSON']?.url;
if (!scriptJsonUrl) {
  throw new Error('Script JSON URL not found in Notion page properties');
}

const assetsJsonUrl = props['Assets JSON']?.url;
if (!assetsJsonUrl) {
  throw new Error('Assets JSON URL not found in Notion page properties');
}

// URLからJSONデータを取得（$helpers.httpRequest()を使用）
const scriptResponse = await $helpers.httpRequest({
  method: 'GET',
  url: scriptJsonUrl,
  json: false  // テキストとして取得
});

const assetsResponse = await $helpers.httpRequest({
  method: 'GET',
  url: assetsJsonUrl,
  json: false  // テキストとして取得
});

const scriptJson = scriptResponse;
const assetsJson = assetsResponse;

// 既存のパース処理（assetsJsonから driveFileId と assetTag を抽出）
const driveFileIdRegex = /"driveFileId":\s*"([^"]+)"/g;
const driveFileIds = [];
let match;
while ((match = driveFileIdRegex.exec(assetsJson)) !== null) {
  driveFileIds.push(match[1]);
}

const assetTagRegex = /"assetTag":\s*"([^"]+)"/g;
const assetTags = [];
while ((match = assetTagRegex.exec(assetsJson)) !== null) {
  assetTags.push(match[1]);
}

const assetsArray = driveFileIds.map((id, idx) => ({
  driveFileId: id,
  assetTag: assetTags[idx] || `asset${idx}`,
  assetIndex: idx
}));

// Article IDもURL型プロパティの可能性があるため、rich_textとurlの両方を試す
const articleId = props['Article ID']?.rich_text?.[0]?.text?.content
  || props['Article ID']?.url
  || notionPage.id;

return {
  json: {
    notionPageId: notionPage.id,
    articleId,
    scriptData: JSON.parse(scriptJson),
    assetsData: assetsArray
  }
};
```

### 4. 保存してテスト実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "2a368d5c29868185a10ece6a9fedcdd4"}'
```

## 主な変更点

| 修正前 | 修正後 |
|--------|--------|
| `props['Script JSON']?.rich_text?.[0]?.text?.content` | `props['Script JSON']?.url` |
| `props['Assets JSON']?.rich_text?.[0]?.plain_text` | `props['Assets JSON']?.url` |
| データを直接使用 | `$helpers.httpRequest()` でURL先のデータを取得 |
| `fetch()` 使用不可 | `$helpers.httpRequest()` を使用（n8n推奨） |

## テスト用Notion ページ

- **Page ID**: `2a368d5c29868185a10ece6a9fedcdd4`
- **Title**: WF7 Phase4 Webhook Test
- **Script JSON**: https://raw.githubusercontent.com/test/sample-script.json
- **Assets JSON**: https://raw.githubusercontent.com/test/sample-assets.json
- **Article ID**: test-article-001
- **Status**: ScriptReady

## 期待される動作

1. Notion APIからページデータを取得 ✅
2. URL型プロパティから Script JSON と Assets JSON のURLを抽出 → 修正が必要
3. URLからJSONデータを取得
4. assetsArrayとscriptDataを構築
5. Split Outノードで各アセットを分割
6. 後続処理へ継続
