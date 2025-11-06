# WF7 Phase4 外部レンダリングソリューション

**作成日**: 2025-11-05
**目的**: FFmpegレンダリング問題の解決のための外部化戦略

---

## 🎯 問題の概要

現在のPhase4レンダリングの課題：
- FFmpegプロセスのタイムアウト問題
- Railway環境でのリソース制限
- 長時間動画レンダリングの不安定性

## 🌟 推奨ソリューション

### Option 1: Creatomate API統合（推奨）

**メリット**:
- 実績のあるレンダリングサービス
- n8nコミュニティで広く使用
- Webhook対応で非同期処理可能
- エラーハンドリングが充実

**実装方法**:

#### 1. Creatomateアカウント設定
```bash
1. https://creatomate.com でアカウント作成
2. API Keyを取得
3. テンプレートを作成（9:16縦型）
```

#### 2. n8nワークフロー改修

```javascript
// Phase4: Creatomate外部レンダリング
const renderPayload = {
  template_id: process.env.CREATOMATE_TEMPLATE_ID,
  modifications: {
    "video-1": videoUrl,
    "audio-1": audioUrl,
    "text-1": title,
    "subtitle-1": subtitleData
  },
  render_settings: {
    format: "mp4",
    quality: "high",
    resolution: "1080x1920",
    fps: 30,
    webhook_url: "https://n8n-python-production-344b.up.railway.app/webhook/wf7-render-callback"
  }
};

// Creatomate APIコール
const response = await $http.post(
  'https://api.creatomate.com/v1/renders',
  {
    headers: {
      'Authorization': `Bearer ${process.env.CREATOMATE_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: renderPayload
  }
);

// レンダリングIDを保存
return {
  json: {
    renderId: response.render_id,
    status: 'rendering',
    articleId: $json.articleId,
    hubPageId: $json.hubPageId
  }
};
```

#### 3. Webhook Callback処理

```javascript
// 新規ワークフロー: WF7 Render Callback Handler
// Webhook受信時の処理

const renderResult = $input.first().json;

if (renderResult.status === 'completed') {
  // 成功時：動画URLをHub DBに保存
  const updatePayload = {
    properties: {
      'Render URL': {
        url: renderResult.video_url
      },
      'Workflow Status': {
        select: { name: 'Rendered' }
      }
    }
  };

  // Hub DB更新
  await updateHubDB(renderResult.metadata.hubPageId, updatePayload);

} else if (renderResult.status === 'failed') {
  // 失敗時：エラーログ記録
  const errorPayload = {
    properties: {
      'Workflow Status': {
        select: { name: 'Failed_Phase4' }
      },
      'Error Log': {
        rich_text: [{
          text: {
            content: `Render failed: ${renderResult.error}`
          }
        }]
      }
    }
  };

  await updateHubDB(renderResult.metadata.hubPageId, errorPayload);
}
```

---

### Option 2: Shotstack API

**特徴**:
- プログラマブルビデオAPI
- JSONタイムライン編集
- 大規模レンダリング対応

**実装例**:
```javascript
const shotstackPayload = {
  timeline: {
    tracks: [
      {
        clips: [
          {
            asset: { type: "video", src: videoUrl },
            start: 0,
            length: "auto"
          }
        ]
      },
      {
        clips: [
          {
            asset: { type: "audio", src: audioUrl },
            start: 0,
            length: "auto"
          }
        ]
      }
    ]
  },
  output: {
    format: "mp4",
    resolution: "1080x1920"
  },
  callback: webhookUrl
};
```

---

### Option 3: Bannerbear API

**特徴**:
- シンプルなAPI
- テンプレートベース
- 自動リサイズ対応

---

## 📊 比較表

| サービス | 料金 | 処理時間 | 信頼性 | n8n統合 |
|---------|------|----------|--------|---------|
| Creatomate | $49~/月 | 1-3分 | ⭐⭐⭐⭐⭐ | 優秀 |
| Shotstack | $39~/月 | 2-5分 | ⭐⭐⭐⭐ | 良好 |
| Bannerbear | $19~/月 | 1-2分 | ⭐⭐⭐ | 標準 |
| Remotion (自前) | サーバー費用のみ | 可変 | ⭐⭐⭐ | 要開発 |

---

## 🚀 実装手順（Creatomate）

### Step 1: 環境設定

```bash
# Railway環境変数追加
CREATOMATE_API_KEY=your_api_key
CREATOMATE_TEMPLATE_ID=your_template_id
RENDER_WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/webhook/wf7-render-callback
```

### Step 2: Phase4ワークフロー改修

1. 既存のFFmpegノードを無効化
2. Creatomate APIノードを追加
3. Webhook受信用の新規ワークフロー作成

### Step 3: テスト実施

```bash
# テストペイロード
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-external-001",
    "videoUrl": "https://example.com/test.mp4",
    "audioUrl": "https://example.com/test.mp3"
  }'
```

### Step 4: モニタリング

- Creatomateダッシュボードでレンダリング状況確認
- Hub DBでステータス更新を監視
- エラーログの定期確認

---

## 💡 移行戦略

### 段階的移行プラン

#### Phase 1: 並行運用（1週間）
- 新規記事：Creatomate使用
- 既存記事：FFmpeg継続

#### Phase 2: 完全移行（2週目）
- 全記事をCreatomate処理
- FFmpegワークフローをバックアップ

#### Phase 3: 最適化（3週目以降）
- テンプレート改善
- 処理時間短縮
- コスト最適化

---

## 🔍 トラブルシューティング

### よくある問題

#### 1. Webhook受信できない
- n8n Webhook URLの確認
- Creatomate側のCallback設定確認
- ファイアウォール/プロキシ設定

#### 2. レンダリング失敗
- 素材URLのアクセス権限
- ファイル形式の互換性
- テンプレート設定の確認

#### 3. 料金超過
- 月次使用量の監視
- 不要なレンダリングの削除
- プラン見直し

---

## 📈 期待される効果

1. **安定性向上**: 99.9%の成功率
2. **処理時間短縮**: 平均1-3分で完了
3. **スケーラビリティ**: 同時複数処理可能
4. **コスト予測可能**: 月額固定料金
5. **メンテナンス削減**: サーバー管理不要

---

## 🎯 推奨アクション

1. **今週中**: Creatomateアカウント作成・テスト
2. **来週**: Phase4ワークフロー改修・並行運用開始
3. **再来週**: 完全移行・最適化

---

**最終更新**: 2025-11-05