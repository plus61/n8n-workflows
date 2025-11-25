#!/usr/bin/env node
/**
 * WF7 Phase4: RenderScript生成ロジック Unit Test
 *
 * 作成日時: 2025-11-16 03:23:38 JST
 *
 * 目的:
 * - n8n Code Nodeで実装したRenderScript生成ロジックをローカル環境でテスト
 * - Phase1/2/3のモックデータを使用して動作確認
 * - 生成されたRenderScriptがCreatomate API仕様に準拠しているか検証
 *
 * テスト項目:
 * 1. Phase1/2/3データの正常な統合
 * 2. assetTagマッピングの正確性
 * 3. RenderScript JSON構造の妥当性
 * 4. エラーハンドリングの動作確認
 */

// ===========================
// Mock Data (Phase 1C based)
// ===========================

// Phase1: Script JSON（7セグメント構成）
const mockPhase1Data = {
  Script: {
    segments: [
      {
        type: "hook",
        duration: 3,
        subtitle: "動画制作の時短術",
        assetTag: "SNS 動画制作"
      },
      {
        type: "intro",
        duration: 10,
        subtitle: "効率化の重要性",
        assetTag: "動画編集 自動化"
      },
      {
        type: "point1",
        duration: 13,
        subtitle: "作業時間を70%削減",
        assetTag: "作業時間 削減"
      },
      {
        type: "point2",
        duration: 13,
        subtitle: "品質の均一化",
        assetTag: "テンプレート 活用"
      },
      {
        type: "point3",
        duration: 14,
        subtitle: "AIでの効率化",
        assetTag: "AI 台本生成"
      },
      {
        type: "summary",
        duration: 20,
        subtitle: "効率化のまとめ",
        assetTag: "動画制作 効率化"
      },
      {
        type: "cta",
        duration: 7,
        subtitle: "シェアしてね！",
        assetTag: "シェアする"
      }
    ]
  }
};

// Phase2: Assets JSON（7枚の画像データ）
const mockPhase2Data = {
  Assets: [
    {
      assetTag: "SNS 動画制作",
      originalUrl: "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1abc123"
    },
    {
      assetTag: "動画編集 自動化",
      originalUrl: "https://images.pexels.com/photos/1181345/pexels-photo-1181345.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1def456"
    },
    {
      assetTag: "作業時間 削減",
      originalUrl: "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1ghi789"
    },
    {
      assetTag: "テンプレート 活用",
      originalUrl: "https://images.pexels.com/photos/7947664/pexels-photo-7947664.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1jkl012"
    },
    {
      assetTag: "AI 台本生成",
      originalUrl: "https://images.pexels.com/photos/8849295/pexels-photo-8849295.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1mno345"
    },
    {
      assetTag: "動画制作 効率化",
      originalUrl: "https://images.pexels.com/photos/3183186/pexels-photo-3183186.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1pqr678"
    },
    {
      assetTag: "シェアする",
      originalUrl: "https://images.pexels.com/photos/3183190/pexels-photo-3183190.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
      driveWebContentLink: "https://drive.google.com/...",
      driveFileId: "1stu901"
    }
  ]
};

// Phase3: Audio/Subtitle JSON（7セグメント分の音声データ）
const mockPhase3Data = {
  Audio: {
    segments: [
      {
        assetTag: "SNS 動画制作",
        audioUrl: "https://elevenlabs.io/api/audio/hook.mp3",
        subtitle: "動画制作の時短術"
      },
      {
        assetTag: "動画編集 自動化",
        audioUrl: "https://elevenlabs.io/api/audio/intro.mp3",
        subtitle: "効率化の重要性"
      },
      {
        assetTag: "作業時間 削減",
        audioUrl: "https://elevenlabs.io/api/audio/point1.mp3",
        subtitle: "作業時間を70%削減"
      },
      {
        assetTag: "テンプレート 活用",
        audioUrl: "https://elevenlabs.io/api/audio/point2.mp3",
        subtitle: "品質の均一化"
      },
      {
        assetTag: "AI 台本生成",
        audioUrl: "https://elevenlabs.io/api/audio/point3.mp3",
        subtitle: "AIでの効率化"
      },
      {
        assetTag: "動画制作 効率化",
        audioUrl: "https://elevenlabs.io/api/audio/summary.mp3",
        subtitle: "効率化のまとめ"
      },
      {
        assetTag: "シェアする",
        audioUrl: "https://elevenlabs.io/api/audio/cta.mp3",
        subtitle: "シェアしてね！"
      }
    ]
  }
};

// ===========================
// n8n Environment Emulation
// ===========================

/**
 * NodeOperationError エミュレーション
 */
class NodeOperationError extends Error {
  constructor(node, message) {
    super(message);
    this.name = 'NodeOperationError';
    this.node = node;
  }
}

