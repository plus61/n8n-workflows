# n8nワークフロー ベストプラクティス

n8nワークフロー開発・運用における推奨事項とアンチパターン

## 📐 ワークフロー設計の原則

### 1. 単一責任の原則

**推奨:**
- 1つのワークフローは1つの明確な目的を持つ
- 複雑な処理は複数のワークフローに分割

**アンチパターン:**
- 1つのワークフローで複数の無関係な処理を実行
- 過度に複雑なワークフロー(50ノード以上)

### 2. エラーハンドリング

**推奨:**
```javascript
// Functionノードでのエラーハンドリング例
try {
  const result = await someOperation();
  return { json: { success: true, data: result } };
} catch (error) {
  return { 
    json: { 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    } 
  };
}
```

**重要ポイント:**
- ✅ すべての外部API呼び出しにエラーハンドリングを実装
- ✅ エラー発生時の通知設定(Slack、Email等)
- ✅ エラーログの記録
- ✅ リトライロジックの実装(必要に応じて)

### 3. ノード命名規則

**推奨:**
- 処理内容が一目でわかる名前
- 動詞+目的語の形式(例: "Fetch User Data", "Update Notion")
- 日本語でも英語でも統一性を保つ

**例:**
- ✅ "LINE Webhook受信"
- ✅ "Notionユーザー検索"
- ✅ "データ変換"
- ❌ "Node1"
- ❌ "処理"
- ❌ "test"

## 🔐 セキュリティ

### 認証情報の管理

**推奨:**
- 環境変数で管理
- n8nのCredentials機能を使用
- 定期的なトークン更新

**アンチパターン:**
- ❌ ワークフロー内にAPIキーをハードコード
- ❌ 認証情報をログに出力
- ❌ 不要な権限を持つトークンの使用

### データの取り扱い

**推奨:**
- 個人情報は最小限の保持期間
- 機密データの暗号化
- アクセスログの記録

## ⚡ パフォーマンス最適化

### 1. バッチ処理

**推奨:**
```javascript
// 複数アイテムを一度に処理
const items = $input.all();
const results = await Promise.all(
  items.map(item => processItem(item))
);
return results.map(r => ({ json: r }));
```

**アンチパターン:**
```javascript
// 1つずつ処理(遅い)
for (const item of items) {
  await processItem(item);
}
```

### 2. API呼び出しの最適化

**推奨:**
- 必要なデータのみ取得
- ページネーション対応
- レート制限の考慮
- キャッシュの活用

### 3. データサイズの管理

**推奨:**
- 大きなデータは分割処理
- 不要なフィールドは削除
- ログ出力は最小限に

## 📝 ドキュメンテーション

### ワークフロー内コメント

**推奨:**
- 各ノードの目的を説明
- 複雑なロジックには詳細なコメント
- 外部依存関係の記載

### README作成

**必須項目:**
- ワークフローの目的
- セットアップ手順
- 必要な認証情報
- 環境変数の説明
- トラブルシューティング

## 🧪 テスト

### テスト戦略

**推奨:**
1. **開発環境でのテスト**
   - テストデータを使用
   - すべてのブランチを確認
   - エラーケースも検証

2. **ステージング環境**
   - 本番に近い環境で検証
   - パフォーマンステスト
   - 統合テスト

3. **本番環境**
   - 段階的なロールアウト
   - モニタリング強化
   - ロールバック準備

## 🔄 バージョン管理

### Git管理

**推奨:**
- ワークフローJSONをGitで管理
- 変更時はコミットメッセージに詳細を記載
- ブランチ戦略の採用(feature/fix/hotfix)

**コミットメッセージ例:**
```
feat: LINE CRMワークフローにリッチメニュー対応を追加

- Switch nodeでpostbackイベントを処理
- Notion更新ロジックを追加
- エラーハンドリングを強化
```

## 📊 モニタリング

### ログ出力

**推奨レベル:**
- **ERROR**: エラー発生時
- **WARN**: 警告(リトライ成功等)
- **INFO**: 重要な処理の開始/完了
- **DEBUG**: 詳細なデバッグ情報(開発時のみ)

### メトリクス

**監視項目:**
- ワークフロー実行回数
- 成功/失敗率
- 実行時間
- エラー発生頻度

## 🚨 よくあるアンチパターン

### 1. 無限ループ

