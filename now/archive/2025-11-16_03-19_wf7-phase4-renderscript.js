/**
 * WF7 Phase4: Creatomate RenderScript生成ロジック
 *
 * 作成日時: 2025-11-16 03:19:57 JST
 *
 * 目的:
 * Phase1（Script JSON）、Phase2（画像データ）、Phase3（音声・字幕データ）を統合し、
 * Creatomate APIに送信するRenderScriptを動的に生成する。
 *
 * 入力:
 * - $('Phase1').item.json.Script: Script JSON（7セグメント構成）
 * - $('Phase2').item.json.Assets: 画像データ配列（assetTag → originalUrl）
 * - $('Phase3').item.json.Audio: 音声・字幕データ（assetTag → audioUrl）
 *
 * 出力:
 * - renderScript: Creatomate RenderScript JSON
 *
 * 重要なルール:
 * 1. 画像URL: originalUrlを使用（driveWebContentLinkは使用不可）
 * 2. Track分離: track 1=画像、track 2=テキスト、track 3=音声
 * 3. 時間整合性: start_timeとdurationを正確に設定
 * 4. assetTagマッピング: Phase1のassetTagでPhase2/3のデータを検索
 */

// ===========================
// 1. 入力データの取得と検証
// ===========================

// Phase1: Script JSON（7セグメント構成）
const scriptData = $('Phase1').item.json.Script;
if (!scriptData || !scriptData.segments || !Array.isArray(scriptData.segments)) {
  throw new NodeOperationError(
    this.getNode(),
    'Phase1のScript JSONが不正です。segments配列が見つかりません。'
  );
}

const segments = scriptData.segments;
if (segments.length === 0) {
  throw new NodeOperationError(
    this.getNode(),
    'Phase1のScript JSONにセグメントが含まれていません。'
  );
}

// Phase2: 画像データ配列
const assetsData = $('Phase2').item.json.Assets;
if (!assetsData || !Array.isArray(assetsData)) {
  throw new NodeOperationError(
    this.getNode(),
    'Phase2のAssets JSONが不正です。Assets配列が見つかりません。'
  );
}

// Phase3: 音声・字幕データ
const audioData = $('Phase3').item.json.Audio;
if (!audioData || !audioData.segments || !Array.isArray(audioData.segments)) {
  throw new NodeOperationError(
    this.getNode(),
    'Phase3のAudio JSONが不正です。segments配列が見つかりません。'
  );
}

// ===========================
// 2. assetTagベースのマッピング
// ===========================

// Phase2: assetTag → Asset（画像データ）のマップを作成
const assetMap = {};
assetsData.forEach(asset => {
  if (asset.assetTag) {
    assetMap[asset.assetTag] = asset;
  }
});

// Phase3: assetTag → AudioSegment（音声データ）のマップを作成
const audioMap = {};
audioData.segments.forEach(audioSegment => {
  if (audioSegment.assetTag) {
    audioMap[audioSegment.assetTag] = audioSegment;
  }
});

// ===========================
// 3. RenderScript elements配列の生成
// ===========================

const elements = [];
const trackImage = 1;
const trackText = 2;
const trackAudio = 3;

let currentTime = 0; // 現在の時間（秒）

segments.forEach((segment, index) => {
  const { type, duration, subtitle, assetTag } = segment;

  // 必須フィールドの検証
  if (!assetTag) {
    throw new NodeOperationError(
      this.getNode(),
      `セグメント${index + 1}（type: ${type}）にassetTagが設定されていません。`
    );
  }

  if (!duration || duration <= 0) {
    throw new NodeOperationError(
      this.getNode(),
      `セグメント${index + 1}（assetTag: ${assetTag}）のdurationが不正です: ${duration}`
    );
  }

  // Phase2から画像データを取得
  const asset = assetMap[assetTag];
  if (!asset) {
    throw new NodeOperationError(
      this.getNode(),
      `assetTag="${assetTag}"に対応する画像データがPhase2に見つかりません。`
    );
  }

  // 画像URL（originalUrlを優先、なければエラー）
  const imageUrl = asset.originalUrl || asset.cloudinaryUrl;
  if (!imageUrl) {
    throw new NodeOperationError(
      this.getNode(),
      `assetTag="${assetTag}"の画像URLが見つかりません。originalUrlまたはcloudinaryUrlを設定してください。`
    );
  }

  // Phase3から音声データを取得
  const audioSegment = audioMap[assetTag];
  if (!audioSegment) {
    throw new NodeOperationError(
      this.getNode(),
      `assetTag="${assetTag}"に対応する音声データがPhase3に見つかりません。`
    );
  }

  const audioUrl = audioSegment.audioUrl;
  if (!audioUrl) {
    throw new NodeOperationError(
      this.getNode(),
      `assetTag="${assetTag}"の音声URLが見つかりません。`
    );
  }

  // 字幕テキスト（Phase3にあればそれを使用、なければPhase1のsubtitleを使用）
  const subtitleText = audioSegment.subtitle || subtitle;
  if (!subtitleText) {
    throw new NodeOperationError(
      this.getNode(),
      `assetTag="${assetTag}"の字幕テキストが見つかりません。`
    );
  }

  // ------------------------------
  // 要素1: 背景画像（Ken Burns効果付き）
  // ------------------------------
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

  // ------------------------------
  // 要素2: 日本語字幕テキスト
  // ------------------------------
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

  // ------------------------------
  // 要素3: 音声（TTS生成音声）
  // ------------------------------
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

// ===========================
// 4. RenderScript JSONの構築
// ===========================

const totalDuration = currentTime; // 合計時間

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

// ===========================
// 5. 出力
// ===========================

return {
  renderScript: renderScript,
  metadata: {
    totalSegments: segments.length,
    totalDuration: totalDuration,
    totalElements: elements.length,
    generatedAt: new Date().toISOString()
  }
};
