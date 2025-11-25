# WF-B Loop Over Items実装テストガイド

**作成日時**: 2025-11-25 11:09:01 JST
**対象ワークフロー**: WF-B: Analyze & Suggest Next Actions (ID: 2mBYCQMjW2Vw1Xaa)
**バージョン**: 22 (versionId: 403f0b9d-0d94-4f0d-a421-4f16a1b29fad)
**優先度**: 🔴 Critical
**ステータス**: 実装完了・テスト実行待ち

---

## 📋 実装内容サマリー

### アーキテクチャ変更

**Before (Version 21 - Split In Batches使用)**:
```
Manual Trigger
  ↓
Google Sheets - Get editorial
  ↓
Function - Filter published
  ↓
Split In Batches (batchSize: 1)  ← 削除
  ├─ output 0 (continue) → Project Config B → ... → Google Sheets Update ─┐
  │                                                                         │
  └─ output 1 (complete) → Loop Back  ← 削除                               │
                              ↑                                             │
                              └─────────────────────────────────────────────┘
```
**問題**: Output 0が空配列になり、ループが機能しない

**After (Version 22 - Loop Over Items使用)**:
```
Manual Trigger
  ↓
Google Sheets - Get editorial
  ↓
Function - Filter published
  ↓
Project Config B (runOnceForEachItem)  ← 各アイテムに対して自動実行
  ↓
Merge
  ↓
Function - Preprocess (runOnceForEachItem)
  ↓
AI Agent (gpt-4o-mini) ← 各アイテムごとに実行
  ↓
Function - Validate Schema (runOnceForEachItem)
  ↓
Google Sheets - Update ← 各アイテムごとに実行（ループバック不要）
```
**解決**: n8nのネイティブアイテム反復機能を使用、明示的なループ不要

### ノード変更詳細

**削除されたノード** (2つ):
- `Split In Batches` (id: "split-batches")
- `Loop Back` (id: "loop-back")

**変更されたノード** (1つ):
- `Project Config B`: `"mode": "runOnceForEachItem"` に設定

**接続変更**:
- `Function - Filter published` → `Project Config B` (直接接続)
- `Google Sheets - Update`: ループバック接続削除（`"main": []`）

**保持されたノード** (10個):
1. Manual Trigger
2. Google Sheets - Get editorial
3. Function - Filter published
4. Project Config B (runOnceForEachItem)
5. Merge
6. Function - Preprocess (runOnceForEachItem)
7. AI Agent (gpt-4o-mini)
8. OpenAI Chat Model
9. Function - Validate Schema (runOnceForEachItem)
10. Google Sheets - Update

---

## 🎯 テスト目的

### 検証ポイント

1. **全ノード実行確認**
   - 10個すべてのノードが実行される
   - エラーが発生しない

2. **アイテム反復確認**
   - AI Agent が3回実行される（テストデータ3件分）
   - Google Sheets Update が3回実行される

3. **AI決定精度確認**
   - Row 2 (AI活用): `next_decision: "pause"` (PV=150, conversion=0.5%, Cold)
   - Row 3 (n8n自動化): `next_decision: "improve"` (PV=500, conversion=1.2%, Middle)
   - Row 4 (マーケティング自動化): `next_decision: "scale"` (PV=3500, conversion=2.8%, Hot)

4. **データ整合性確認**
   - Google Sheets 'editorial' シートに3行追加
   - すべてのフィールドが正しく書き込まれる

---

## 📊 テストデータ

### 前提条件

Google Sheets 'ideas' シートに以下の3レコードが存在すること：

| row_number | status | trending_keyword | abstract | segment | generated_title | note_url | note_pv | note_likes | note_conversion | created_at |
|------------|--------|------------------|----------|---------|-----------------|----------|---------|------------|-----------------|------------|
| 2 | published | AI活用 | AIビジネス活用の基礎 | Cold | AI活用の基礎：ビジネスでの実践ガイド | https://note.com/test/n/n123456789abc | 150 | 5 | 0.5 | 2025-11-25_02:40:00 JST |
| 3 | published | n8n自動化 | n8nで業務効率化 | Middle | n8nで始める業務自動化入門 | https://note.com/test/n/n234567890bcd | 500 | 12 | 1.2 | 2025-11-25_02:40:00 JST |
| 4 | published | マーケティング自動化 | データドリブンマーケティング | Hot | マーケティング自動化の実践テクニック | https://note.com/test/n/n345678901cde | 3500 | 45 | 2.8 | 2025-11-25_02:40:00 JST |

