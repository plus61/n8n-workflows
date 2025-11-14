# WF7 Phase4a Execute Workflow修正後統合テスト結果

**作成日時**: 2025-11-13 18:39:28 JST

## テスト概要

Phase4aのExecute WorkflowノードがランタイムでPhase4c (mfRdJJFJRKmeBjKv) を呼び出していた問題を修正し、正しいPhase4b FIXED (hfhZijyKIt1DjI1V) を呼び出すよう強制更新を実施。修正後の統合テストを実行し、ワークフロー実行チェーンが正常に動作することを検証した。

## 問題の詳細

### 発見された問題

**Execute Workflowノードの構成不整合**:
- **データベース設定**: `workflowId: "hfhZijyKIt1DjI1V"` (正しいPhase4b FIXED)
- **ランタイム実行**: `workflowId: "mfRdJJFJRKmeBjKv"` (誤り - Phase4c)

**エラー症状**:
- execution 1967: `status: "error"`, `finished: false`
- エラーメッセージ: "Missing node to start execution"
- 原因: Phase4cはWebhook triggerを持ち、Execute Workflow Triggerを持たない

### 根本原因

前回の構成更新が完全に永続化されなかった、またはn8nサーバーが古い構成をキャッシュしていた。データベースには正しいIDが保存されていたが、ランタイム実行時に古いキャッシュが使用された。

**証拠**:
- `n8n_get_workflow`で取得: `"value": "hfhZijyKIt1DjI1V"` ✅
- execution 1967エラーデータ: `"value": "mfRdJJFJRKmeBjKv"` ❌
- Phase4aメタデータ: versionCounter: 129, updatedAt: "2025-11-13T09:09:59.261Z"

## 解決策

### 実施した修正

**n8n_update_partial_workflowによる強制更新**:

```javascript
{
  "type": "updateNode",
  "nodeId": "execute-phase4b",
  "updates": {
    "parameters": {
      "source": "database",
      "workflowId": {
        "__rl": true,
        "mode": "id",
        "value": "hfhZijyKIt1DjI1V"
      },
      "mode": "each"
    }
  }
}
```

**更新結果**:
- ✅ 更新成功: "Applied 1 operations"
- ✅ versionCounter: 129 → 131
- ✅ updatedAt: "2025-11-13T09:24:00.035Z"

### 代替手段を試行した経緯

**失敗した試み**:
`n8n_update_full_workflow`でactive: falseを設定しようとしたが、以下のエラー:
```
Invalid request: request/body must have required property 'nodes'
```

**理由**: full updateは完全なワークフロー定義（全ノード配列を含む）を要求する。

**成功した手法**: `n8n_update_partial_workflow`を使用して特定ノードのパラメータのみを外科的に更新。

## 検証結果

### Phase4a実行（親ワークフロー）

**execution 1978** (修正後):
- ✅ status: "success"
- ✅ finished: true
- ✅ 開始: 2025-11-13T09:35:19.171Z
- ✅ 終了: 2025-11-13T09:36:12.581Z
- ✅ 実行時間: 53.41秒
- ✅ 出力: 7アイテム（7枚のスライドメタデータ）

**比較（問題解決の証拠）**:
| Execution | Status | WorkflowId Used | Result |
|-----------|--------|-----------------|---------|
| 1967 (修正前) | error | mfRdJJFJRKmeBjKv (Phase4c) | ❌ Missing node to start execution |
| 1978 (修正後) | success | hfhZijyKIt1DjI1V (Phase4b FIXED) | ✅ 7つの子実行成功 |

### Phase4b子実行（個別動画生成）

**7つの子実行すべて成功**:

