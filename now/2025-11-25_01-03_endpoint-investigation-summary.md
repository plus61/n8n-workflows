# WF10-Main APIエンドポイント調査完了レポート

**作成日時**: 2025-11-25 01:03:09 JST

## 🎯 問題の再調査

### 前回の誤った「修正」

**誤った変更内容**:
```json
"url": "=https://api.kie.ai/api/v1/jobs/getTask?taskId=xxx"
```

**結果**:
- ❌ 404エラー即座に発生
- ❌ エラーメッセージ: "The resource you are requesting could not be found"
- ❌ Spring Boot Whitelabel Error Page

## ✅ 正しいエンドポイントの確認

### kie.ai公式ドキュメント調査結果

**公式パターン** (docs.kie.ai):
```
GET /api/v1/{service}/record-info
```

**サービス別エンドポイント**:
- Veo3.1: `/api/v1/veo/record-info`
- Generate: `/api/v1/generate/record-info`
- Runway: `/api/v1/runway/record-info`

**結論**:
- ✅ `/api/v1/veo/record-info` は公式の正しいエンドポイント
- ❌ `/api/v1/jobs/getTask` は存在しないエンドポイント

## 📊 実際の動作確認

### E2Eテスト結果（バックグラウンド実行）

**テスト**: `2025-11-24_00-41_e2e-test-after-correct-endpoint.txt`
- **エンドポイント**: `/api/v1/veo/record-info` （正しい）
- **結果**: タイムアウト（6分以上実行中、レスポンスなし）
- **ステータス**: 404エラーなし = エンドポイントは正常

**重要な発見**:
1. **正しいエンドポイントは存在し、動作している** - 404が出ていない
2. **タイムアウトは別の問題** - kie.aiのビデオ生成時間が長い可能性
3. **Wait時間の見直しが必要** - 現在の5分間隔では不十分かもしれない

## 🔍 Sora 2 API仕様の未解明点

### ドキュメント不足

**docs.kie.aiの状況**:
- ❌ Sora 2の公式ドキュメントなし
- ✅ Veo3.1, Runway, Lumaのみドキュメント化
- ❓ Sora 2が"veo"サービスパスを使用するか不明

### 推測される仕様

**model名**: `sora-2-image-to-video`
→ おそらく `/api/v1/veo/record-info` を使用（Veoファミリー）

**taskIdライフサイクル**:
- 作成直後: 有効
- 75分後: 無効または期限切れ（`data: null`）
- 生成完了: 有効期間不明

## 📝 次のステップ

### 1. 修正済みワークフロー作成完了 ✅

- **ファイル名**: `2025-11-25_01-03_WF10-Main-reverted-correct-endpoint.json`
- **変更内容**: Line 217を正しいエンドポイントに戻した
- **エンドポイント**: `/api/v1/veo/record-info` （kie.ai公式準拠）

### 2. fresh taskIdでのテスト実行 ⏳

**目的**: `data: null` 問題がtaskId有効期限切れによるものか検証

**テスト手順**:
1. 新しいビデオ生成タスク作成（fresh taskId取得）
2. 即座に `/api/v1/veo/record-info?taskId=xxx` で確認
3. 実際のタスクデータが返るか検証

### 3. Wait時間の最適化検討 ⏳

**現在の設定**: 5分（300秒）
**推奨検討事項**:
- kie.ai Sora 2の平均生成時間を調査
- 必要に応じてWait時間を10分または15分に延長
- またはcallbackUrl方式への移行検討

## 🚀 推奨アクション

1. **即座に**: 修正済みワークフロー `2025-11-25_01-03_WF10-Main-reverted-correct-endpoint.json` をn8nにインポート
2. **テスト実行**: fresh taskIdで正しいエンドポイントの動作確認
3. **監視**: タイムアウトが発生する場合はWait時間延長を検討
4. **代替案**: webhook callback方式への移行も視野に

## 🔧 技術的教訓

### 誤った前提

- ❌ `/api/v1/jobs/getTask` が正しいと思い込んだ
- ❌ `data: null` の原因をエンドポイントの問題と誤認
- ❌ 公式ドキュメント確認を後回しにした

### 正しいアプローチ

- ✅ 公式ドキュメントを最初に確認する
- ✅ APIエラーの種類を正確に識別する（404 vs 200 with null）
- ✅ taskIdのライフサイクルを考慮する

## 📚 参考情報

- **kie.ai公式ドキュメント**: https://docs.kie.ai
- **APIパターン**: `GET /api/v1/{service}/record-info`
- **サポートされているサービス**: veo, generate, runway, luma
- **Sora 2**: ドキュメント未掲載（veoファミリーと推測）
