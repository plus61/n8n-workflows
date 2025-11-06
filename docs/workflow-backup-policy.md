# n8n ワークフロー バックアップポリシー

## 基本方針

**検証完了し完成したワークフローは必ずバックアップを取得する**

このポリシーは、安定稼働しているワークフローの保護と、変更履歴の管理を目的としています。

---

## バックアップ取得タイミング

### 必須バックアップ（MUST）

以下のタイミングでは**必ず**バックアップを取得してください：

1. ✅ **検証完了時**
   - E2Eテストが全て通過
   - 本番環境で正常動作を確認
   - ドキュメント作成完了

2. ✅ **本番デプロイ直前**
   - アクティブ化する前の最終状態を保存
   - ロールバック用の安全な復元ポイント確保

3. ✅ **重要な変更前**
   - ノード構成の大幅な変更
   - ビジネスロジックの修正
   - 認証情報や接続先の変更

4. ✅ **定期バックアップ**
   - 週次: 毎週金曜日 18:00
   - 月次: 毎月末日 18:00
   - 四半期末: 各四半期最終営業日 18:00

### 推奨バックアップ（SHOULD）

5. 🔵 **マイナー修正後**
   - エラーハンドリングの改善
   - ログ出力の調整
   - パフォーマンス最適化

6. 🔵 **実験的機能追加後**
   - A/Bテスト用の分岐追加
   - 新しいAPIエンドポイント連携
   - 試験的な自動化処理

---

## バックアップディレクトリ構成

```
workflows/backups/
├── YYYYMMDD_HHMMSS/           # タイムスタンプディレクトリ
│   ├── README.md              # バックアップサマリー
│   ├── WF1_WorkflowName.json  # ワークフローメタデータ
│   ├── WF2_WorkflowName.json
│   └── ...
├── verified/                  # 検証済みワークフロー（マイルストーン）
│   ├── WF5_v1.0_20251027/    # バージョン管理
│   ├── WF7-Phase1_v1.0_20251101/
│   └── ...
└── archive/                   # 廃止・非アクティブワークフロー
    ├── deprecated_20251001/
    └── ...
```

### ディレクトリルール

#### `backups/YYYYMMDD_HHMMSS/`
- **用途**: 日次・定期バックアップ、作業前バックアップ
- **保持期間**: 30日間（月次バックアップは永久保持）
- **形式**: タイムスタンプディレクトリ + README.md + JSON群

#### `backups/verified/`
- **用途**: 検証完了したマイルストーンワークフロー
- **保持期間**: 永久保持
- **命名規則**: `{ワークフロー名}_v{バージョン}_{YYYYMMDD}/`
- **バージョン管理**: セマンティックバージョニング準拠
  - `v1.0`: 初回リリース
  - `v1.1`: マイナー機能追加
  - `v2.0`: メジャー変更・破壊的変更

#### `backups/archive/`
- **用途**: 廃止・非アクティブ化されたワークフロー
- **保持期間**: 1年間（その後削除可能）
- **移動タイミング**: ワークフロー削除・非アクティブ化時

---

## バックアップ手順

### 自動バックアップ（推奨）

#### 1. 全アクティブワークフローのバックアップ

```bash
# n8n-mcp経由で全アクティブワークフローを取得しバックアップ
# Claude Codeで実行:
# "現在アクティブなワークフローを全てバックアップして"
```

**実行内容**:
1. `n8n_list_workflows(active: true)` で全アクティブワークフロー取得
2. タイムスタンプディレクトリ作成
3. 各ワークフローの詳細を並列取得
4. JSON形式でメタデータ保存
5. README.md生成（バックアップサマリー）

#### 2. 検証済みワークフローの保存

```bash
# 検証完了ワークフローをverifiedディレクトリに保存
# Claude Codeで実行:
# "WF7 Phase4を検証済みワークフローとしてv1.0で保存して"
```

**実行内容**:
1. ワークフロー詳細取得
2. `verified/{ワークフロー名}_v{バージョン}_{YYYYMMDD}/` ディレクトリ作成
3. 完全なワークフローJSON保存
4. バージョンREADME.md生成（検証結果・変更履歴記載）

