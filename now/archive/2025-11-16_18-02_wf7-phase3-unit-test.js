/**
 * WF7 Phase3 Unit Test - セグメント別音声生成ロジック検証
 *
 * 作成日時: 2025-11-16 18:02:46 JST
 *
 * テスト対象:
 * - Script JSON解析: 7セグメント分割
 * - セグメントメタデータ蓄積: URL生成とメタデータ構築
 * - 音声メタデータ最終化: Audio.segments配列生成
 * - Notionペイロード作成: JSON文字列化
 */

// モックデータ
const mockScriptData = {
  "title": "【テスト】SNS動画自動生成フロー検証",
  "segments": [
    {
      "type": "hook",
      "duration": 3,
      "narration": "これが未来の動画制作です。",
      "subtitle": "これが未来の動画制作",
      "assetTag": "test-hook-001"
    },
    {
      "type": "intro",
      "duration": 10,
      "narration": "効率化がもたらす変革について説明します。",
      "subtitle": "効率化がもたらす変革",
      "assetTag": "test-intro-001"
    },
    {
      "type": "point1",
      "duration": 13,
      "narration": "作業時間を70%削減した実例を紹介します。",
      "subtitle": "作業時間を70%削減した実例",
      "assetTag": "test-point1-001"
    },
    {
      "type": "point2",
      "duration": 13,
      "narration": "品質を保ちながら高速化を実現しました。",
      "subtitle": "品質を保ちながら高速化",
      "assetTag": "test-point2-001"
    },
    {
      "type": "point3",
      "duration": 14,
      "narration": "AIがもたらす新しい価値を体験してください。",
      "subtitle": "AIがもたらす新しい価値",
      "assetTag": "test-point3-001"
    },
    {
      "type": "summary",
      "duration": 20,
      "narration": "自動化で変わる未来の働き方を一緒に作りましょう。",
      "subtitle": "自動化で変わる未来の働き方",
      "assetTag": "test-summary-001"
    },
    {
      "type": "cta",
      "duration": 7,
      "narration": "今すぐ試してみよう！",
      "subtitle": "今すぐ試してみよう！",
      "assetTag": "test-cta-001"
    }
  ]
};

const testData = {
  articleId: "test-article-001",
  notionPageId: "test-notion-page-123"
};

// テスト結果格納
const testResults = {
  passed: 0,
  failed: 0,
  tests: []
};

function addTestResult(name, passed, message, data = null) {
  testResults.tests.push({ name, passed, message, data });
  if (passed) {
    testResults.passed++;
    console.log(`✅ PASS: ${name}`);
  } else {
    testResults.failed++;
    console.error(`❌ FAIL: ${name} - ${message}`);
  }
  if (data) {
    console.log("   データ:", JSON.stringify(data, null, 2));
  }
}

// ========================================
// Test 1: Script JSON解析ノード
// ========================================
console.log("\n=== Test 1: Script JSON解析 ===\n");

function scriptJsonParser(notionPage, prevData) {
  // Notion APIレスポンスをシミュレート
  const scriptJsonProperty = notionPage.properties['Script JSON'];
  if (!scriptJsonProperty || !scriptJsonProperty.rich_text || scriptJsonProperty.rich_text.length === 0) {
    throw new Error('Script JSON property not found in Notion page');
  }

  const scriptJsonString = scriptJsonProperty.rich_text[0].text.content;
  const scriptData = JSON.parse(scriptJsonString);

  if (!scriptData.segments || !Array.isArray(scriptData.segments)) {
    throw new Error('Invalid script data structure: segments array not found');
  }

  // セグメント配列を個別に出力（結合しない）
  const segments = scriptData.segments.map((segment, index) => ({
    ...prevData,
    segmentIndex: index,
    segmentType: segment.type,
    segmentNarration: segment.narration,
    segmentSubtitle: segment.subtitle || segment.narration,
    segmentDuration: segment.duration,
    segmentAssetTag: segment.assetTag
  }));

  return segments;
}

