# Verified Workflows - 検証済みワークフロー

このディレクトリには、E2Eテストを完全に通過し、本番環境での動作が確認された**検証済みワークフロー**のマイルストーンバックアップを保存します。

## 目的

- 安定稼働しているワークフローの保護
- バージョン管理による変更履歴の追跡
- 緊急時のロールバック用復元ポイント
- 将来の参照・再利用のための資産化

## 保存基準

以下の**全ての条件**を満たしたワークフローのみを保存：

1. ✅ **E2Eテスト完全通過**
   - 全テストケースが成功
   - エラーハンドリング動作確認
   - エッジケース検証済み

2. ✅ **本番環境での動作確認**
   - 最低24時間の安定稼働
   - エラー発生率 <0.1%
   - パフォーマンス基準達成

3. ✅ **ドキュメント完備**
   - README.md作成
   - 設定項目記載
   - トラブルシューティングガイド

4. ✅ **バージョンREADME作成**
   - 変更履歴
   - 検証結果
   - 依存関係
   - ロールバック手順

## ディレクトリ構造

```
verified/
├── WF5_v1.0_20251027/
│   ├── README.md              # バージョン情報・検証結果
│   ├── workflow.json          # 完全なワークフロー定義
│   └── test-results.md        # テスト結果詳細
├── WF7-Phase1_v1.0_20251101/
│   ├── README.md
│   ├── workflow.json
│   └── test-results.md
└── ...
```

## 命名規則

### ディレクトリ名
`{ワークフロー名}_v{バージョン}_{YYYYMMDD}/`

**例**:
- `WF5_v1.0_20251027/` - WF5の初回リリース
- `WF7-Phase4_v1.1_20251115/` - WF7 Phase4のマイナーアップデート
- `WF7-Phase4_v2.0_20251201/` - WF7 Phase4のメジャーアップデート

### バージョニングルール（セマンティックバージョニング簡易版）

- **v1.0**: 初回リリース（検証完了・本番稼働開始）
- **v1.1, v1.2**: マイナー更新
  - 機能追加（既存機能への影響なし）
  - バグフィックス
  - パフォーマンス改善
  - ドキュメント更新
- **v2.0, v3.0**: メジャー更新
  - ノード構成の大幅変更
  - ビジネスロジックの変更
  - 破壊的変更（既存の設定・データ形式が非互換）
  - 依存サービスの変更

## 保存手順

### Claude Code経由（推奨）

```
"WF7 Phase4を検証済みワークフローとしてv1.0で保存して"
```

実行内容:
1. ワークフロー詳細取得（n8n-mcp）
2. ディレクトリ作成: `verified/WF7-Phase4_v1.0_20251101/`
3. `workflow.json` 保存（完全なノード定義）
4. `README.md` 生成（テンプレートベース）
5. `test-results.md` 作成（テスト結果記載）

### 手動保存

1. n8n UI → 対象ワークフロー → Download
2. `verified/{ワークフロー名}_v{バージョン}_{YYYYMMDD}/` ディレクトリ作成
3. ダウンロードしたJSONを `workflow.json` として保存
4. `README.md` をテンプレートから作成（後述）
5. `test-results.md` にテスト結果を記載

## README.mdテンプレート

各verifiedディレクトリに以下のREADME.mdを作成：

````markdown
# {ワークフロー名} v{バージョン}

## Version Information

**Version**: v{Major}.{Minor}
**Release Date**: YYYY-MM-DD
**Workflow ID**: xxx
**Verification Date**: YYYY-MM-DD
**Verified By**: [担当者名]

## Changes from Previous Version

### Added
- [新機能1]
- [新機能2]

### Changed
- [変更点1]
- [変更点2]

### Fixed
- [修正1]
- [修正2]

## Verification Results

### E2E Test Results
- ✅ Test Case 1: [説明]
- ✅ Test Case 2: [説明]
- ✅ Test Case 3: [説明]

### Performance Metrics
- Response Time: XXms
- Success Rate: XX%
- Error Rate: XX%

### Production Validation
- Deploy Date: YYYY-MM-DD
- Monitoring Period: XX days
- Issues Found: [なし | リスト]

## Configuration

### Environment Variables
- VAR1: [説明]
- VAR2: [説明]

### Credentials Required
- OpenAI API Key
- Notion Integration Token
- [その他]

### Webhook Endpoints
- Production: https://xxx
- Test: https://xxx

## Dependencies

### External Services
- OpenAI GPT-4
- Notion API
- [その他]

### Other Workflows
- WF1: [依存関係の説明]
- WF2: [依存関係の説明]

## Rollback Procedure

1. [ロールバック手順ステップ1]
2. [ロールバック手順ステップ2]
3. [ロールバック手順ステップ3]

## Notes

[その他重要事項]
````

## 保持期間

**永久保持**: 全てのverifiedワークフローは削除しない

理由:
- バージョン履歴の完全な追跡
- 将来の参照・学習資料
- 緊急時の復元ポイント
- 設計パターンの資産化

## 使用例

### 最新の検証済みバージョンを確認

```bash
ls -lt verified/WF7-Phase4_*
```

### 特定バージョンの詳細確認

```bash
cat verified/WF7-Phase4_v1.0_20251101/README.md
```

### ロールバック時の復元

```bash
# 1. README確認
cat verified/WF7-Phase4_v1.0_20251101/README.md

# 2. n8n UIでインポート
# - n8n UI → Import from File
# - verified/WF7-Phase4_v1.0_20251101/workflow.json を選択
# - 認証情報設定
# - テスト実行
```

## 関連ドキュメント

- [バックアップポリシー](../../docs/workflow-backup-policy.md)
- [ワークフロー構築ナレッジ](../../docs/knowledge/n8n-workflow-construction-knowledge.md)

---

最終更新: 2025-11-01
