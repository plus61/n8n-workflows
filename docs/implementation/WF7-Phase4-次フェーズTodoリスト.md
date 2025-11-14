# WF7 Phase4 次フェーズTodoリスト

**作成日**: 2025-11-12
**前フェーズ**: Phase4b MVP技術検証完了
**現在のステータス**: 次フェーズ計画策定完了

---

## 🎯 即時対応タスク（今日中）

### 1. Phase4c Webhookエンドポイント存在確認
- **優先度**: 🔴 最高
- **所要時間**: 5分
- **担当**: AI Assistant
- **実施内容**:
  ```bash
  curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-ffmpeg-concat" \
    -H "Content-Type: application/json" \
    -d '{"test": "ping"}'
  ```
- **成功基準**: HTTP 200/400応答（404以外ならエンドポイント存在）
- **失敗時対応**: Phase4c実装状況確認、未実装ならPhase4c先行実装

### 2. Phase4c入力データ契約ドキュメント確認
- **優先度**: 🔴 最高
- **所要時間**: 10分
- **担当**: AI Assistant
- **実施内容**:
  - `docs/implementation/` 配下のPhase4c設計書検索
  - Phase4c Webhookノード設定確認
  - 入力パラメータ仕様ドキュメント化
- **成功基準**: Phase4c必須パラメータリスト取得
- **必要情報**:
  - `script_id`: 必須/オプション
  - `cloudinary_batch_id`: 必須/オプション
  - `cloudinary_public_id`: 必須/オプション
  - その他のパラメータ

### 3. 親ワークフローr9Sp5n0mkUCcH8cwの現在の構成取得
- **優先度**: 🔴 最高
- **所要時間**: 5分
- **担当**: AI Assistant
- **実施内容**:
  ```javascript
  mcp_n8n-mcp_n8n_get_workflow({id: "r9Sp5n0mkUCcH8cw"})
  ```
- **成功基準**: 親ワークフローJSON取得、Phase4a/4b呼び出し箇所特定
- **確認項目**:
  - 現在のPhase4b呼び出しノードID
  - エラーハンドリングIF構造
  - Notion更新ノード位置

---

## 📅 短期対応タスク（1週間以内）

### Week 1 Day 1-2: Phase4c統合設計

#### 4. Phase4b→Phase4cデータフロー設計
- **優先度**: 🟡 高
- **所要時間**: 2時間
- **担当**: AI Assistant + User
- **実施内容**:
  - Phase4bレスポンス形式確認
  - Phase4c入力要求確認
  - データ変換ロジック設計
- **成果物**: データマッピング仕様書
- **データフロー例**:
  ```json
  Phase4b出力:
  {
    "success": true,
    "cloudinary_batch_id": "...",
    "cloudinary_public_id": "...",
    "slides_count": 7
  }

  Phase4c入力（想定）:
  {
    "script_id": "...",
    "video_clips": [
      {"url": "cloudinary://...", "duration": 80}
    ]
  }
  ```

#### 5. Phase4c統合実装（Set + HTTP Requestノード）
- **優先度**: 🟡 高
- **所要時間**: 1時間
- **担当**: AI Assistant
- **実施内容**:
  1. Phase4b成功時の出力を受け取るSetノード作成
  2. Phase4cペイロード構築
  3. HTTP Requestノード作成（Phase4c呼び出し）
  4. onError設定: `continueErrorOutput`
- **成果物**: 新ノード2個追加完了
- **検証**: 単体curlテスト

#### 6. Phase4c統合テスト
- **優先度**: 🟡 高
- **所要時間**: 30分
- **担当**: AI Assistant
- **実施内容**:
  - Phase4b MVP結果を使用してPhase4c手動呼び出し
  - エラーレスポンス確認
  - タイムアウト設定確認（180秒）
- **成功基準**: Phase4c正常応答確認

### Week 1 Day 3-4: 親ワークフロー更新