### 手動バックアップ（緊急時）

#### n8nエクスポート経由

1. n8n UI → 対象ワークフロー選択
2. 右上「…」メニュー → "Download"
3. `workflows/backups/manual/` に保存
4. ファイル名を `{ワークフロー名}_{YYYYMMDD}.json` にリネーム

---

## バックアップ検証

### 取得直後の検証

バックアップ取得後、以下を確認：

1. ✅ **ファイル存在確認**
   ```bash
   ls -la workflows/backups/YYYYMMDD_HHMMSS/
   ```

2. ✅ **JSON妥当性チェック**
   ```bash
   # JSONパースエラーがないか確認
   cat WF1_WorkflowName.json | jq .
   ```

3. ✅ **メタデータ確認**
   - ワークフローID存在
   - 名前・ノード数・更新日時が正しい
   - Webhook情報（該当する場合）

4. ✅ **README.md生成確認**
   - バックアップサマリー記載
   - 全ワークフロー一覧
   - 次ステップ記載

### 定期検証（月次）

月次バックアップ時に以下を実施：

1. 🔍 **バックアップ復元テスト**
   - テスト環境にインポート
   - 基本動作確認
   - 復元手順ドキュメント更新

2. 🔍 **ストレージ容量確認**
   - ディスク使用量チェック
   - 不要バックアップ削除（30日超過）

3. 🔍 **バージョン管理確認**
   - `verified/` ディレクトリ整合性
   - バージョン番号の連続性
   - ドキュメントとの一致

---

## バックアップREADMEテンプレート

### 日次バックアップ用

```markdown
# n8n Workflow Backup - YYYY-MM-DD HH:MM:SS

## Backup Summary

**Total Active Workflows**: XX
**Backup Date**: YYYY-MM-DD HH:MM:SS JST
**Backup Location**: `/path/to/backup/`
**Backup Type**: [scheduled | pre-deployment | pre-change | emergency]

## Workflow List

### WF7 Video Generation Pipeline (X workflows)
1. **WF7_Phase1_SNS動画台本整形.json**
   - ID: xxx
   - Webhook: xxx
   - Nodes: XX
   - Purpose: xxx
   - Last Updated: YYYY-MM-DD

[... 他のワークフロー ...]

## Context

**Reason for Backup**: [検証完了 | 定期バックアップ | 変更前保存]

**Changes Since Last Backup**:
- [変更内容1]
- [変更内容2]

**Verification Status**:
- [ ] E2Eテスト完了
- [ ] 本番動作確認完了
- [ ] ドキュメント更新完了

## Important Notes

- [重要な注意事項]
- [既知の問題]
- [依存関係]

## Next Steps

1. [次のアクション1]
2. [次のアクション2]
```

### 検証済みワークフロー用

```markdown
# {ワークフロー名} v{バージョン} - Verified Backup

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

手順: [詳細なロールバック手順]

## Notes

[その他重要事項]
```

---

## 復元手順

### バックアップから復元

#### 1. 検証済みワークフローの復元

```bash
# 1. バックアップファイル確認
cat workflows/backups/verified/WF7-Phase4_v1.0_20251101/README.md

# 2. n8n-mcp経由でワークフロー作成
# Claude Codeで実行:
# "WF7 Phase4の検証済みバックアップv1.0から復元して"
```

#### 2. タイムスタンプバックアップからの復元

```bash
# 1. 復元したいバックアップ特定
ls -la workflows/backups/

# 2. README確認
cat workflows/backups/20251101_125416/README.md

# 3. n8n UI経由でインポート
# - n8n UI → Workflows → Import from File
# - 対象JSONファイル選択
# - 認証情報・環境変数設定
# - テスト実行
```

---

## ベストプラクティス

### バックアップ命名規則

#### ワークフローJSONファイル
- **形式**: `{ワークフロー名}.json`
- **例**: `WF7_Phase4_動画レンダリング.json`
- **ルール**:
  - 日本語OK（可読性優先）
  - スペース → アンダースコア変換
  - 特殊文字除外: `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`