| Execution ID | 開始時刻 | 終了時刻 | Status | WorkflowId | Mode |
|--------------|----------|----------|--------|------------|------|
| 1979 | 09:35:22 | 09:35:29 | success | hfhZijyKIt1DjI1V | integrated |
| 1980 | 09:35:29 | 09:35:36 | success | hfhZijyKIt1DjI1V | integrated |
| 1981 | 09:35:36 | 09:35:44 | success | hfhZijyKIt1DjI1V | integrated |
| 1982 | 09:35:44 | 09:35:51 | success | hfhZijyKIt1DjI1V | integrated |
| 1983 | 09:35:51 | 09:35:58 | success | hfhZijyKIt1DjI1V | integrated |
| 1984 | 09:35:58 | 09:36:05 | success | hfhZijyKIt1DjI1V | integrated |
| 1985 | 09:36:05 | 09:36:12 | success | hfhZijyKIt1DjI1V | integrated |

**重要な観察**:
- すべて `mode: "integrated"` → Execute Workflowノード経由で呼び出された証拠
- 各実行が約7秒間実行（FAL API処理時間）
- 順次実行パターン（mode: "each"の動作確認）

### ランタイム構成検証

**execution 1978の詳細（filtered mode）**:

```json
{
  "metadata": {
    "subExecution": {
      "executionId": "1979",
      "workflowId": "hfhZijyKIt1DjI1V"
    }
  }
}
```

**確認事項**:
- ✅ ランタイムで正しいworkflowId: `hfhZijyKIt1DjI1V`を使用
- ✅ 各アイテムにsubExecution metadataが含まれる
- ✅ すべての子実行が正しいワークフローIDで実行された

### Phase4b出力データ

**各Phase4b実行の出力例**:

```json
{
  "section": "hook",
  "duration": 3,
  "video_url": "https://v3b.fal.media/files/b/panda/3eB6aQZgK8H5DO4jZD8HM_output.mp4",
  "fal_request_id": "f049c30b-7b19-4d32-a5e9-f223ab843e5c",
  "motion_prompt": "dramatic zoom in effect, professional business style, sharp focus",
  "filename": "video_hook.mp4",
  "text": "フックテキストがありません"
}
```

**検証結果**:
- ✅ 各実行がFAL APIから動画URLを正常に取得
- ✅ FAL request IDが記録されている（トレーサビリティ確保）
- ✅ セクション情報、duration、motion_promptすべて正常
- ⚠️ textフィールドにフォールバックテキスト使用（別の問題）

## 残る課題

### フォールバックテキスト問題

**症状**:
すべてのスライドで実際のsubtitleではなく、フォールバックテキストが使用されている：
- "フックテキストがありません"
- "導入テキストがありません"
- "ポイント1がありません"
- 等

**根本原因**（既存レポートより）:

**Phase1の出力**:
- 実際のセグメント数: 5
- 構造: 自由形式（セクションタイプ指定なし）

**Phase4aの期待**:
- 期待セグメント数: 7固定
- コードロジック: `if len(segments) >= 7:`
- 条件がFalseのためフォールバック分岐が実行される

**Phase4aコード該当部分**:
```python
if len(segments) >= 7:
    texts['hook'] = segments[0].get('subtitle', 'フックテキストがありません')
    texts['intro'] = segments[1].get('subtitle', '導入テキストがありません')
    # ... segments[0] through segments[6]
else:
    # フォールバック: デフォルトテキストを使用
    texts = {
        'hook': 'フックテキストがありません',
        'intro': '導入テキストがありません',
        # ...
    }
```

**ステータス**:
- ❌ 未解決（本セッションの対象外）
- 📋 別途対応が必要
- 📄 詳細は`now/2025-01-13_15-27_WF7-Phase1-Phase4a-データ構造不整合レポート.md`参照

### 推奨される対応策

**Option 1: Phase1を修正**（推奨）:
- GPT-4o-miniプロンプトで7セグメント固定を指示
- Phase4aコードの変更不要
- Phase1-Phase4a間のデータ契約を明確化

**Option 2: Phase4aを修正**:
- 可変セグメント数に対応するよう実装
- Phase1の柔軟性を維持
- コード複雑度が増加

## テスト実行情報

### Webhook呼び出し

```bash
curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator" \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2aa68d5c-2986-81b0-b488-e2d7ee8026b7"}'
```

**レスポンス**:
- HTTP Status: 200 OK
- 実行時間: 4.30秒
- 出力: 7枚のスライドメタデータ（Cloudinary URLs含む）

