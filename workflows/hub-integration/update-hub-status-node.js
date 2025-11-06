/**
 * Update Hub Status Node for n8n
 *
 * このコードは、MEO Operations Hubデータベースのステータスと各種URLを更新する
 * n8n Codeノード用のテンプレートです。
 *
 * 使用方法:
 * 1. 各Phaseの終了時にこのコードノードを配置
 * 2. phaseNameパラメータを適切に設定（Phase1, Phase2, Phase3, Phase4, Phase5）
 * 3. 生成されたアセットのURLをinputから渡す
 */

// コンテキスト情報を前段のノードから取得
const context = $('Fetch Hub Context').first().json.context;
const hubPageId = context?.hubPageId;

if (!hubPageId) {
  throw new Error('Hub Page ID is required for status update');
}

// 現在のフェーズを判定（このノードの設定またはワークフロー変数から）
const phaseName = $json.phaseName || $env.WORKFLOW_PHASE || 'Phase1';

// フェーズごとの更新内容を定義
const phaseUpdates = {
  'Phase1': {
    status: 'ScriptReady',
    updateFields: ['Script JSON']
  },
  'Phase2': {
    status: 'AssetsReady',
    updateFields: ['Assets JSON']
  },
  'Phase3': {
    status: 'NarrationReady',
    updateFields: ['Voice URL', 'Subtitle URL']
  },
  'Phase4': {
    status: 'Rendered',
    updateFields: ['Render URL', 'Thumbnail URL']
  },
  'Phase5': {
    status: 'Distributed',
    updateFields: ['Channel']
  },
  'Error': {
    status: 'Failed',
    updateFields: ['Error Log']
  }
};

const currentPhase = phaseUpdates[phaseName] || phaseUpdates['Phase1'];

// Notion API設定
const NOTION_TOKEN = $env.NOTION_API_TOKEN || process.env.NOTION_API_TOKEN;

// 更新用のペイロードを構築
const updatePayload = {
  properties: {
    'Workflow Status': {
      select: {
        name: currentPhase.status
      }
    },
    'Latest Execution ID': {
      rich_text: [
        {
          text: {
            content: $execution.id || 'manual-' + Date.now()
          }
        }
      ]
    },
    'Updated At': {
      date: {
        start: new Date().toISOString()
      }
    }
  }
};

// フェーズ別の更新フィールドを追加
if (phaseName === 'Phase1' && $json.scriptUrl) {
  updatePayload.properties['Script JSON'] = {
    url: $json.scriptUrl
  };
}

if (phaseName === 'Phase2' && $json.assetsUrl) {
  updatePayload.properties['Assets JSON'] = {
    url: $json.assetsUrl
  };
}

if (phaseName === 'Phase3') {
  if ($json.voiceUrl) {
    updatePayload.properties['Voice URL'] = {
      url: $json.voiceUrl
    };
  }
  if ($json.subtitleUrl) {
    updatePayload.properties['Subtitle URL'] = {
      url: $json.subtitleUrl
    };
  }
}

if (phaseName === 'Phase4') {
  if ($json.renderUrl || $json.videoUrl) {
    updatePayload.properties['Render URL'] = {
      url: $json.renderUrl || $json.videoUrl
    };
  }
  if ($json.thumbnailUrl) {
    updatePayload.properties['Thumbnail URL'] = {
      url: $json.thumbnailUrl
    };
  }
}

if (phaseName === 'Phase5' && $json.channels) {
  updatePayload.properties['Channel'] = {
    multi_select: $json.channels.map(channel => ({ name: channel }))
  };
}

// エラーハンドリング
if (phaseName === 'Error' && $json.error) {
  updatePayload.properties['Workflow Status'] = {
    select: {
      name: 'Failed'
    }
  };
  updatePayload.properties['Error Log'] = {
    rich_text: [
      {
        text: {
          content: `[${new Date().toISOString()}] ${$json.error.message || $json.error}\nStack: ${$json.error.stack || 'N/A'}`
        }
      }
    ]
  };
}

// Notion APIを使用してHub DBを更新
try {
  const response = await $http.patch(
    `https://api.notion.com/v1/pages/${hubPageId}`,
    {
      headers: {
        'Authorization': `Bearer ${NOTION_TOKEN}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
      },
      body: updatePayload
    }
  );

  // 成功レスポンスを返す
  return {
    json: {
      success: true,
      phase: phaseName,
      status: currentPhase.status,
      hubPageId: hubPageId,
      updatedFields: Object.keys(updatePayload.properties),
      timestamp: new Date().toISOString(),
      originalInput: $input.first().json
    }
  };
} catch (error) {
  // エラーをHub DBに記録
  const errorPayload = {
    properties: {
      'Workflow Status': {
        select: {
          name: 'Failed'
        }
      },
      'Error Log': {
        rich_text: [
          {
            text: {
              content: `[${phaseName}] ${error.message}\n${error.stack}`
            }
          }
        ]
      }
    }
  };

  await $http.patch(
    `https://api.notion.com/v1/pages/${hubPageId}`,
    {
      headers: {
        'Authorization': `Bearer ${NOTION_TOKEN}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
      },
      body: errorPayload
    }
  );

  throw error;
}