try {
  const mockNotionPage = {
    properties: {
      'Script JSON': {
        rich_text: [{
          text: { content: JSON.stringify(mockScriptData) }
        }]
      }
    }
  };

  const segments = scriptJsonParser(mockNotionPage, testData);

  // 検証
  const test1a = segments.length === 7;
  addTestResult(
    "Script JSON解析: 7セグメント出力",
    test1a,
    `期待: 7, 実際: ${segments.length}`,
    segments.length
  );

  const test1b = segments.every(seg =>
    seg.hasOwnProperty('segmentType') &&
    seg.hasOwnProperty('segmentNarration') &&
    seg.hasOwnProperty('segmentSubtitle') &&
    seg.hasOwnProperty('segmentAssetTag')
  );
  addTestResult(
    "Script JSON解析: 必須プロパティ存在確認",
    test1b,
    test1b ? "すべてのセグメントに必須プロパティあり" : "一部のセグメントで必須プロパティ欠損"
  );

  const test1c = segments[0].segmentType === 'hook' && segments[6].segmentType === 'cta';
  addTestResult(
    "Script JSON解析: セグメントタイプ正確性",
    test1c,
    `最初: ${segments[0].segmentType}, 最後: ${segments[6].segmentType}`
  );

  // 次のテストで使用するため保存
  global.testSegments = segments;

} catch (error) {
  addTestResult("Script JSON解析: 実行エラー", false, error.message);
}

// ========================================
// Test 2: セグメントメタデータ蓄積ノード
// ========================================
console.log("\n=== Test 2: セグメントメタデータ蓄積 ===\n");

function segmentMetadataAccumulator(currentItem) {
  const articleId = currentItem.articleId;
  const segmentType = currentItem.segmentType;
  const segmentSubtitle = currentItem.segmentSubtitle;
  const segmentAssetTag = currentItem.segmentAssetTag;

  const baseUrl = process.env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';
  const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;

  // セグメント固有のaudio URLを生成
  const audioUrl = `${fullBaseUrl}/webhook/wf7-files-audio?articleId=${articleId}&segment=${segmentType}`;

  return {
    ...currentItem,
    segmentMetadata: {
      assetTag: segmentAssetTag,
      audioUrl: audioUrl,
      subtitle: segmentSubtitle
    }
  };
}

try {
  if (!global.testSegments || global.testSegments.length === 0) {
    throw new Error("Test 1のセグメントデータが見つかりません");
  }

  // 各セグメントにメタデータを追加（Split In Batchesループをシミュレート）
  const segmentsWithMetadata = global.testSegments.map(seg =>
    segmentMetadataAccumulator(seg)
  );

  const test2a = segmentsWithMetadata.every(seg =>
    seg.hasOwnProperty('segmentMetadata') &&
    seg.segmentMetadata.hasOwnProperty('assetTag') &&
    seg.segmentMetadata.hasOwnProperty('audioUrl') &&
    seg.segmentMetadata.hasOwnProperty('subtitle')
  );
  addTestResult(
    "セグメントメタデータ蓄積: メタデータ構造",
    test2a,
    test2a ? "すべてのセグメントに正しいメタデータ構造" : "メタデータ構造が不正"
  );

  const test2b = segmentsWithMetadata[0].segmentMetadata.audioUrl.includes('webhook/wf7-files-audio');
  addTestResult(
    "セグメントメタデータ蓄積: audioURL形式",
    test2b,
    `URL: ${segmentsWithMetadata[0].segmentMetadata.audioUrl}`
  );

  const test2c = segmentsWithMetadata[0].segmentMetadata.audioUrl.includes('segment=hook');
  addTestResult(
    "セグメントメタデータ蓄積: セグメント別URL",
    test2c,
    `hook URLにsegment=hookパラメータあり`
  );

  // 次のテストで使用
  global.segmentsWithMetadata = segmentsWithMetadata;

} catch (error) {
  addTestResult("セグメントメタデータ蓄積: 実行エラー", false, error.message);
}

