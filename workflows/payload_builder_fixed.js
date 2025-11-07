// FAL APIが期待する形式に変換
const scriptData = $('Notionデータ抽出').item.json.scriptData;
const metadataItems = $input.all();
const articleId = $('Notionデータ抽出').item.json.articleId;

// スクリプトのセグメントからdurationを取得
const segments = scriptData.segments || [];
let currentTimestamp = 0;

// 各アセットからkeyframesを構築
const keyframes = metadataItems.map((metaItem, idx) => {
  const segment = segments[idx] || { duration: 10 };
  const duration = segment.duration || 10;

  // Google Drive URLを直接使用（data URLではなく）
  const driveFileId = metaItem.json.driveFileId;
  const imageUrl = `https://drive.google.com/uc?export=download&id=${driveFileId}`;

  const keyframe = {
    url: imageUrl,
    timestamp: currentTimestamp,
    duration: duration
  };

  currentTimestamp += duration;
  return keyframe;
});

// FAL APIが期待するJSON構造を構築
const videoJson = {
  tracks: [
    {
      id: "1",
      type: "video",
      keyframes: keyframes
    }
  ]
};

// JSON文字列として返す
return {
  json: {
    json_string: JSON.stringify(videoJson),
    articleId: articleId
  }
};