#### 7. 親ワークフローHTTP RequestノードをyyR10x16t0OdhIjGに更新
- **優先度**: 🟡 高
- **所要時間**: 15分
- **担当**: AI Assistant
- **実施内容**:
  ```javascript
  mcp_n8n-mcp_n8n_update_partial_workflow({
    id: "r9Sp5n0mkUCcH8cw",
    operations: [{
      type: "updateNode",
      nodeId: "<phase4b-http-request-node-id>",
      updates: {
        parameters: {
          url: "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video"
        }
      }
    }]
  })
  ```
- **注意**: 新ワークフローID `yyR10x16t0OdhIjG` のWebhook pathは同じ
- **検証**: 親フローからのPhase4b呼び出し確認

#### 8. Phase4c呼び出しノード追加
- **優先度**: 🟡 高
- **所要時間**: 30分
- **担当**: AI Assistant
- **実施内容**:
  1. Phase4b成功IF後に新ノード追加
  2. HTTP Request - Call Phase4c作成
  3. Set - Phase4c Payload作成
  4. 接続更新: Phase4b Success → Set → HTTP Request
- **成果物**: 親ワークフローに2ノード追加

#### 9. 統合エラーハンドリングIF実装
- **優先度**: 🟡 高
- **所要時間**: 45分
- **担当**: AI Assistant
- **実施内容**:
  - 現在のPhase4a/4b IFノード確認
  - Phase4c Success CheckのIF追加
  - エラー時の統合処理（Notion更新）
  - 成功時のGoogle Drive → Notion更新フロー
- **フロー**:
  ```
  IF - Phase4b Success
    ├─ [true] → HTTP Request - Call Phase4c
    │              ↓
    │         IF - Phase4c Success
    │              ├─ [true] → Google Drive Upload → Notion更新
    │              └─ [false] → エラー時Notion更新
    └─ [false] → エラー時Notion更新
  ```

### Week 1 Day 5: 統合テスト

#### 10. Phase4a→4b→4c統合テスト
- **優先度**: 🟡 高
- **所要時間**: 1時間
- **担当**: AI Assistant + User
- **実施内容**:
  - 親ワークフローのWebhookを手動トリガー
  - Notion実データを使用
  - 各フェーズの成功/失敗を監視
- **成功基準**: 最終動画URLがNotion更新される
- **監視項目**:
  - Phase4a: スライド生成成功
  - Phase4b: Cloudinary batch_id取得
  - Phase4c: FFmpeg連結成功
  - Google Drive: 最終動画アップロード成功
  - Notion: Video URL更新成功

---

## 📊 中期対応タスク（2週間以内）

### Week 2 Day 1-2: E2Eテスト

#### 11. 最小構成テスト（1枚スライド + 音声なし）
- **優先度**: 🟢 中
- **所要時間**: 30分
- **テストデータ**:
  ```json
  {
    "script_id": "test-minimal",
    "slides_metadata": [{"section": "hook", "image_url": "...", "duration": 3}]
  }
  ```
- **成功基準**: 3秒動画生成成功

#### 12. 標準構成テスト（7枚スライド + 音声あり）
- **優先度**: 🟢 中
- **所要時間**: 30分
- **テストデータ**: Phase4a実データ使用
- **成功基準**: 80秒動画生成、音声同期確認

#### 13. エッジケーステスト
- **優先度**: 🟢 中
- **所要時間**: 1時間
- **テストケース**:
  1. 長時間スライド（duration: 30秒）
  2. 大量テキストスライド（文字数上限テスト）
  3. 無効なimage_url
  4. Cloudinary API障害シミュレーション
- **成功基準**: 適切なエラーメッセージ返却

### Week 2 Day 3-4: パフォーマンス測定

#### 14. 各フェーズ処理時間計測
- **優先度**: 🟢 中
- **所要時間**: 2時間
- **計測項目**:
  - Phase4a: スライド生成時間（目標: <30秒）
  - Phase4b: Cloudinary応答時間（目標: <60秒）
  - Phase4c: FFmpeg連結時間（目標: <50秒）
  - 合計: E2E時間（目標: <140秒）
- **計測方法**: n8nワークフロー実行履歴から各ノード実行時間取得