**問題:**
```javascript
// 終了条件がない
while (true) {
  await doSomething();
}
```

**解決:**
```javascript
// 最大試行回数を設定
let attempts = 0;
const maxAttempts = 10;
while (attempts < maxAttempts && !success) {
  success = await doSomething();
  attempts++;
}
```

### 2. エラーの無視

**問題:**
```javascript
try {
  await riskyOperation();
} catch (error) {
  // 何もしない
}
```

**解決:**
```javascript
try {
  await riskyOperation();
} catch (error) {
  console.error('Error:', error);
  // エラー通知
  await notifyError(error);
  // 適切な代替処理
  return fallbackValue;
}
```

### 3. 同期処理の乱用

**問題:**
```javascript
// 順次処理(遅い)
for (const item of items) {
  await processItem(item);
}
```

**解決:**
```javascript
// 並列処理(速い)
await Promise.all(
  items.map(item => processItem(item))
);
```

## 🎬 FAL API統合

### 1. `/compose`エンドポイントのペイロード形式

**推奨: `tracks`形式を使用**

FAL APIの`/compose`エンドポイントで動画を結合する際、`response_url`にGETリクエストを送信して結果を取得する場合、`tracks`形式のペイロードを使用する必要があります。

**✅ 推奨パターン（tracks形式）**:
```javascript
// ペイロード構築ノード
const videoUrls = $input.first().json.video_url || [];
const originalInput = $('When clicking \'Test workflow\'').all();

let cumulativeTime = 0;
const keyframes = videoUrls.map((url, index) => {
  const duration = originalInput[index]?.json?.duration || 5;
  const timestamp = cumulativeTime;
  cumulativeTime += duration;
  
  return {
    url: url,
    timestamp: timestamp,
    duration: duration
  };
});

const payload = {
  tracks: [{
    id: "1",
    type: "video",
    keyframes: keyframes
  }]
};

return [{ json: payload }];
```

**❌ アンチパターン（inputs形式）**:
```javascript
// inputs形式はresponse_urlにGETリクエストを送信する際に422エラーが発生
const payload = {
  inputs: videoUrls.map(url => ({ type: "video", url: url })),
  output_format: "mp4",
  concat_method: "concat"
};
```

**重要なポイント**:
- `timestamp`は累積時間を計算（前の動画の終了時点）
- `duration`は元の入力データから取得、またはデフォルト値（5秒）を使用
- `response_url`にGETリクエストを送信する際、`tracks`形式が必要

### 2. 動画URL取得のフロー

**推奨: 複数のアプローチを実装**

FAL APIから動画URLを取得する際、複数のアプローチを実装して、いずれかが成功するようにします。

**成功パターン**:
```
1. Submit to FAL → tracks形式のペイロードを送信
2. Fetch Status → ステータスをポーリング
3. Extract Video URL (Attempt 1) → ステータスレスポンスから動画URLを抽出
4. Get Result (Approach 2) → response_urlにGETリクエストを送信（tracks形式により成功）
5. Extract Video URL (Attempt 2) → レスポンスから動画URLを抽出
6. Merge Video URL → 動画URLを統合
7. Download Video → 動画をダウンロード
```

**エラーハンドリング**:
```javascript
// Get Result (Approach 2)ノードの設定
{
  "options": {
    "response": {
      "response": {
        "neverError": true  // 422エラーでも処理を続行
      }
    }
  }
}
```

### 3. タイムアウト設定

**推奨: 適切なタイムアウト値を設定**

FAL APIへのリクエストは時間がかかる場合があるため、適切なタイムアウト値を設定します。

```javascript
// Submit to FAL ノードの設定
{
  "options": {
    "timeout": 300000  // 300秒（300000ミリ秒）
  }
}
```

**アンチパターン**:
```javascript
// ❌ タイムアウトが短すぎる（300msなど）
{
  "options": {
    "timeout": 300  // 0.3秒では確実にタイムアウト
  }
}
```

## 📚 参考リソース

- [n8n公式ドキュメント](https://docs.n8n.io/)
- [n8n Community Forum](https://community.n8n.io/)
- [n8n Best Practices](https://docs.n8n.io/workflows/best-practices/)
- [WF7 Phase3 & Phase4 トラブルシューティングガイド](./knowledge/wf7-phase4-troubleshooting-guide.md)

---

最終更新: 2025-11-09
