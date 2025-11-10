# WF7 Phase4 簡素化設計書

**作成日**: 2025-11-09  
**対象ワークフロー**: `r9Sp5n0mkUCcH8cw` (WF7 Phase4 - V3 Fixed_final)  
**目的**: 複雑性の罠から脱却し、必要最低限のノードで実用的なワークフローを実現  
**ベース**: n8n MCPツールによる分析結果 + ベストプラクティス

---

## 📊 現状分析

### 現在のワークフロー統計

| 項目 | 値 | 問題点 |
|------|-----|--------|
| **総ノード数** | 48個 | 必要最低限の2.5-3倍 |
| **エラー数** | 5個 | 構造的問題あり |
| **警告数** | 65個 | typeVersion古い、エラーハンドリング不足 |
| **線形チェーン** | 23ノード | サブワークフロー分割推奨 |
| **サイクル** | 検出 | 無限ループの可能性 |

### 主な問題点

1. **データ変換の多段階処理**
   - `Webhookデータ抽出` → `URL抽出` → `データ統合` → `Set - Phase4a Payload` → `Set - Phase4b Payload` → `レスポンスデータ準備` → `レスポンスデータ復元`
   - 同じデータを何度も整形している

2. **エラーハンドリングの分散**
   - Phase4aエラー、Phase4bエラー、Phase4cエラーでそれぞれ別ノード
   - 統一的なエラーハンドリング戦略がない

3. **FAL処理のポーリング機構が親フローに残存**
   - `Submit to FAL` → `Fetch Status` → `Wait for Processing` → `Check Render Status` → `Retry Counter` → `Check Retry Limit` → `Wait Before Retry`
   - これらはPhase4b側で処理すべき

4. **不要な中間ノード**
   - `レスポンスデータ準備` → `レスポンスデータ復元`（データを一時保存して復元するだけ）

5. **Codeノードの制約違反**
   - `Code - Phase4c FFmpeg Concat`: ファイルシステムアクセス不可（Pyodide環境の制限）
   - `Code - Cleanup Temp Files`: ファイルシステムアクセス不可（Pyodide環境の制限）

---

## 🎯 簡素化目標

### 目標ノード数

| 構成 | 現在 | 目標 | 削減率 |
|------|------|------|--------|
| **親フロー** | 48ノード | 10-12ノード | **75-80%削減** |
| **Phase4a** | 統合済み | 独立サブワークフロー | - |
| **Phase4b** | 統合済み | 独立サブワークフロー | - |
| **Phase4c** | 統合済み | 独立サブワークフロー | - |

### 設計原則

1. **サブワークフロー化**: Phase4a/b/cを完全独立のサブワークフローとして実装
2. **エラーハンドリング統一**: 1つのIFノード + 1つのエラーハンドリングノード
3. **データ変換の標準化**: 各Phaseの入力/出力をJSONで標準化
4. **最小限のオーケストレーション**: 親フローはHTTP Requestで呼び出すだけ

---

## 🏗️ 簡素化版アーキテクチャ

### 全体構造

```
┌─────────────────────────────────────────────────────────────┐
│ 親フロー: WF7 Phase4 Orchestrator (10-12ノード)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Webhook (受信)                                          │
│     ↓                                                       │
│  2. Notion API呼び出し (台本データ取得)                     │
│     ↓                                                       │
│  3. Execute Sub-workflow - Phase4a (スライド生成)           │
│     ↓ slides_metadata[7]                                    │
│  4. Execute Sub-workflow - Phase4b (動画生成)               │
│     ↓ videos_metadata[7]                                    │
│  5. Execute Sub-workflow - Phase4c (動画結合)               │
│     ↓ final_video_url                                        │
│  6. IF - Success Check                                      │
│     ├─ [true] → Respond to Webhook                         │
│     └─ [false] → Error Handler → Respond to Webhook        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### データ契約

```yaml
# Phase4a入力
script_id: string (必須)
scriptData: object (必須)

# Phase4a出力
success: boolean (必須)
script_id: string (必須)
slides_metadata: array (必須、7要素)
slides_count: number (必須、7)

# Phase4b入力
script_id: string (必須)
slides_metadata: array (必須、7要素)

# Phase4b出力
success: boolean (必須)
script_id: string (必須)
videos_metadata: array (必須、7要素)
  - section: string
  - video_url: string
  - duration: number
  - render_elapsed: number