/**
 * n8nのノード参照 $('NodeName') エミュレーション
 */
function createMockN8nContext() {
  return {
    Phase1: {
      item: {
        json: mockPhase1Data
      }
    },
    Phase2: {
      item: {
        json: mockPhase2Data
      }
    },
    Phase3: {
      item: {
        json: mockPhase3Data
      }
    }
  };
}

function createMockThis() {
  return {
    getNode: () => ({ name: 'RenderScript Generator' })
  };
}

// ===========================
// RenderScript Generation Logic
// (from 2025-11-16_03-19_wf7-phase4-renderscript.js)
// ===========================

function generateRenderScript($, thisContext) {
  // 1. 入力データの取得と検証
  const scriptData = $('Phase1').item.json.Script;
  if (!scriptData || !scriptData.segments || !Array.isArray(scriptData.segments)) {
    throw new NodeOperationError(
      thisContext.getNode(),
      'Phase1のScript JSONが不正です。segments配列が見つかりません。'
    );
  }

  const segments = scriptData.segments;
  if (segments.length === 0) {
    throw new NodeOperationError(
      thisContext.getNode(),
      'Phase1のScript JSONにセグメントが含まれていません。'
    );
  }

  const assetsData = $('Phase2').item.json.Assets;
  if (!assetsData || !Array.isArray(assetsData)) {
    throw new NodeOperationError(
      thisContext.getNode(),
      'Phase2のAssets JSONが不正です。Assets配列が見つかりません。'
    );
  }

  const audioData = $('Phase3').item.json.Audio;
  if (!audioData || !audioData.segments || !Array.isArray(audioData.segments)) {
    throw new NodeOperationError(
      thisContext.getNode(),
      'Phase3のAudio JSONが不正です。segments配列が見つかりません。'
    );
  }

  // 2. assetTagベースのマッピング
  const assetMap = {};
  assetsData.forEach(asset => {
    if (asset.assetTag) {
      assetMap[asset.assetTag] = asset;
    }
  });

  const audioMap = {};
  audioData.segments.forEach(audioSegment => {
    if (audioSegment.assetTag) {
      audioMap[audioSegment.assetTag] = audioSegment;
    }
  });

  // 3. RenderScript elements配列の生成
  const elements = [];
  const trackImage = 1;
  const trackText = 2;
  const trackAudio = 3;

  let currentTime = 0;

  segments.forEach((segment, index) => {
    const { type, duration, subtitle, assetTag } = segment;

    // 必須フィールドの検証
    if (!assetTag) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `セグメント${index + 1}（type: ${type}）にassetTagが設定されていません。`
      );
    }

    if (!duration || duration <= 0) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `セグメント${index + 1}（assetTag: ${assetTag}）のdurationが不正です: ${duration}`
      );
    }

    // Phase2から画像データを取得
    const asset = assetMap[assetTag];
    if (!asset) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `assetTag="${assetTag}"に対応する画像データがPhase2に見つかりません。`
      );
    }

    // 画像URL（originalUrlを優先、なければエラー）
    const imageUrl = asset.originalUrl || asset.cloudinaryUrl;
    if (!imageUrl) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `assetTag="${assetTag}"の画像URLが見つかりません。originalUrlまたはcloudinaryUrlを設定してください。`
      );
    }

    // Phase3から音声データを取得
    const audioSegment = audioMap[assetTag];
    if (!audioSegment) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `assetTag="${assetTag}"に対応する音声データがPhase3に見つかりません。`
      );
    }

    const audioUrl = audioSegment.audioUrl;
    if (!audioUrl) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `assetTag="${assetTag}"の音声URLが見つかりません。`
      );
    }

    // 字幕テキスト（Phase3にあればそれを使用、なければPhase1のsubtitleを使用）
    const subtitleText = audioSegment.subtitle || subtitle;
    if (!subtitleText) {
      throw new NodeOperationError(
        thisContext.getNode(),
        `assetTag="${assetTag}"の字幕テキストが見つかりません。`
      );
    }

    // 要素1: 背景画像（Ken Burns効果付き）
    elements.push({
      type: "image",
      source: imageUrl,
      track: trackImage,
      time: currentTime,
      duration: duration,
      animations: [
        {
          type: "scale",
          start_scale: "120%",
          end_scale: "100%",
          duration: duration,
          easing: "cubic-in-out",
          scope: "element"
        }
      ]
    });

    // 要素2: 日本語字幕テキスト
    elements.push({
      type: "text",
      text: subtitleText,
      font_family: "Noto Sans JP",
      font_size: "60 px",
      color: "#FFFFFF",
      y: "50%",
      x: "50%",
      x_anchor: "50%",
      y_anchor: "50%",
      track: trackText,
      time: currentTime,
      duration: duration
    });

    // 要素3: 音声（TTS生成音声）
    elements.push({
      type: "audio",
      source: audioUrl,
      track: trackAudio,
      time: currentTime,
      duration: duration
    });

    // 次のセグメントの開始時間を更新
    currentTime += duration;
  });

  // 4. RenderScript JSONの構築
  const totalDuration = currentTime;

  const renderScript = {
    template_id: "40ff626c-9e09-4769-b8b9-66e859ecafa9",
    modifications: {
      output_format: "mp4",
      width: 1080,
      height: 1920,
      duration: totalDuration,
      elements: elements
    }
  };

  // 5. 出力
  return {
    renderScript: renderScript,
    metadata: {
      totalSegments: segments.length,
      totalDuration: totalDuration,
      totalElements: elements.length,
      generatedAt: new Date().toISOString()
    }
  };
}