**テストデータ詳細**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-25_02-40_WF-B-test-data.md`

### AI決定ロジック（再掲）

```javascript
// WF-B AI Agentのプロンプトより
DECISION CRITERIA:
- "improve": PV < 1000 OR conversion < 1%
- "pause": PV < 100 AND conversion < 0.5% AND segment is Cold
- "scale": PV > 3000 AND conversion > 2%
```

### 期待される結果

**Row 2 (AI活用)**:
- `next_decision`: "pause"
- 理由: PV=150は100以上だが、conversion=0.5%かつsegment=Coldの条件に該当

**Row 3 (n8n自動化)**:
- `next_decision`: "improve"
- 理由: PV=500 < 1000の条件に該当

**Row 4 (マーケティング自動化)**:
- `next_decision`: "scale"
- 理由: PV=3500 > 3000かつconversion=2.8% > 2%の両方を満たす

---

## 🚀 テスト実行手順

### Step 1: Google Sheetsの確認

1. **Google Sheets URL**: https://docs.google.com/spreadsheets/d/1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII/edit

2. **'ideas' シートの確認**:
   - Row 2, 3, 4に上記のテストデータが存在すること
   - `status` 列がすべて "published" であること

3. **'editorial' シートの確認**:
   - 現在の行数を記録（テスト前）
   - テスト後に3行増えることを確認

### Step 2: n8nでWF-B実行

1. **n8n UI URL**: https://n8n-python-production-344b.up.railway.app/workflow/2mBYCQMjW2Vw1Xaa

2. **実行方法**:
   - 「Execute Workflow」ボタンをクリック
   - または Manual Trigger ノードをクリックして実行

3. **実行時間**: 約30-60秒（3レコード分、AI Agent実行時間含む）

### Step 3: 実行ログの確認

**確認ポイント**:

1. **全ノード実行確認** (10ノード):
   ```
   ✅ Manual Trigger
   ✅ Google Sheets - Get editorial (3 items)
   ✅ Function - Filter published (3 items filtered)
   ✅ Project Config B (3 executions)
   ✅ Merge (3 executions)
   ✅ Function - Preprocess (3 executions)
   ✅ AI Agent (gpt-4o-mini) (3 executions)
   ✅ OpenAI Chat Model (3 connections)
   ✅ Function - Validate Schema (3 executions)
   ✅ Google Sheets - Update (3 executions)
   ```

2. **エラーの有無**:
   - すべてのノードが緑色（成功）であること
   - 赤色（エラー）のノードがないこと

3. **データフロー確認**:
   - 各ノードの Output Data を確認
   - AI Agent の output に JSON文字列が含まれること
   - Validate Schema が正しくパースできていること

### Step 4: Google Sheets 'editorial' シートの確認

**確認ポイント**:

1. **行数確認**:
   - テスト前の行数 + 3 になっていること

2. **各行のフィールド確認**:
   ```
   Row N (AI活用):
   - next_decision: "pause"
   - next_action: (200文字以内の具体的なアクション)
   - next_segment: "Cold"
   - next_keyword_idea: (100文字以内のキーワード案)
   - insights_json: (JSON配列文字列、2-4個のインサイト)
   - reasoning: (500文字以内の判断理由)
   - analyzed_at: (実行時刻のISO 8601タイムスタンプ)

   Row N+1 (n8n自動化):
   - next_decision: "improve"
   - next_action: (200文字以内の具体的なアクション)
   - next_segment: "Middle"
   - next_keyword_idea: (100文字以内のキーワード案)
   - insights_json: (JSON配列文字列、2-4個のインサイト)
   - reasoning: (500文字以内の判断理由)
   - analyzed_at: (実行時刻のISO 8601タイムスタンプ)

   Row N+2 (マーケティング自動化):
   - next_decision: "scale"
   - next_action: (200文字以内の具体的なアクション)
   - next_segment: "Hot"
   - next_keyword_idea: (100文字以内のキーワード案)
   - insights_json: (JSON配列文字列、2-4個のインサイト)
   - reasoning: (500文字以内の判断理由)
   - analyzed_at: (実行時刻のISO 8601タイムスタンプ)
   ```

3. **データ型確認**:
   - `next_decision`: 文字列（"improve", "pause", "scale"のいずれか）
   - `next_action`: 文字列（200文字以内）
   - `next_segment`: 文字列（"Cold", "Middle", "Hot", "Current"のいずれか）
   - `next_keyword_idea`: 文字列（100文字以内）
   - `insights_json`: JSON配列文字列（例: `["Insight 1","Insight 2"]`）
   - `reasoning`: 文字列（500文字以内）
   - `analyzed_at`: ISO 8601タイムスタンプ（例: `2025-11-25T02:09:01.123Z`）

---

## 📝 テスト結果記録フォーマット

### 実行情報

```markdown
**実行日時**: YYYY-MM-DD HH:MM:SS JST
**実行者**: [名前]
**Execution ID**: [n8nの実行ID]
**実行時間**: [秒]
```

### 実行結果

```markdown
## ✅ 成功項目