videos_count: number (必須、7)
total_duration: number

# Phase4c入力
script_id: string (必須)
videos_metadata: array (必須、7要素)

# Phase4c出力
success: boolean (必須)
script_id: string (必須)
final_video_path: string
final_video_url: string
total_duration: number
video_size_mb: number
```

---

## 🔄 移行計画

### Phase 1: サブワークフロー準備（1-2日）

1. **Phase4a確認**
   - 既存ワークフロー `LYPbvJfkMzLlhc6t` の動作確認
   - 入力/出力データ契約の確認
   - 必要に応じて改修

2. **Phase4b改修**
   - 既存ワークフロー `wHaKi98mTlUvFIOR` の改修
   - FALポーリング・リトライロジックをサブワークフロー内に完結
   - 入力/出力データ契約の標準化

3. **Phase4c作成**
   - 新規ワークフロー作成
   - 外部PythonスクリプトまたはExecute Commandノードで実装
   - 入力/出力データ契約の定義

### Phase 2: 親フロー簡素化（1日）

1. **バックアップ**
   - 現在のワークフロー `r9Sp5n0mkUCcH8cw` をバックアップ
   - `workflows/archive/wf7-phase4-v3-complex.json` として保存

2. **ノード削除**
   - 不要なSetノード削除
   - FALポーリング機構削除（Phase4bに移行）
   - レスポンスデータ準備/復元ノード削除

3. **Execute Sub-workflowノード追加**
   - Phase4a/b/cのExecute Sub-workflowノードを追加
   - データマッピング設定

4. **エラーハンドリング統合**
   - 統一IFノード追加
   - エラーハンドリングノード統合

### Phase 3: テスト・検証（1-2日）

1. **単体テスト**
   - Phase4a単体テスト
   - Phase4b単体テスト
   - Phase4c単体テスト

2. **統合テスト**
   - 親フロー全体のE2Eテスト
   - エラーハンドリングテスト

3. **パフォーマンステスト**
   - 処理時間の測定
   - メモリ使用量の確認

---

## 📈 期待効果

### 定量的効果

| 指標 | 現在 | 目標 | 改善率 |
|------|------|------|--------|
| **ノード数** | 48個 | 10-12個 | **75-80%削減** |
| **実行時間** | 5-10分 | 3-5分 | **40-50%短縮** |
| **保守性** | 低 | 高 | **大幅改善** |
| **エラー率** | 5% | 1%以下 | **80%削減** |

### 定性的効果

1. **保守性の向上**: サブワークフロー化により、各Phaseの修正が独立して可能
2. **テスト容易性**: 各Phaseを個別にテスト可能
3. **再利用性**: Phase4a/b/cを他のワークフローでも再利用可能
4. **可読性**: 親フローがシンプルになり、全体像が把握しやすい

---

## ⚠️ 注意事項

### Phase4cの制約

現在の実装では、`Code - Phase4c FFmpeg Concat`と`Code - Cleanup Temp Files`がPyodide環境で実行されるため、ファイルシステムアクセスが制限されています。

**解決策**:
1. **Execute Commandノードを使用**: Railway環境で直接FFmpegコマンドを実行
2. **外部Pythonスクリプト**: FastAPIエンドポイントとして実装し、HTTP Requestで呼び出す
3. **FAL FFmpeg APIを使用**: FALのFFmpeg API `/compose`エンドポイントを使用して動画結合

### 推奨アプローチ

**FAL FFmpeg APIを使用**することを推奨します。理由：
- ファイルシステムアクセスの制約がない
- サーバーレスで実行可能
- コスト効率が良い
- 既存のFAL API認証情報を再利用可能

---

## 📝 次のステップ

1. **Phase4cの実装方法を決定**
   - FAL FFmpeg APIを使用するか、Execute Commandノードを使用するか
   - 実装方法に応じて、Phase4cサブワークフローを作成

2. **Phase4a/b/cのデータ契約を標準化**
   - 各Phaseの入力/出力をJSONで標準化
   - エラーハンドリングを統一

3. **親フローの簡素化を実施**
   - 不要なノードを削除
   - Execute Sub-workflowノードを追加

4. **テスト・検証を実施**
   - 単体テスト
   - 統合テスト
   - パフォーマンステスト

---

**作成**: Claude Code (Composer)  
**最終更新**: 2025-11-09