#### バックアップディレクトリ
- **日次**: `YYYYMMDD_HHMMSS`
- **検証済み**: `{ワークフロー名}_v{バージョン}_{YYYYMMDD}`
- **アーカイブ**: `deprecated_{YYYYMMDD}`

### 保持期間管理

#### 自動削除ルール（推奨）

```bash
# 30日超過の日次バックアップ削除（月次を除く）
# ※ 実装は任意
find workflows/backups/ -maxdepth 1 -type d -name "202*" -mtime +30 -exec rm -rf {} \;

# verifiedとarchiveは手動管理
```

#### 保持優先順位

1. **永久保持**: `verified/` 検証済みワークフロー
2. **1年保持**: `archive/` 廃止ワークフロー
3. **30日保持**: 日次バックアップ（月次を除く）
4. **永久保持**: 月次バックアップ（月末日分）

---

## トラブルシューティング

### Q1: バックアップが大きすぎる

**A**: メタデータのみのバックアップに切り替え

現在の運用では、各ワークフローのメタデータ（ID, name, nodes, updatedAt, webhook情報）のみを保存しています。完全なノード定義が必要な場合は `n8n_get_workflow(id)` で個別に取得してください。

### Q2: 復元時に認証情報が欠落

**A**: 認証情報は別途管理が必要

n8nの認証情報（Credentials）はワークフローJSONに含まれません。復元時は以下を再設定：
- OpenAI API Key
- Notion Integration Token
- その他API認証情報

### Q3: Webhookが動作しない

**A**: UI再保存が必要（n8n既知の制限）

Webhookワークフローを復元後、n8n UIで以下を実施：
1. ワークフローを開く
2. 「Save」ボタンクリック
3. Webhook URLが生成されることを確認

詳細: `docs/knowledge/n8n-workflow-construction-knowledge.md` 参照

### Q4: バージョン管理が複雑

**A**: セマンティックバージョニング簡易版を使用

- `v1.0`: 初回リリース
- `v1.1`, `v1.2`: マイナー更新（互換性あり）
- `v2.0`: メジャー更新（破壊的変更）

---

## チェックリスト

### ワークフロー検証完了時

- [ ] E2Eテスト全通過
- [ ] 本番環境で正常動作確認（最低24時間）
- [ ] エラーハンドリング動作確認
- [ ] ログ出力適切
- [ ] ドキュメント作成完了
- [ ] **バックアップ取得** → `verified/` に保存
- [ ] バージョンREADME作成
- [ ] Git commit & push

### 重要変更前

- [ ] 現在のアクティブワークフロー全バックアップ
- [ ] 変更内容をドキュメント化
- [ ] ロールバック手順確認
- [ ] テスト環境で動作確認
- [ ] **バックアップ検証** → 復元テスト実施

### 定期バックアップ（週次・月次）

- [ ] 全アクティブワークフローバックアップ
- [ ] README.md生成
- [ ] バックアップ検証（JSON妥当性）
- [ ] ストレージ容量確認
- [ ] 30日超過バックアップ削除（日次分のみ）
- [ ] 月次バックアップをGit LFSで保存（推奨）

---

## 自動化（今後の拡張）

### GitHub Actions統合案

```yaml
# .github/workflows/n8n-backup.yml
name: n8n Workflow Backup

on:
  schedule:
    - cron: '0 9 * * 5'  # 毎週金曜 18:00 JST
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backup Active Workflows
        run: |
          # Claude Code実行
          # n8n-mcp経由でバックアップ取得
      - name: Commit and Push
        run: |
          git add workflows/backups/
          git commit -m "chore: weekly n8n workflow backup"
          git push
```

---

## 関連ドキュメント

- [n8n Workflow Construction Knowledge](knowledge/n8n-workflow-construction-knowledge.md)
- [Best Practices](best-practices.md)
- [Troubleshooting](troubleshooting.md)

---

最終更新: 2025-11-01
