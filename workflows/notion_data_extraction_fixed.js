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





