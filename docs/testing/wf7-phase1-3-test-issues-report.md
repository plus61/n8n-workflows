# WF7 Phase1-3 テスト問題レポート

## 実行情報
- **実行日時**: 2025-11-08 11:50-12:00 (JST)
- **テスト対象**: WF7 Phase1 → Phase2 → Phase3
- **ソースデータ**: WF6記事 (ID: `2a568d5c-2986-817b-b57e-df0cfb36f9ab`)
- **生成Notionページ**: `2a568d5c-2986-8182-a928-d891e8feaac1`

## 発見された問題

### 🚨 Critical Issues

#### 1. Notionデータベース不一致問題
**問題**: WF6とWF7で異なるNotionデータベースを使用している

**詳細**:
- **WF6 Articles DB**: `29968d5c-2986-81ad-90d0-c24ed710503e`
  - WF4-6パイプラインで使用
  - 記事データ（タイトル、本文、ステータス等）を保存

- **WF7 Videos DB**: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed`
  - WF7専用データベース
  - 動画生成データ（Script JSON、Assets JSON、Voice URL等）を保存

**影響**:
- Phase1でWF6記事データを直接参照できない
- `articleId`での紐付けはできるが、データベース間の直接リレーションが存在しない
- Phase4でWF6記事のメタデータ（カテゴリ、Author等）にアクセスできない

**現在の回避策**:
- Phase1実行時に手動で`title`と`keyPoints`を抽出してwebhookペイロードに含める
- `articleId`をWF7 DBの`Article ID`プロパティに保存して参照関係を維持

**推奨修正**:
- [ ] WF7 DBに`Hub Entry`リレーションプロパティを追加し、WF6記事と直接リレーション設定
- [ ] Phase1でWF6記事のNotion APIから直接データ取得するロジックを追加
- [ ] または、WF6とWF7で統一データベース構造を検討（Hub DB統合）

---

#### 2. Phase3の`scriptUrl`パラメータ問題
**問題**: Phase3ワークフローが`scriptUrl`パラメータを期待しているが、Phase1/Phase2では生成されない

**詳細**:
- Phase3の「ナレーション抽出」ノードのコード:
```javascript
const scriptUrl = body.scriptUrl;
// TODO: scriptUrlからscript.jsonを取得してnarrationTextを抽出
const narrationText = 'こちらの動画では、MEO対策の基本を紹介します。'; // ハードコード
```

- 現状の実装では`scriptUrl`が未実装
- Script JSONはNotionの`Script JSON`プロパティ（rich_text）に保存されているだけ

**影響**:
- Phase3が正常に動作しない（現在はハードコードされたnarrationTextを使用）
- 実際のScript JSONからnarrationを抽出できない

**現在の回避策**:
- Phase3実行時に手動で全セクションのnarrationテキストを結合してwebhookペイロードに含める

**推奨修正**:
- [ ] Phase1で生成したScript JSONをGoogle DriveまたはS3にアップロードし、`scriptUrl`を生成
- [ ] Phase3でNotionから直接Script JSON（rich_text）を読み込むロジックを実装
- [ ] Script JSON内の全セクションのnarrationフィールドを自動抽出・結合する処理を追加

---

#### 3. Script JSON構造の不一致
**問題**: Phase1で生成されるScript JSON構造がPhase4で期待される構造と異なる

**Phase1の実際の出力構造**:
```json
{
  "articleId": "...",
  "version": "1.0",
  "createdAt": "...",
  "video_script": {
    "sections": [
      {
        "section": "Hook",
        "duration": "0-10秒",
        "text": {
          "subtitle": "...",
          "narration": "...",
          "assets": ["tag1", "tag2"]  // ⚠️ 文字列配列
        }
      }
    ]
  }
}
```

**Phase4が期待する構造（FAL API用）**:
```json
{
  "segments": [
    {
      "assetTag": "...",
      "duration": 5,  // ⚠️ 数値（秒）
      "timestamp": 0
    }
  ]
}
```

**影響**:
- Phase4のペイロード構築ノードで`scriptData.segments`を参照しているが、実際は`scriptData.video_script.sections`
- `duration`が文字列形式（"0-10秒"）で数値ではない
- アセットタグが`text.assets`配列内に複数あるが、Phase4は各セグメントに1つのアセットタグを想定

**推奨修正**:
- [ ] Phase1のGPT-4プロンプトを修正して、Phase4互換のJSON構造を生成
- [ ] または、Phase1とPhase4の間に変換レイヤーを追加
- [ ] `duration`を数値（秒）で統一
- [ ] 各セクションの複数アセットを個別セグメントに分割

---

### ⚠️ Medium Issues

#### 4. Assets JSONのdriveFileId検証不足
**問題**: Phase2で生成されたGoogle Driveファイルのアクセシビリティ検証がない

**詳細**:
- Phase2はGoogle Drive APIでファイルアップロードし、`driveFileId`を取得
- しかし、FAL APIがこれらのファイルにアクセス可能かの検証がない
- Google Driveの共有設定が適切でない場合、Phase4でレンダリング失敗の可能性

**影響**:
- Phase4実行時にFAL APIが画像URLにアクセスできずエラー
- デバッグが困難（Phase2では成功と判定されるため）

**推奨修正**:
- [ ] Phase2でGoogle Driveファイルの共有設定を「リンクを知っている全員」に自動設定
- [ ] Phase2完了後、各画像URLに対してHTTP GETリクエストでアクセシビリティ検証
- [ ] 検証失敗時はエラーステータスをNotionに記録

---

#### 5. Phase間のステータス遷移の非一貫性
**問題**: 各Phaseでのステータス更新が統一されていない

**現在のステータス遷移**:
- Phase1完了: ステータス更新なし（初期値は不明）
- Phase2完了: `Status = "AssetsReady"`
- Phase3完了: `Status = "VoiceReady"`
- Phase4完了: `Status = "Completed"` (想定)

**問題点**:
- Phase1完了時のステータスが定義されていない
- Phase3はオプションだが、スキップ時のステータス遷移パスが不明確
- エラー発生時のステータス（"Failed", "Error"等）が未定義

**推奨修正**:
- [ ] 完全なステータス遷移図を定義
  - `Created` → `ScriptReady` → `AssetsReady` → `VoiceReady` → `RenderReady` → `Completed`
  - エラー時: `Failed` + `Error Message`プロパティに詳細記録
- [ ] 各PhaseのNotionページ更新で明示的にステータス設定
- [ ] Phase3スキップ時は`AssetsReady`から直接`RenderReady`に遷移

---

### ℹ️ Low Issues

#### 6. エラーメッセージプロパティの未使用
**問題**: Notion DBに`Error Message`プロパティが存在するが、Phase1-3では使用されていない

**推奨修正**:
- [ ] 各Phaseのエラーハンドリングノードで`Error Message`プロパティにエラー詳細を記録
- [ ] Statusを`Failed`に設定し、`Error Message`で原因を明示

---

#### 7. Phase2の画像検索キーワード最適化不足
**問題**: 日本語のアセットタグ（"渋谷の景色"等）をそのままPexels APIに送信している

**詳細**:
- Pexels APIは英語キーワードで最適な結果を返す
- 日本語タグのままでは関連性の低い画像が取得される可能性

**推奨修正**:
- [ ] Phase2のアセットタグを英語に翻訳するステップを追加
- [ ] GPT-4でアセットタグを英語キーワードに変換（例: "渋谷の景色" → "shibuya cityscape"）
- [ ] または、Phase1のGPT-4プロンプトで英語アセットタグを生成

---

## 修正優先度

### P0 (Critical - 即時対応必要)
1. **Script JSON構造の統一** (Issue #3)
   - Phase4実装に直接影響
   - Phase1のプロンプト修正が必要

2. **scriptUrl問題の解決** (Issue #2)
   - Phase3が正常動作しない
   - Notion直接読み込みまたはファイルURL生成を実装

### P1 (High - Phase4実装前に対応)
3. **ステータス遷移の明確化** (Issue #5)
   - 全体フロー理解に必要
   - エラーハンドリング設計に影響

4. **Assets JSONアクセシビリティ検証** (Issue #4)
   - Phase4実行時エラーの予防

### P2 (Medium - 改善推奨)
5. **Notionデータベース統合** (Issue #1)
   - 長期的なアーキテクチャ改善
   - Hub Entry リレーション設定で当面は対処可能

6. **エラーメッセージ記録** (Issue #6)
   - デバッグ効率向上

### P3 (Low - 将来の改善)
7. **画像検索キーワード最適化** (Issue #7)
   - 画像品質向上

---

## テストで正常動作した箇所

### ✅ 成功した機能
1. **Phase1: GPT-4によるScript JSON生成**
   - 4セクション構成（Hook/Pain/Solution/CTA）の生成成功
   - アセットタグの抽出成功（8個）

2. **Phase2: Pexels API + Google Drive連携**
   - 8個すべてのアセットタグで画像取得成功
   - Google Driveアップロード成功
   - Assets JSON生成成功

3. **Phase3: OpenAI TTS音声生成**
   - WAV形式の音声ファイル生成成功
   - SRT字幕ファイル生成成功
   - Webhook配信URL生成成功

4. **Notion API連携**
   - Phase1でのNotionページ作成成功
   - Phase2/Phase3でのNotionページ更新成功
   - すべてのプロパティ値が正常に保存

5. **Webhook連携**
   - 各PhaseのWebhook呼び出し成功
   - レスポンスデータの構造が正常

---

## 次のアクション

### 即座に実施
1. Script JSON構造の統一修正計画を立案
2. Phase4実装要件の明確化
3. ステータス遷移図の作成

### Phase4実装前に実施
4. scriptUrlまたはNotion直接読み込みの実装
5. Assets JSON検証ロジックの追加
6. エラーハンドリング強化

### 長期改善
7. Notionデータベース統合の検討
8. 画像検索キーワード最適化

---

## 参考情報
- WF6テスト結果: `/docs/testing/wf6-test-result-2025-11-08.md`
- Phase4トラブルシューティング: `/docs/knowledge/wf7-phase4-troubleshooting-guide.md`
- 生成Notionページ: https://www.notion.so/2a568d5c29868182a928d891e8feaac1