### 関連実行ID

**Phase4a (LYPbvJfkMzLlhc6t)**:
- execution 1967: エラー（修正前）
- execution 1978: 成功（修正後）← 本検証対象

**Phase4b FIXED (hfhZijyKIt1DjI1V)**:
- executions 1979-1985: すべて成功（子実行）

**テストデータ**:
- Notion Script ID: `2aa68d5c-2986-81b0-b488-e2d7ee8026b7`
- 同一台本データで複数回テスト実行

## まとめ

### ✅ 解決した問題

1. **Execute Workflowノードの構成永続化問題**
   - データベース設定とランタイム実行の乖離を解決
   - n8n_update_partial_workflowによる強制更新で修正
   - versionCounter増加で永続化を確認

2. **Phase4a→Phase4b実行チェーン**
   - Execute Workflowノードが正しいワークフローを呼び出すよう修正
   - 7つの子実行すべて成功
   - 各子実行が個別のFAL動画を生成

3. **ワークフロー実行の安定性**
   - execution 1978: status "success", finished true
   - エラーレート: 0/7 (100%成功)

### ⚠️ 既知の未解決問題

1. **Phase1-Phase4a セグメント数不一致**
   - Phase1: 5セグメント生成
   - Phase4a: 7セグメント期待
   - 影響: すべてのスライドでフォールバックテキスト使用
   - 優先度: 高（別途対応が必要）

### 📊 パフォーマンス指標

- **Phase4a実行時間**: 53.41秒（7枚スライド生成）
- **Phase4b平均実行時間**: 約7秒/動画
- **合計実行時間**: 約53秒（並行処理なしの順次実行）
- **成功率**: 7/7 (100%)

## 次のステップ

### 即座の対応

1. ✅ Execute Workflowノード修正完了
2. ✅ 統合テスト実行完了
3. ✅ 検証完了
4. ✅ ドキュメント作成完了

### 今後の対応

1. **Phase1台本生成の修正**
   - 7セグメント固定生成に変更
   - セクションタイプ（hook/intro/point1-3/summary/cta）を明示的に指定
   - GPT-4o-miniプロンプトの調整

2. **Phase4a再テスト**
   - Phase1修正後、実際のsubtitleテキストが使用されることを確認
   - フォールバックテキストが表示されないことを検証

3. **Phase4c統合**
   - Phase4b出力（7つの動画URL）をPhase4cで結合
   - 完全なWF7パイプライン（Phase1→Phase2→Phase4a→Phase4b→Phase4c）のE2Eテスト

## 参考情報

### ワークフローID

- **Phase4a**: LYPbvJfkMzLlhc6t (Webhook trigger)
- **Phase4b FIXED**: hfhZijyKIt1DjI1V (Execute Workflow Trigger)
- **Phase4c**: mfRdJJFJRKmeBjKv (Webhook trigger - Execute Workflowと互換性なし)

### 関連ドキュメント

- `now/2025-01-13_15-27_WF7-Phase1-Phase4a-データ構造不整合レポート.md`
- `workflows/wf7-phase4b-single-video-generator-FIXED.json`

### Railway環境

- **n8n URL**: https://n8n-python-production-344b.up.railway.app
- **Phase4a Webhook**: /webhook/wf7-phase4a-slide-generator
- **デプロイ環境**: Production
- **稼働状況**: 正常

## 結論

Execute Workflowノードの構成永続化問題は**完全に解決**されました。n8n_update_partial_workflowによる強制更新により、ランタイムでも正しいworkflowId (`hfhZijyKIt1DjI1V`) が使用されることを確認しました。

Phase4a→Phase4b実行チェーンは正常に動作しており、7つの子実行すべてが成功し、各実行が個別のFAL動画を生成しています。

残るフォールバックテキスト問題は、Phase1-Phase4a間のデータ構造不一致に起因する別の問題であり、Phase1の修正が必要です。この問題は既に詳細レポートで文書化されており、今後の対応タスクとして記録されています。