#### 15. 旧FAL.ai実装との比較分析
- **優先度**: 🟢 中
- **所要時間**: 1時間
- **比較項目**:
  - API呼び出し回数（FAL: 7回 vs Cloudinary: 1回）
  - 処理時間（FAL: ~140秒 vs Cloudinary: ~60-80秒）
  - エラー率
  - コスト（API使用料）
- **成果物**: パフォーマンス比較レポート

#### 16. Railwayリソース使用量分析
- **優先度**: 🔵 低
- **所要時間**: 30分
- **確認項目**:
  - CPU/メモリ使用率
  - 無料枠残量
  - 月間予測コスト
- **成果物**: リソース使用レポート

### Week 2 Day 5: ドキュメント整備

#### 17. 技術設計書更新
- **優先度**: 🔵 低
- **所要時間**: 1時間
- **更新内容**:
  - Phase4b/4c詳細設計書
  - データ契約仕様書
  - API統合パターン図

#### 18. 運用ガイド作成
- **優先度**: 🔵 低
- **所要時間**: 1時間
- **内容**:
  - トラブルシューティング手順
  - エラーコード一覧
  - 監視ポイント
  - ロールバック手順

#### 19. テストレポート作成
- **優先度**: 🔵 低
- **所要時間**: 30分
- **内容**:
  - E2Eテスト結果サマリー
  - パフォーマンス測定結果
  - 既知の制限事項
  - 今後の改善提案

---

## 📋 チェックリスト

### Phase4c統合準備
- [ ] Phase4c Webhookエンドポイント存在確認
- [ ] Phase4c入力データ契約確認
- [ ] 親ワークフロー現在構成取得
- [ ] Phase4b→4cデータフロー設計完了

### Phase4c統合実装
- [ ] Phase4c統合ノード実装（Set + HTTP Request）
- [ ] Phase4c単体テスト成功
- [ ] 親ワークフローPhase4b呼び出し更新
- [ ] Phase4c呼び出しノード追加
- [ ] 統合エラーハンドリングIF実装

### テスト
- [ ] 統合テスト実行（Phase4a→4b→4c）
- [ ] 最小構成テスト
- [ ] 標準構成テスト
- [ ] エッジケーステスト
- [ ] パフォーマンス測定完了

### ドキュメント
- [ ] 技術設計書更新
- [ ] 運用ガイド作成
- [ ] テストレポート作成
- [ ] パフォーマンス比較レポート作成

---

## 🚨 ブロッカーと依存関係

### ブロッカー
1. **Phase4c未実装**: Phase4c FFmpegワークフローが存在しない場合
   - **対応**: Phase4c先行実装またはPhase4b単体での価値提供

2. **Cloudinary API制限**: 無料枠超過
   - **対応**: 有料プラン検討またはテストデータ削減

3. **Railwayリソース不足**: CPU/メモリ使用率>80%
   - **対応**: Railway有料プラン検討または処理の最適化

### 依存関係
- **Phase4c統合**: Phase4cワークフロー実装完了が前提
- **親ワークフロー更新**: Phase4b/4c統合完了が前提
- **E2Eテスト**: 親ワークフロー更新完了が前提
- **パフォーマンス測定**: E2Eテスト成功が前提

---

## 📊 進捗トラッキング

| フェーズ | 進捗率 | 完了日 | ステータス |
|---------|-------|--------|-----------|
| Phase4b MVP検証 | 100% | 2025-11-12 | ✅ 完了 |
| Phase4c統合準備 | 0% | - | 📋 計画中 |
| Phase4c統合実装 | 0% | - | 📋 計画中 |
| 親ワークフロー更新 | 0% | - | 📋 計画中 |
| E2Eテスト | 0% | - | 📋 計画中 |
| パフォーマンス測定 | 0% | - | 📋 計画中 |
| ドキュメント整備 | 0% | - | 📋 計画中 |

---

**作成者**: AI Assistant
**最終更新**: 2025-11-12
**次回更新**: Phase4c統合準備完了時
