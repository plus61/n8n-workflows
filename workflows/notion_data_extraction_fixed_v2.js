const notionPage = $input.first().json;
const props = notionPage.properties;

// rich_textから直接取得を試す（既存の方法）
const scriptJson = props['Script JSON']?.rich_text?.[0]?.text?.content;
if (scriptJson) {
  // rich_textから直接取得できる場合
  const assetsJson = props['Assets JSON']?.rich_text?.[0]?.plain_text || props['Assets JSON']?.rich_text?.[0]?.text?.content;
  if (!assetsJson) {
    throw new Error('Assets JSON not found in Notion page');
  }
  
  // 既存のパース処理
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
  
  const articleId = props['Article ID']?.rich_text?.[0]?.text?.content || notionPage.id;
  
  return {
    json: {
      notionPageId: notionPage.id,
      articleId,
      scriptData: JSON.parse(scriptJson),
      assetsData: assetsArray
    }
  };
}

// URL型プロパティから取得を試す（フォールバック）
const scriptJsonUrl = props['Script JSON']?.url;
if (!scriptJsonUrl) {
  throw new Error('Script JSON not found in Notion page (neither rich_text nor url)');
}

const assetsJsonUrl = props['Assets JSON']?.url;
if (!assetsJsonUrl) {
  throw new Error('Assets JSON URL not found in Notion page properties');
}

// URLからJSONデータを取得（$helpers.httpRequest()を使用 - fetchの代わり）
try {
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
  
  const scriptJsonText = scriptResponse;
  const assetsJsonText = assetsResponse;
  
  // 既存のパース処理（assetsJsonから driveFileId と assetTag を抽出）
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
  
  // Article IDもURL型プロパティの可能性があるため、rich_textとurlの両方を試す
  const articleId = props['Article ID']?.rich_text?.[0]?.text?.content
    || props['Article ID']?.url
    || notionPage.id;
  
  return {
    json: {
      notionPageId: notionPage.id,
      articleId,
      scriptData: JSON.parse(scriptJsonText),
      assetsData: assetsArray
    }
  };
} catch (error) {
  throw new Error(`Failed to fetch JSON from URLs: ${error.message}`);
}