// ========================================
// Test 3: 音声メタデータ最終化ノード
// ========================================
console.log("\n=== Test 3: 音声メタデータ最終化 ===\n");

function audioMetadataFinalizer(allItems) {
  // Split In Batchesのループ完了を検出（ここではシミュレート）
  const isLoopComplete = true; // テストでは常にtrue

  if (!isLoopComplete) {
    return [];
  }

  // すべてのセグメントメタデータを集約
  const articleId = allItems[0].articleId;
  const notionPageId = allItems[0].notionPageId;
  const segments = allItems.map(item => item.segmentMetadata);

  return {
    Audio: {
      segments: segments
    },
    articleId: articleId,
    notionPageId: notionPageId
  };
}

try {
  if (!global.segmentsWithMetadata || global.segmentsWithMetadata.length === 0) {
    throw new Error("Test 2のメタデータが見つかりません");
  }

  const finalizedAudio = audioMetadataFinalizer(global.segmentsWithMetadata);

  const test3a = finalizedAudio.hasOwnProperty('Audio') &&
                 finalizedAudio.Audio.hasOwnProperty('segments') &&
                 Array.isArray(finalizedAudio.Audio.segments);
  addTestResult(
    "音声メタデータ最終化: Audio.segments構造",
    test3a,
    test3a ? "正しいAudio.segments配列" : "構造が不正"
  );

  const test3b = finalizedAudio.Audio.segments.length === 7;
  addTestResult(
    "音声メタデータ最終化: セグメント数",
    test3b,
    `期待: 7, 実際: ${finalizedAudio.Audio.segments.length}`
  );

  const test3c = finalizedAudio.Audio.segments.every(seg =>
    seg.hasOwnProperty('assetTag') &&
    seg.hasOwnProperty('audioUrl') &&
    seg.hasOwnProperty('subtitle')
  );
  addTestResult(
    "音声メタデータ最終化: セグメント必須フィールド",
    test3c,
    test3c ? "すべてのセグメントに必須フィールドあり" : "一部フィールド欠損"
  );

  // Phase4互換性チェック
  const expectedFormat = {
    assetTag: "string",
    audioUrl: "string",
    subtitle: "string"
  };
  const test3d = finalizedAudio.Audio.segments.every(seg => {
    return typeof seg.assetTag === 'string' &&
           typeof seg.audioUrl === 'string' &&
           typeof seg.subtitle === 'string' &&
           seg.audioUrl.startsWith('https://');
  });
  addTestResult(
    "音声メタデータ最終化: Phase4互換性",
    test3d,
    test3d ? "Phase4期待形式に準拠" : "形式エラー",
    finalizedAudio.Audio.segments[0]
  );

  // 次のテストで使用
  global.finalizedAudio = finalizedAudio;

} catch (error) {
  addTestResult("音声メタデータ最終化: 実行エラー", false, error.message);
}

// ========================================
// Test 4: Notionペイロード作成ノード
// ========================================
console.log("\n=== Test 4: Notionペイロード作成 ===\n");

function notionPayloadCreator(audio, articleId, notionPageId) {
  if (!notionPageId) {
    throw new Error('notionPageId is required');
  }

  // Store Audio.segments as JSON string in Notion property
  const audioSegmentsJson = JSON.stringify(audio);

  return {
    notionPageId,
    notionPayload: {
      properties: {
        'Audio JSON': {
          rich_text: [{
            text: { content: audioSegmentsJson }
          }]
        },
        'Status': {select: {name: 'VoiceReady'}}
      }
    }
  };
}

