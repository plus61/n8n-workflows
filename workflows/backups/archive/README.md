# Archive - 廃止・非アクティブワークフロー

このディレクトリには、運用を終了した、または非アクティブ化されたワークフローを保存します。

## 目的

- 廃止ワークフローの履歴保持
- 将来の再利用可能性の確保
- 過去の設計パターンの学習資料
- 監査・コンプライアンス対応

## 保存対象

以下のいずれかに該当するワークフロー：

1. 🗄️ **廃止ワークフロー**
   - ビジネス要件の変更により不要になった
   - 新しいワークフローに置き換えられた
   - サービス終了により動作不可能

2. 🗄️ **長期非アクティブワークフロー**
   - 3ヶ月以上非アクティブ状態
   - 再利用の予定なし
   - メンテナンス対象外

3. 🗄️ **実験的ワークフロー**
   - PoC（概念実証）用
   - A/Bテスト終了後
   - 採用されなかった代替案

## ディレクトリ構造

```
archive/
├── deprecated_20251101/
│   ├── README.md                    # アーカイブ理由・概要
│   ├── WF3_OldWorkflow.json         # 廃止ワークフローJSON
│   ├── WF8_ExperimentalFlow.json
│   └── ...
├── deprecated_20251201/
└── ...
```

## 命名規則

### ディレクトリ名
`deprecated_{YYYYMMDD}/`

**例**:
- `deprecated_20251101/` - 2025年11月1日にアーカイブ
- `deprecated_20251231/` - 2025年12月31日にアーカイブ

### 保存タイミング
- 四半期末: 各四半期最終営業日
- 非アクティブ化時: ワークフロー停止時即座
- 年次整理: 毎年12月31日

## 保存手順

### Claude Code経由（推奨）

```
"WF3を廃止ワークフローとしてアーカイブして"
```

実行内容:
1. ワークフロー詳細取得（n8n-mcp）
2. 最新の `deprecated_YYYYMMDD/` 確認（なければ作成）
3. `WF3_WorkflowName.json` として保存
4. アーカイブREADME.md更新（廃止理由追記）

### 手動保存

1. n8n UI → 対象ワークフロー → Download
2. 最新の `deprecated_YYYYMMDD/` ディレクトリに保存
3. README.md更新（後述）
4. n8nで非アクティブ化 or 削除

## README.mdテンプレート

各archivedディレクトリに以下のREADME.mdを作成：

````markdown
# Archived Workflows - YYYY-MM-DD

## Archive Summary

**Archive Date**: YYYY-MM-DD
**Total Archived Workflows**: XX
**Reason**: [定期整理 | サービス終了 | 置き換え]

## Archived Workflow List

### 1. WF3_OldWorkflow.json
- **Workflow ID**: xxx
- **Archive Reason**: 新しいWF10に置き換え
- **Last Active Date**: YYYY-MM-DD
- **Original Purpose**: [元の目的]
- **Replacement**: WF10（より効率的な実装）

### 2. WF8_ExperimentalFlow.json
- **Workflow ID**: xxx
- **Archive Reason**: PoC終了・本番採用見送り
- **Last Active Date**: YYYY-MM-DD
- **Original Purpose**: A/Bテスト用代替実装
- **Outcome**: 既存フローの方が高パフォーマンス

[... 他のワークフロー ...]

## Retention Policy

**保持期間**: 1年間（アーカイブ日から）
**削除予定日**: YYYY-MM-DD
**延長条件**: 監査要件、法的要件、再利用可能性

## Retrieval Instructions

アーカイブワークフローを復元する場合:

1. README確認（目的・廃止理由）
2. n8n UI → Import from File
3. 対象JSONファイル選択
4. 認証情報再設定（期限切れの可能性）
5. テスト実行（依存サービス変更の可能性）

**注意**:
- 依存サービスが終了している可能性
- 認証情報が無効化されている可能性
- n8nバージョン互換性の確認が必要

## Notes

[その他重要事項・特記事項]
````

## 保持期間管理

### 保持期間
**1年間**: アーカイブ日から1年間保持

### 削除判断基準
1年経過後、以下を確認して削除判断：

- ✅ **削除可能**: 監査要件なし、再利用可能性なし
- ⚠️ **延長検討**: 監査要件あり、法的要件あり
- 🔄 **復活**: 再利用が決定、要件が復活

### 定期レビュー
- 四半期ごと: アーカイブワークフロー一覧確認
- 年次: 削除対象の最終確認と実行

## 使用例

### 最近のアーカイブ確認

```bash
ls -lt archive/
cat archive/deprecated_20251101/README.md
```

### 特定ワークフロー検索

```bash
grep -r "WF3" archive/*/README.md
```

### 復元手順

```bash
# 1. README確認
cat archive/deprecated_20251101/README.md

# 2. n8n UIでインポート
# - n8n UI → Import from File
# - archive/deprecated_20251101/WF3_OldWorkflow.json 選択

# 3. 認証情報再設定
# - 各種API Key確認
# - 有効期限確認

# 4. 依存関係確認
# - 外部サービス稼働状況
# - 他ワークフロー依存関係

# 5. テスト実行
```

## 関連ドキュメント

- [バックアップポリシー](../../docs/workflow-backup-policy.md)
- [ワークフロー構築ナレッジ](../../docs/knowledge/n8n-workflow-construction-knowledge.md)

---

最終更新: 2025-11-01
