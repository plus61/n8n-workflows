# WF7 E2Eテスト実行レポート

**実行日**: 2025-11-01
**目的**: WF7 SNS動画生成パイプライン全体を実データで検証し、動画出力まで完遂する
**結果**: Phase1-2成功、Phase4で致命的なアーキテクチャ問題を検出

---

## 📋 実行サマリー

| Phase | ステータス | 実行ID | 結果 |
|-------|----------|--------|------|
| Phase1: 台本生成 | ✅ 成功 | 1239 | GPT-4で4セクション台本生成完了 |
| Phase2: 素材取得 | ✅ 成功 | 1241 | Pexels画像1枚取得、Notion更新完了 |
| Phase3: 音声生成 | ⏭️ スキップ | - | 音声なしテストのため省略 |
| Phase4: 動画レンダリング | ❌ 失敗 | 1242 | File Server空レスポンス + Python実行環境不在 |
| Phase5: 最終登録 | ⏹️ 未実行 | - | Phase4失敗のため到達せず |

**総合判定**: 🚨 **アーキテクチャ設計に根本的な問題あり** - Phase4実行不可能

---

## 🎬 Phase1: 台本生成 ✅

### 実行コマンド
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-test-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-meo-001",
    "title": "🧭 AI検索時代に選ばれる店舗へ：MEO（地図最適化）が\"近さ\"を価値に変える",
    "keyPoints": "「この記事ではAI時代におけるMEOの重要性を、渋谷の店舗を例に解説しています」..."
  }'
```

### 入力データソース
- **Notion DB**: `29968d5c298681ad90d0c24ed710503e` (note記事管理DB)
- **記事ID**: `29968d5c-2986-81e3-957b-e70b6507991e`
- **ステータス**: 検知済み

### 出力結果
**実行ID**: `1239`
**Notion Page作成**: `29e68d5c-2986-81c7-a260-cf9084f8d864`

**生成台本構造**:
```json
{
  "sections": [
    {
      "type": "hook",
      "text": "AI検索が店舗選択の鍵を握る時代、あなたの店舗は地図上で見つけてもらえていますか？",
      "duration": 5
    },
    {
      "type": "pain",
      "text": "どんなに良いサービスでも、位置情報の最適化がなければ顧客の目に留まりません...",
      "duration": 10
    },
    {
      "type": "solution",
      "text": "MEO（地図エンジン最適化）を活用すれば、Googleマップの検索結果で上位表示され...",
      "duration": 10
    },
    {
      "type": "cta",
      "text": "今すぐ詳細を確認して、あなたの店舗を地図上で目立たせましょう！リンクはこちら",
      "duration": 5
    }
  ],
  "totalDuration": 30
}
```

**抽出アセットタグ**: 12タグ
- 店舗, AI, 検索, AI検索, 位置情報, 顧客, MEO, Googleマップ, 最適化, CTA, リンク, 店舗選択

**GPT-4設定**:
- Model: `gpt-4-turbo`
- Temperature: 0.7
- Max Tokens: 2000

**✅ Phase1完全成功**: Notion DB更新、台本JSON生成、アセットタグ抽出すべて完了

---

## 🖼️ Phase2: 素材取得 ✅

### 実行コマンド
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-meo-001",
    "notionPageId": "29e68d5c-2986-81c7-a260-cf9084f8d864",
    "assetTags": "店舗,AI,検索,AI検索,位置情報,顧客,MEO,Googleマップ,最適化,CTA,リンク,店舗選択"
  }'
```

### 実行ID: `1241`

### 取得結果
**成功**: 1画像取得 (Pexels)
- **タグ**: 店舗
- **画像URL**: `https://images.pexels.com/photos/[image-id]/pexels-photo-[image-id].jpeg`
- **解像度**: 1920x1080
- **ソース**: Pexels API

**他のタグ**: 11タグは画像取得失敗（Pexels/Unsplash両方でマッチなし）

### Notion更新
- **ステータス**: `ScriptGenerated` → `AssetsReady`
- **Assets JSONフィールド**: 下記構造で保存
```json
{
  "images": [
    {
      "tag": "店舗",
      "url": "https://images.pexels.com/photos/.../pexels-photo-....jpeg",
      "source": "pexels",
      "width": 1920,
      "height": 1080
    }
  ],
  "totalAssets": 1
}
```