- [ ] 全10ノードが実行された
- [ ] エラーが発生しなかった
- [ ] AI Agent が3回実行された
- [ ] Google Sheets Update が3回実行された
- [ ] 'editorial' シートに3行追加された
- [ ] Row 2 の next_decision が "pause" だった
- [ ] Row 3 の next_decision が "improve" だった
- [ ] Row 4 の next_decision が "scale" だった
- [ ] すべてのフィールドが正しく書き込まれた

## ❌ 失敗項目

- [ ] 該当なし

または：

- [ ] [具体的な失敗項目]
- [ ] [エラーメッセージ]
- [ ] [スクリーンショット添付]
```

### AI Agent出力例（参考）

```json
{
  "next_decision": "pause",
  "next_action": "コンテンツ品質を見直し、Cold セグメント向けにより魅力的なビジュアルと具体例を追加する",
  "next_segment": "Cold",
  "next_keyword_idea": "AI導入 効果",
  "insights": [
    "現在の記事はPVとコンバージョンがゼロで、エンゲージメントが低い",
    "セグメントがColdで、認知度向上戦略が必要",
    "トレンドキーワードは関連性があるが、コンテンツに魅力が不足",
    "スケール前に改善が必要"
  ],
  "reasoning": "PVは0、コンバージョンは0%で、改善またはスケールの閾値を下回っている。セグメントがColdで、一時停止して戦略を再評価する基準を満たしている。"
}
```

---

## 🐛 トラブルシューティング

### 問題1: Google Sheets - Get editorial が0件を返す

**原因**: 'ideas' シートにテストデータが存在しない

**解決策**:
1. Google Sheets 'ideas' シートを確認
2. テストデータを手動で追加（参照: `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-25_02-40_WF-B-test-data.md`）
3. `status` 列が "published" であることを確認

### 問題2: Function - Filter published が0件を返す

**原因**: `status` 列の値が "published" ではない（全角/半角、前後スペース）

**解決策**:
1. Google Sheets で `status` 列を確認
2. 正確に "published"（小文字、スペースなし）であることを確認
3. 必要に応じて修正

### 問題3: AI Agent がエラーを返す

**原因1**: OpenAI API キーが無効
**解決策**: n8n Credentials で OpenAI API キーを確認

**原因2**: AI Agent プロンプトでデータが渡されていない
**解決策**: Function - Preprocess の出力を確認、`$json.row` にデータが含まれているか確認

### 問題4: Function - Validate Schema でパースエラー

**原因**: AI Agent が JSON 以外の形式で応答

**解決策**:
1. AI Agent の出力を確認
2. Markdown コードブロック（```json```）が含まれていないか確認
3. AI Agent プロンプトの "CRITICAL REQUIREMENTS" セクションを確認

### 問題5: Google Sheets Update で書き込みエラー

**原因1**: Google Sheets Credentials が無効
**解決策**: n8n Credentials で Google Sheets 認証を確認

**原因2**: 'editorial' シートが存在しない
**解決策**: Google Sheets で 'editorial' シートを作成

**原因3**: フィールドマッピングエラー
**解決策**: Google Sheets Update ノードの設定を確認、`={{ $json.next_decision }}` 等の式が正しいか確認

---

## 📚 関連ドキュメント

- **テストデータ**: `now/2025-11-25_02-40_WF-B-test-data.md`
- **前回修正レポート**: `now/2025-11-25_01-12_WF-B-loop-connection-fix-report.md`
- **Phase 4型インシデント知識**: `now/2025-11-24_18-13_WF-B-critical-fixes-knowledge.md`
- **Validation実装**: `now/2025-11-24_01-59_function-validate-schema-fixed.js`
- **オリジナルバックアップ**: `now/2025-11-23_22-22_WF-B-backup.json`

---

## ✅ テスト完了確認チェックリスト

- [ ] テストデータがGoogle Sheets 'ideas' シートに存在する
- [ ] WF-B Version 22 を手動実行した
- [ ] 実行ログで10ノードすべてが成功した
- [ ] AI Agent が3回実行されたことを確認した
- [ ] Google Sheets 'editorial' シートに3行追加された
- [ ] Row 2の next_decision が "pause" だった
- [ ] Row 3の next_decision が "improve" だった
- [ ] Row 4の next_decision が "scale" だった
- [ ] すべてのフィールドが正しく書き込まれた
- [ ] テスト結果を `CURRENT_STATE.md` に記録した

---

**作成者**: Claude Code
**検証対象**: WF-B Loop Over Items実装（Version 22）
**目的**: Split In Batches削除後のネイティブアイテム反復機能検証