// ===========================
// Test Execution & Validation
// ===========================

console.log("=".repeat(60));
console.log("WF7 Phase4: RenderScript生成ロジック Unit Test");
console.log("=".repeat(60));
console.log();

try {
  // n8n環境エミュレーション
  const mockContext = createMockN8nContext();
  const $ = (nodeName) => mockContext[nodeName];
  const thisContext = createMockThis();

  console.log("📋 テスト実行開始...");
  console.log();

  // RenderScript生成
  const result = generateRenderScript($, thisContext);

  console.log("✅ RenderScript生成成功！");
  console.log();

  // ===========================
  // 検証 1: メタデータの確認
  // ===========================
  console.log("📊 検証 1: メタデータ");
  console.log(`   - セグメント数: ${result.metadata.totalSegments} (期待値: 7)`);
  console.log(`   - 合計時間: ${result.metadata.totalDuration}秒 (期待値: 80秒)`);
  console.log(`   - 要素数: ${result.metadata.totalElements} (期待値: 21 [7セグメント × 3要素])`);
  console.log(`   - 生成日時: ${result.metadata.generatedAt}`);
  console.log();

  if (result.metadata.totalSegments !== 7) {
    throw new Error(`セグメント数が不正: ${result.metadata.totalSegments} (期待値: 7)`);
  }
  if (result.metadata.totalDuration !== 80) {
    throw new Error(`合計時間が不正: ${result.metadata.totalDuration} (期待値: 80)`);
  }
  if (result.metadata.totalElements !== 21) {
    throw new Error(`要素数が不正: ${result.metadata.totalElements} (期待値: 21)`);
  }
  console.log("✅ 検証 1: メタデータ - OK");
  console.log();

  // ===========================
  // 検証 2: RenderScript構造
  // ===========================
  console.log("📊 検証 2: RenderScript構造");
  console.log(`   - Template ID: ${result.renderScript.template_id}`);
  console.log(`   - Output Format: ${result.renderScript.modifications.output_format}`);
  console.log(`   - 動画サイズ: ${result.renderScript.modifications.width}x${result.renderScript.modifications.height}`);
  console.log(`   - Duration: ${result.renderScript.modifications.duration}秒`);
  console.log(`   - Elements: ${result.renderScript.modifications.elements.length}個`);
  console.log();

  if (result.renderScript.template_id !== "40ff626c-9e09-4769-b8b9-66e859ecafa9") {
    throw new Error("Template IDが不正");
  }
  if (result.renderScript.modifications.output_format !== "mp4") {
    throw new Error("Output Formatが不正");
  }
  if (result.renderScript.modifications.width !== 1080 || result.renderScript.modifications.height !== 1920) {
    throw new Error("動画サイズが不正");
  }
  console.log("✅ 検証 2: RenderScript構造 - OK");
  console.log();

  // ===========================
  // 検証 3: 要素の詳細確認
  // ===========================
  console.log("📊 検証 3: 要素の詳細確認（最初のセグメント）");
  const firstImageElement = result.renderScript.modifications.elements[0];
  const firstTextElement = result.renderScript.modifications.elements[1];
  const firstAudioElement = result.renderScript.modifications.elements[2];

  console.log("   [Image Element]");
  console.log(`   - Type: ${firstImageElement.type}`);
  console.log(`   - Source: ${firstImageElement.source.substring(0, 60)}...`);
  console.log(`   - Track: ${firstImageElement.track}`);
  console.log(`   - Time: ${firstImageElement.time}`);
  console.log(`   - Duration: ${firstImageElement.duration}`);
  console.log(`   - Animation: ${firstImageElement.animations[0].type} (${firstImageElement.animations[0].start_scale} → ${firstImageElement.animations[0].end_scale})`);
  console.log();

  console.log("   [Text Element]");
  console.log(`   - Type: ${firstTextElement.type}`);
  console.log(`   - Text: ${firstTextElement.text}`);
  console.log(`   - Font: ${firstTextElement.font_family}`);
  console.log(`   - Font Size: ${firstTextElement.font_size}`);
  console.log(`   - Color: ${firstTextElement.color}`);
  console.log(`   - Track: ${firstTextElement.track}`);
  console.log();

  console.log("   [Audio Element]");
  console.log(`   - Type: ${firstAudioElement.type}`);
  console.log(`   - Source: ${firstAudioElement.source}`);
  console.log(`   - Track: ${firstAudioElement.track}`);
  console.log();

  if (firstImageElement.type !== "image" || firstImageElement.track !== 1) {
    throw new Error("Image Elementの構造が不正");
  }
  if (firstTextElement.type !== "text" || firstTextElement.track !== 2) {
    throw new Error("Text Elementの構造が不正");
  }
  if (firstAudioElement.type !== "audio" || firstAudioElement.track !== 3) {
    throw new Error("Audio Elementの構造が不正");
  }
  console.log("✅ 検証 3: 要素の詳細確認 - OK");
  console.log();

  // ===========================
  // 検証 4: assetTagマッピング確認
  // ===========================
  console.log("📊 検証 4: assetTagマッピング確認");
  const expectedMappings = [
    { segmentIdx: 0, assetTag: "SNS 動画制作", expectedUrl: "https://images.pexels.com/photos/7193859/" },
    { segmentIdx: 6, assetTag: "シェアする", expectedUrl: "https://images.pexels.com/photos/3183190/" }
  ];

  expectedMappings.forEach((mapping) => {
    const imageElement = result.renderScript.modifications.elements[mapping.segmentIdx * 3];
    if (!imageElement.source.includes(mapping.expectedUrl)) {
      throw new Error(`assetTag="${mapping.assetTag}"のマッピングが不正: ${imageElement.source}`);
    }
    console.log(`   ✅ "${mapping.assetTag}" (セグメント${mapping.segmentIdx + 1}) → 正しい画像URL`);
  });
  console.log();
  console.log("✅ 検証 4: assetTagマッピング - OK");
  console.log();

  // ===========================
  // 検証 5: 時間整合性確認
  // ===========================
  console.log("📊 検証 5: 時間整合性確認");
  let expectedTime = 0;
  for (let i = 0; i < 7; i++) {
    const segmentIdx = i * 3; // 各セグメントの最初の要素（image）
    const imageElement = result.renderScript.modifications.elements[segmentIdx];
    const textElement = result.renderScript.modifications.elements[segmentIdx + 1];
    const audioElement = result.renderScript.modifications.elements[segmentIdx + 2];

    if (imageElement.time !== expectedTime || textElement.time !== expectedTime || audioElement.time !== expectedTime) {
      throw new Error(`セグメント${i + 1}の時間が不正: ${imageElement.time} (期待値: ${expectedTime})`);
    }

    console.log(`   セグメント${i + 1}: time=${imageElement.time}秒, duration=${imageElement.duration}秒 ✅`);
    expectedTime += imageElement.duration;
  }
  console.log();
  console.log("✅ 検証 5: 時間整合性 - OK");
  console.log();

  // ===========================
  // テスト成功
  // ===========================
  console.log("=".repeat(60));
  console.log("✅ すべてのテストが成功しました！");
  console.log("=".repeat(60));
  console.log();
  console.log("📋 生成されたRenderScriptサマリー:");
  console.log(`   - Template ID: ${result.renderScript.template_id}`);
  console.log(`   - 動画サイズ: ${result.renderScript.modifications.width}x${result.renderScript.modifications.height}`);
  console.log(`   - 合計時間: ${result.renderScript.modifications.duration}秒`);
  console.log(`   - セグメント数: ${result.metadata.totalSegments}`);
  console.log(`   - 要素数: ${result.metadata.totalElements}`);
  console.log();
  console.log("次のステップ:");
  console.log("- [ ] Step 2: HTTP Request Node設定（Creatomate API呼び出し）");
  console.log("- [ ] Step 3: Wait Node + ポーリングループ実装");
  console.log("- [ ] Step 4: 動画URL抽出 + Notion更新");
  console.log("- [ ] Integration Test: Phase1-4完全統合テスト");
  console.log();

  // RenderScriptをファイルに出力（デバッグ用）
  const fs = require('fs');
  const outputPath = '/tmp/renderscript-test-output.json';
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.log(`📁 RenderScript出力: ${outputPath}`);

} catch (error) {
  console.error("❌ テスト失敗:");
  console.error(`   ${error.message}`);
  if (error.stack) {
    console.error();
    console.error("Stack Trace:");
    console.error(error.stack);
  }
  process.exit(1);
}