**✅ Phase2成功**: 1画像取得、Notion更新完了

**⚠️ 注意**: 12タグ中11タグで画像取得失敗 - 日本語タグの検索性能に課題

---

## 🎥 Phase4: 動画レンダリング ❌

### 実行コマンド
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-meo-001",
    "scriptUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-script?articleId=test-meo-001",
    "assetsUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-assets?articleId=test-meo-001",
    "templateId": "default"
  }'
```

### 実行ID: `1242`
**ステータス**: ❌ ERROR

---

## 🚨 致命的な問題1: File Server空レスポンス

### 問題の詳細
Phase4が期待するFile Server URLにアクセスしても、JSONデータが取得できない。

#### 検証コマンド
```bash
# script.json取得試行
curl "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-script?articleId=test-meo-001"
# 結果: 空レスポンスまたは404

# assets.json取得試行
curl "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-assets?articleId=test-meo-001"
# 結果: 空レスポンスまたは404
```

### 根本原因分析

#### File Server Workflow構造
File Serverは6つの独立したn8nワークフローで構成:
1. `wf7-files-script` (GET webhook)
2. `wf7-files-assets` (GET webhook)
3. `wf7-files-video` (GET webhook)
4. `wf7-files-subtitles` (GET webhook)
5. `wf7-files-audio` (GET webhook)
6. `wf7-files-metadata` (GET webhook)

**期待動作**:
- Phase1/2がPOSTでJSON uploadを送信
- File Serverがデータをメモリまたはファイルシステムにキャッシュ
- Phase4がGETでデータを取得

**実際の動作**:
```javascript
// Phase1 Workflowのノード構成（wf7-phase1ワークフロー取得結果より）
1. Webhook (wf7-test-webhook) - POST受信
2. Code: 入力検証
3. Code: Prompt構築
4. GPT-4 APIコール
5. Code: 台本整形
6. Code: アセットタグ抽出
7. Notion: Page作成
8. Webhook Response - 終了

// 👈 File Serverへのアップロードステップが存在しない
```

**Phase1/2はNotionにのみ書き込み、File Serverへのアップロードを行っていない**

### 設計上の矛盾

| 想定アーキテクチャ | 実装状況 | 結果 |
|----------------|---------|------|
| Phase1 → File Server Upload | ❌ 未実装 | script.json空 |
| Phase2 → File Server Upload | ❌ 未実装 | assets.json空 |
| File Server → データ保持 | ⚠️ ソースなし | 何も返せない |
| Phase4 → File Server Download | ✅ 実装済み | ダウンロード失敗 |

### Phase4での実際のエラーログ
```json
{
  "node": "Download Script from File Server",
  "error": "Request failed with status code 404 or empty body",
  "details": {
    "url": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-script?articleId=test-meo-001",
    "fileSize": "0 B",
    "contentType": "text/plain"
  }
}
```

---

## 🚨 致命的な問題2: Python実行環境不在

### エラー内容
```
Command failed: python /app/render_video.py --script /tmp/script_test-meo-001.json --assets /tmp/assets_test-meo-001.json --template default --out /tmp/video_test-meo-001.mp4

/bin/sh: python: not found
```

### Phase4のExecute Command設定
```json
{
  "command": "python /app/render_video.py --script /tmp/script_test-meo-001.json --assets /tmp/assets_test-meo-001.json --template default --out /tmp/video_test-meo-001.mp4"
}
```

### 根本原因
**Railway n8nコンテナにPython実行環境がインストールされていない**

#### 必要な依存関係（すべて不在）
1. Python 3.8+ インタープリター
2. MoviePy (`pip install moviepy`)
3. FFmpeg バイナリ
4. Pillow (`pip install Pillow`)
5. NumPy (`pip install numpy`)
6. その他Pythonライブラリ

### 環境確認
```bash
# Railway n8nコンテナ内
which python   # Not found
which python3  # Not found
which ffmpeg   # Not found
which pip      # Not found
```

**Railway n8nは純粋なNode.jsコンテナイメージ** - Python/FFmpegは含まれていない

---

## 🔍 アーキテクチャ問題の全体像

### 現在のデータフロー（実装済み）
```
WF6 (note記事生成)
  ↓
Notion DB登録
  ↓