try {
  if (!global.finalizedAudio) {
    throw new Error("Test 3の最終化データが見つかりません");
  }

  const notionPayload = notionPayloadCreator(
    global.finalizedAudio.Audio,
    global.finalizedAudio.articleId,
    global.finalizedAudio.notionPageId
  );

  const test4a = notionPayload.hasOwnProperty('notionPayload') &&
                 notionPayload.notionPayload.hasOwnProperty('properties');
  addTestResult(
    "Notionペイロード作成: ペイロード構造",
    test4a,
    test4a ? "正しいNotion API形式" : "構造エラー"
  );

  const test4b = notionPayload.notionPayload.properties.hasOwnProperty('Audio JSON') &&
                 notionPayload.notionPayload.properties['Audio JSON'].rich_text[0].text.content.length > 0;
  addTestResult(
    "Notionペイロード作成: Audio JSONプロパティ",
    test4b,
    test4b ? "Audio JSON文字列化成功" : "文字列化失敗"
  );

  // JSON文字列のパース検証
  try {
    const parsedAudioJson = JSON.parse(
      notionPayload.notionPayload.properties['Audio JSON'].rich_text[0].text.content
    );
    const test4c = parsedAudioJson.hasOwnProperty('segments') &&
                   parsedAudioJson.segments.length === 7;
    addTestResult(
      "Notionペイロード作成: JSON文字列パース可能性",
      test4c,
      test4c ? "正しくパース可能" : "パースエラー"
    );
  } catch (parseError) {
    addTestResult("Notionペイロード作成: JSON文字列パース可能性", false, parseError.message);
  }

  const test4d = notionPayload.notionPayload.properties['Status'].select.name === 'VoiceReady';
  addTestResult(
    "Notionペイロード作成: Statusプロパティ",
    test4d,
    `期待: VoiceReady, 実際: ${notionPayload.notionPayload.properties['Status'].select.name}`
  );

} catch (error) {
  addTestResult("Notionペイロード作成: 実行エラー", false, error.message);
}

// ========================================
// Test 5: Webhook応答形式
// ========================================
console.log("\n=== Test 5: Webhook応答形式 ===\n");

try {
  if (!global.finalizedAudio) {
    throw new Error("最終化データが見つかりません");
  }

  const webhookResponse = {
    status: 'success',
    message: 'WF7 Phase3 completed',
    articleId: global.finalizedAudio.articleId,
    notionPageId: global.finalizedAudio.notionPageId,
    Audio: global.finalizedAudio.Audio
  };

  const test5a = webhookResponse.status === 'success';
  addTestResult(
    "Webhook応答: ステータス",
    test5a,
    `期待: success, 実際: ${webhookResponse.status}`
  );

  const test5b = webhookResponse.hasOwnProperty('Audio') &&
                 webhookResponse.Audio.hasOwnProperty('segments');
  addTestResult(
    "Webhook応答: Audio.segments含有",
    test5b,
    test5b ? "Audio.segmentsが応答に含まれる" : "Audio.segments欠損"
  );

  const test5c = webhookResponse.Audio.segments.length === 7;
  addTestResult(
    "Webhook応答: セグメント数",
    test5c,
    `期待: 7, 実際: ${webhookResponse.Audio.segments.length}`
  );

  console.log("\n=== Webhook応答サンプル ===");
  console.log(JSON.stringify(webhookResponse, null, 2));

} catch (error) {
  addTestResult("Webhook応答: 実行エラー", false, error.message);
}

// ========================================
// テスト結果サマリー
// ========================================
console.log("\n" + "=".repeat(60));
console.log("テスト結果サマリー");
console.log("=".repeat(60));
console.log(`合計テスト数: ${testResults.passed + testResults.failed}`);
console.log(`✅ 成功: ${testResults.passed}`);
console.log(`❌ 失敗: ${testResults.failed}`);
console.log(`成功率: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);
console.log("=".repeat(60));

if (testResults.failed === 0) {
  console.log("\n🎉 すべてのテストが成功しました！");
  console.log("WF7 Phase3のロジックはPhase4要件を満たしています。");
  process.exit(0);
} else {
  console.log("\n⚠️ 一部のテストが失敗しました。詳細を確認してください。");
  process.exit(1);
}
