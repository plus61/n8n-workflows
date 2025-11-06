/**
 * Fetch Hub Context Node for n8n
 *
 * このコードは、MEO Operations HubデータベースからArticle IDを使用して
 * コンテキスト情報を取得するn8n Codeノード用のテンプレートです。
 *
 * 使用方法:
 * 1. n8nワークフローのCodeノードにこのコードを貼り付けます
 * 2. 前段のノードから articleId を受け取る、または手動で設定します
 * 3. Notion APIトークンとHub DB IDを環境変数または直接設定します
 */

// 入力データから articleId を取得
const articleId = $input.first().json.articleId ||
                 $input.first().json.body?.articleId ||
                 $json.articleId;

if (!articleId) {
  throw new Error('Article ID is required to fetch Hub context');
}

// Notion API設定
const NOTION_TOKEN = $env.NOTION_API_TOKEN || process.env.NOTION_API_TOKEN;
const HUB_DB_ID = '2a268d5c-2986-813c-a8e5-eba390fb71fd'; // MEO Operations Hub DB ID

// Notion APIでHub DBからレコードを検索
const searchPayload = {
  filter: {
    property: 'Article ID',
    rich_text: {
      equals: articleId
    }
  }
};

// HTTPリクエストの準備（n8n内部処理を使用）
const hubSearchResponse = await $http.post(
  `https://api.notion.com/v1/databases/${HUB_DB_ID}/query`,
  {
    headers: {
      'Authorization': `Bearer ${NOTION_TOKEN}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json'
    },
    body: searchPayload
  }
);

// レスポンスの確認
if (!hubSearchResponse.results || hubSearchResponse.results.length === 0) {
  // レコードが存在しない場合、新規作成
  const createPayload = {
    parent: { database_id: HUB_DB_ID },
    properties: {
      'Title': {
        title: [
          {
            text: {
              content: `Article ${articleId} - ${new Date().toISOString().split('T')[0]}`
            }
          }
        ]
      },
      'Article ID': {
        rich_text: [
          {
            text: {
              content: articleId
            }
          }
        ]
      },
      'Workflow Status': {
        select: {
          name: 'Draft'
        }
      },
      'Created At': {
        date: {
          start: new Date().toISOString()
        }
      }
    }
  };

  const createResponse = await $http.post(
    'https://api.notion.com/v1/pages',
    {
      headers: {
        'Authorization': `Bearer ${NOTION_TOKEN}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
      },
      body: createPayload
    }
  );

  // 作成したレコードをコンテキストとして返す
  return {
    json: {
      context: {
        hubPageId: createResponse.id,
        articleId: articleId,
        workflowStatus: 'Draft',
        isNewEntry: true,
        properties: createResponse.properties
      },
      originalInput: $input.first().json
    }
  };
}

// 既存レコードからコンテキストを抽出
const hubRecord = hubSearchResponse.results[0];
const properties = hubRecord.properties;

// プロパティから値を抽出するヘルパー関数
const extractValue = (prop, type) => {
  if (!prop) return null;

  switch(type) {
    case 'title':
      return prop.title?.[0]?.text?.content || '';
    case 'rich_text':
      return prop.rich_text?.[0]?.text?.content || '';
    case 'select':
      return prop.select?.name || '';
    case 'multi_select':
      return prop.multi_select?.map(option => option.name) || [];
    case 'url':
      return prop.url || '';
    case 'date':
      return prop.date?.start || '';
    case 'relation':
      return prop.relation?.map(rel => rel.id) || [];
    default:
      return null;
  }
};

// コンテキストオブジェクトを構築
const context = {
  hubPageId: hubRecord.id,
  articleId: extractValue(properties['Article ID'], 'rich_text'),
  title: extractValue(properties['Title'], 'title'),
  workflowStatus: extractValue(properties['Workflow Status'], 'select'),
  channel: extractValue(properties['Channel'], 'multi_select'),
  relatedVideo: extractValue(properties['Related Video'], 'relation'),
  relatedArticle: extractValue(properties['Related Article'], 'relation'),
  latestExecutionId: extractValue(properties['Latest Execution ID'], 'rich_text'),
  scriptJson: extractValue(properties['Script JSON'], 'url'),
  assetsJson: extractValue(properties['Assets JSON'], 'url'),
  renderUrl: extractValue(properties['Render URL'], 'url'),
  thumbnailUrl: extractValue(properties['Thumbnail URL'], 'url'),
  voiceUrl: extractValue(properties['Voice URL'], 'url'),
  subtitleUrl: extractValue(properties['Subtitle URL'], 'url'),
  errorLog: extractValue(properties['Error Log'], 'rich_text'),
  scheduleDate: extractValue(properties['Schedule Date'], 'date'),
  createdAt: extractValue(properties['Created At'], 'date'),
  updatedAt: extractValue(properties['Updated At'], 'date'),
  isNewEntry: false
};

// コンテキストと元の入力データを返す
return {
  json: {
    context,
    originalInput: $input.first().json
  }
};