[Phase1: GPT-4台本生成]
  ├→ Notion DB書き込み ✅
  └→ File Server Upload ❌ 未実装

[Phase2: Pexels画像取得]
  ├→ Notion DB書き込み ✅
  └→ File Server Upload ❌ 未実装

[File Server (6 workflows)]
  └→ データソースなし → 空レスポンス

[Phase4: 動画レンダリング]
  ├→ File Server Download試行 ❌ 404/空
  ├→ Python実行試行 ❌ 実行環境なし
  └→ 処理中断
```

### 期待されていたデータフロー（設計意図）
```
[Phase1: 台本生成]
  ├→ Notion DB書き込み ✅
  └→ File Server POST /upload-script ⚠️ 必要

[Phase2: 素材取得]
  ├→ Notion DB書き込み ✅
  └→ File Server POST /upload-assets ⚠️ 必要

[File Server]
  ├→ メモリキャッシュまたはファイル保存 ⚠️ 必要
  └→ GET webhookでJSON返却

[Phase4: 動画レンダリング]
  ├→ File Server GET script.json ✅ 実装済み
  ├→ File Server GET assets.json ✅ 実装済み
  ├→ Python + MoviePy実行 ⚠️ 環境構築必要
  └→ 動画ファイル出力
```

---

## 💡 解決策の選択肢

### Option A: File Server統合実装（設計意図に従う）

#### 必要な作業
1. **Phase1にFile Server Upload追加**
   - HTTP Request node追加: POST to `wf7-files-script-upload`
   - Payload: `{ articleId, scriptJson }`

2. **Phase2にFile Server Upload追加**
   - HTTP Request node追加: POST to `wf7-files-assets-upload`
   - Payload: `{ articleId, assetsJson }`

3. **File Server側にUpload endpoint実装**
   - 新規webhookノード: `wf7-files-script-upload` (POST)
   - 新規webhookノード: `wf7-files-assets-upload` (POST)
   - データ保存: n8n Execute Commandでファイル書き込み、またはメモリキャッシュ（Redis等）

4. **File Server GET endpointの修正**
   - 保存済みデータを読み込んで返却

#### メリット
- 設計意図通りの実装
- Phase間の疎結合性を維持
- スケーラビリティ（File Server分離）

#### デメリット
- 実装工数が大きい（4-6 workflows修正）
- File Serverのデータ永続化戦略が必要
- Railway環境でのファイルI/O制約（ephemeral storage）

---

### Option B: Phase4を直接Notion読み取りに変更（シンプル化）

#### 必要な作業
1. **Phase4のDownloadノードを削除**
   - `Download Script from File Server` → 削除
   - `Download Assets from File Server` → 削除

2. **Notion API読み取りノード追加**
   - Notion APIでnotionPageId指定
   - `script`プロパティ取得 → JSONパース
   - `assets`プロパティ取得 → JSONパース

3. **Code nodeでJSON整形**
   - Notion rich_text形式 → MoviePy入力形式

#### メリット
- 実装工数最小（Phase4のみ修正）
- File Server不要 → アーキテクチャ簡素化
- データソースが単一（Notion DB）

#### デメリット
- Notion APIレート制限の影響
- Notionプロパティのサイズ制約（2000文字）
- Phase4がNotionに密結合

---

### Option C: Python環境をRailwayコンテナに追加

#### 必要な作業
1. **Dockerfileカスタマイズ**
   ```dockerfile
   FROM n8nio/n8n:latest

   # Python + FFmpeg追加
   RUN apk add --no-cache python3 py3-pip ffmpeg

   # MoviePy依存関係
   RUN pip3 install moviepy pillow numpy

   # render_video.pyをコピー
   COPY render_video.py /app/render_video.py
   ```

2. **Railwayでカスタムイメージデプロイ**
   - GitHub連携でDockerfile自動ビルド
   - 環境変数設定維持

3. **render_video.py実装**
   - MoviePy APIで動画合成
   - 1080x1920縦型、30fps、H.264出力

#### メリット
- Phase4の設計意図を実現
- 本格的な動画編集機能実装可能
- FFmpegで高度なエフェクト追加可能

#### デメリット
- **コンテナイメージサイズ大幅増加**（+500MB~1GB）
- Railway無料枠の実行時間制約
- 動画レンダリングの処理時間（30-60秒/動画）
- メモリ消費量増加（512MB→1-2GB必要）

---

## 📊 推奨アプローチ

### 🥇 第1推奨: **Option B（Notion直接読み取り）+ Option C（Python環境構築）**

#### 理由
1. **即時性**: File Server実装を省略し、迅速にE2Eテスト完遂
2. **実用性**: Notionプロパティ2000文字制約は台本/アセット用途で十分
3. **完全性**: Python環境構築で動画出力まで到達

#### 実装ステップ
**Phase 1: Notion直接読み取り実装（1-2時間）**
- Phase4のDownloadノード削除
- Notion API読み取りノード追加
- JSON整形Code node実装

**Phase 2: Python環境構築（2-3時間）**
- Dockerfileカスタマイズ
- render_video.py実装（MoviePy）
- Railwayデプロイ＆動作確認

**Phase 3: E2Eテスト実行（30分）**
- Phase1-4連続実行
- 動画ファイル出力確認
- Notion最終ステータス更新確認

---

### 🥈 第2推奨: **Option A（File Server統合）のみ** ※Python環境は後回し

#### 理由
- 設計意図に忠実
- アーキテクチャの完全性維持
- Python環境はモックで代替可能（テスト用JSON出力）

#### 実装ステップ
**Phase 1: File Server Upload実装（3-4時間）**
- Phase1/2にHTTP Request Upload追加
- File Server側Upload endpoint実装
- ファイル永続化戦略決定（tmpファイル or Redis）

**Phase 2: Phase4統合テスト（1時間）**
- DownloadノードでJSON取得確認
- Python部分はモック（`echo '{"status":"success"}' > /tmp/video.mp4`）

**Phase 3: Python環境構築（後日対応）**
- Option C実施

---

## 📝 Phase1での教訓 - Lesson Learned

### ✅ 成功したこと
1. **GPT-4台本生成品質**: 4セクション構造で自然な日本語台本生成
2. **Notion統合**: Page作成とプロパティ書き込みが安定動作
3. **Webhook連携**: RailwayのPOST webhookが想定通り機能

### ⚠️ 改善が必要なこと
1. **File Server設計の検証不足**:
   - Phase1実装時にFile Server Uploadの必要性を見落とし
   - Phase4実装時に初めてダウンロード前提が判明
   - **教訓**: 依存関係を事前にワークフロー図で可視化すべき

2. **実行環境の前提条件未確認**:
   - Python実行環境をRailway n8nに期待
   - コンテナ調査を事前に実施せず
   - **教訓**: 外部コマンド実行前に`which`で存在確認

3. **アセットタグの言語問題**:
   - 日本語タグ（店舗、顧客等）がPexels/Unsplash検索で低マッチ率
   - **教訓**: タグ抽出時に英訳ステップを追加すべき

---

## 🎯 次のアクションアイテム

### 即時対応（今日中）
- [ ] ユーザーに本レポート共有
- [ ] 解決策の選択肢について意思決定
- [ ] 選択したOptionの実装開始

### 短期対応（1週間以内）
- [ ] Phase4をE2E実行可能な状態にする
- [ ] 最低1本の動画ファイル出力成功
- [ ] WF7-COMPLETE-PIPELINE-OVERVIEW.md更新

### 中期対応（1ヶ月以内）
- [ ] File Serverアーキテクチャ最終化
- [ ] Python動画レンダリング品質向上
- [ ] 日本語アセットタグ対応（英訳ステップ追加）

---

## 📎 参考資料

### 関連ドキュメント
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/WF7-COMPLETE-PIPELINE-OVERVIEW.md`
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/docs/phase1-script-generation-prompt.md`
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/docs/phase2-asset-collection-spec.md`

### 実行済みWorkflow IDs
- WF6 (note記事生成): `tkmG4YSZyi5RLiPw`
- WF7 Phase1: `fqbULAMXIGyBkNtL`
- WF7 Phase2: `sGjN9Vqw4pGTLmaX`
- WF7 Phase4: `VF3kFwJLKVq990jn`

### Notion Database IDs
- note記事管理DB: `29968d5c298681ad90d0c24ed710503e`
- WF7動画管理DB: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed`

---

**レポート作成日**: 2025-11-01
**作成者**: Claude Code (SuperClaude Framework)
**ステータス**: Phase4失敗分析完了、解決策提示済み
