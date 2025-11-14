# WF7: SNS動画化ワークフロー要件定義書（スクリプト自動生成版）

> ⚠️ **ステータス**: このドキュメントはフルスペック版（v2.0）です。
>
> **現行実装版**: [WF7_SNS動画化_要件定義書_MVP版.md](./WF7_SNS動画化_要件定義書_MVP版.md) v2.1
>
> **アーカイブ**: [_archive/WF7/](./_archive/WF7/)

**プロジェクト**: MEO集客自動化 - コンテンツ生成パイプライン
**対象ワークフロー**: WF7（SNS動画化）
**改訂日**: 2025-10-29
**作成者**: Codex
**バージョン**: 2.0（スクリプトレンダリング版・フルスペック）
**実装ステータス**: 保留（MVP版で効果検証中）

---

## 目次

1. [背景と目的](#背景と目的)  
2. [ビジネスゴールとKPI](#ビジネスゴールとkpi)  
3. [システム全体像](#システム全体像)  
4. [機能要件](#機能要件)  
5. [非機能要件](#非機能要件)  
6. [コンポーネント選定](#コンポーネント選定)  
7. [データ設計](#データ設計)  
8. [ワークフロー詳細](#ワークフロー詳細)  
9. [コストモデル](#コストモデル)  
10. [運用と保守](#運用と保守)  
11. [リスクと対応策](#リスクと対応策)  
12. [導入ロードマップ](#導入ロードマップ)

---

## 背景と目的

- CapCutなどGUI依存ツールを排除し、CLI/スクリプト完結の動画生成ラインを構築する。  
- note記事（WF6アウトプット）から縦型ショート動画を安定して量産し、X・Instagram・TikTokに同一テンプレを展開する。  
- OSSベース（Python＋ffmpeg）を中心に据え、再現性とクラウド実行（夜間バッチ）を担保する。

---

## ビジネスゴールとKPI

| 目的 | KPI | 目標値 | 計測方法 |
|------|-----|--------|----------|
| 制作コスト削減 | 1本あたり実コスト | 80円以下 | 工数×時給 + API費用をSheetsで集計 |
| 制作速度向上 | 1バッチ(4本)所要時間 | 45分以内 | n8n/CLIジョブ完了時間 |
| 投稿頻度維持 | 週次動画本数 | 5本以上 | Notion「動画管理DB」集計 |
| 品質確保 | 完走率 | 35%以上 | SNS Insightsでモニタリング |

---

## システム全体像

```
WF6(note台本)
   ↓ Webhook
[n8n Scenario A] 台本整形・テンプレ設定
   ↓ Google Sheets (SNS動画マスタ)
[n8n Scenario B] 素材取得 + メタ生成
   ↓ Drive / assets/
[n8n Scenario C] 音声・字幕生成（任意）
   ↓ voice.wav / subtitle.srt
[Batch Runner] Python CLI (moviepy + ffmpeg)
   ↓ MP4(1080x1920) / thumb.jpg
[Notion 更新] 動画管理DB
   ↓
WF8（SNS投稿自動化）へURL・メタ情報を引き渡し
```

- バッチランナーはCloud Run/Functions/EC2でも実行できるようDocker化を前提。  
- テンプレートはJSON/CSV管理し、シーン構成・テロップ位置・効果音をパラメータ化。

---

## 機能要件

### FR-1: 台本整形

- **トリガー**: WF6完了Webhook / 毎日09:00バッチ  
- **入力**: `articleId`, `title`, `keyPoints[]`  
- **処理**:
  1. GPT-4o-miniで30-45秒のスクリプト生成（セクション: Hook / Pain / Solution / CTA）  
  2. セクションごとにテロップ文、読み上げ文、推奨アセットタグを生成  
  3. Google Sheets「SNS動画マスタ」に行を追加  
- **出力**: `script.json`（S3/Drive保管）、Sheets更新

### FR-2: アセット取得

- **トリガー**: Sheets追加時  
- **処理**:
  1. アセットタグからPexels/Unsplash APIで縦型画像/動画を取得  
  2. ブランドライブラリ（Drive固定素材）を参照し不足分を補完  
  3. 取得ファイルをDrive `assets/{articleId}/` に保存し、パスをSheetsに書き戻す  
- **出力**: `assets.json`（使用素材リスト）

### FR-3: 音声・字幕生成（任意）

- **条件**: `needsNarration = TRUE`  
- **処理**:
  1. VOICEVOX CLI（docker）またはOpenAI TTSを呼び出し音声生成  
  2. whisper.cppで音声からテキスト化→SRT作成  
  3. 生成物をDriveに保存し、SheetsにURLを記録  
- **出力**: `voice.wav`, `subtitle.srt`

### FR-4: 動画レンダリング

- **仕組み**:
  - Pythonスクリプト `render_video.py` をCLIで実行  
  - `script.json`, `assets.json`, `subtitle.srt` を入力に、moviepy + ffmpegでレンダリング  
  - シーン定義はテンプレJSON（位置、フォント、カラー、アニメーション）を読み込み  
  - オプションでRemotion CLI（Node.js）に差し替えられるようアダプタを用意

- **処理ステップ**:
  1. シーンごとに背景アセット、テキスト、B-rollを合成  
  2. BGMループ＆音量調整（ffmpeg filter）  
  3. 字幕がある場合は画像ベースではなくburn-in（ffmpeg drawtext）で合成  
  4. エンコード設定: `ffmpeg -vf scale=1080:1920 -r 30 -c:v libx264 -preset fast -crf 23`

- **出力**: `video.mp4`, `thumbnail.jpg`

### FR-5: メタデータ登録とWF8連携

- **処理**:
  1. Notion「動画管理DB」へファイルURL、生成時刻、テンプレIDを登録  
  2. Slack通知 + WF8用Webhook（動画ID、SNS推奨コピー、ハッシュタグ）送信  
  3. Sheetsステータスを `Ready` に更新

### FR-6: エラー検知・リトライ

- n8nシナリオ・バッチランナーともに最大3回リトライ  
- Python CLIは構造化ログ（JSON）をCloud Logging / Lokiに送信  
- 失敗時はNotionのステータスを `Error` に更新し、Slackで通知。再実行CLIを用意。

---

## 非機能要件

- **コスト**: 月2,000円以内（API課金 + BGM定額）  
- **スループット**: 20本/日（夜間実行時、同時4ジョブで3時間以内）  
- **可搬性**: Dockerコンテナ化し、Mac/Ubuntu/Cloud Runで共通稼働  
- **信頼性**: 自動生成成功率95%以上、失敗時再実行で100%到達  
- **監視**: n8nダッシュボード + Slack通知 + CloudWatch（任意）

---

## コンポーネント選定

| レイヤ | ツール | 理由 | コスト |
|--------|--------|------|--------|
| 台本整形 | OpenAI GPT-4o-mini / Claude Haiku | 低単価・レスポンス安定 | 0.3円/本前後 |
| 素材取得 | Pexels API / Unsplash API | 無料・商用利用可 | 0円 |
| 音声 | VOICEVOX Docker / OpenAI TTS無料枠 | ライセンス明確・自前完結 | 0円 |
| 字幕 | whisper.cpp + ffmpeg | OSS・CPU動作 | 0円 |
| 動画レンダ | Python 3.11 + moviepy + ffmpeg | CLI完結・テンプレ組みやすい | 0円 |
| 代替レンダ | Remotion CLI（Node.js） | Reactテンプレで拡張性 | OSS |
| オーケストレーション | n8n（Railway） | 既存環境で制御可能 | 既存枠内 |
| ストレージ | Google Drive / S3（任意） | 既存利用 | 0円 |
| 管理DB | Google Sheets / Notion | 既存運用 | 0円 |

---

## データ設計

### Google Sheets: `SNS動画マスタ`

| カラム | 型 | 説明 |
|--------|----|------|
| `articleId` | TEXT | 元note記事ID |
| `scriptId` | TEXT | `articleId`-`YYYYMMDDHH` |
| `templateId` | TEXT | 使用テンプレ（hook01等） |
| `segmentIndex` | INT | セグメント番号 |
| `sceneType` | TEXT | hook / pain / solution / cta |
| `caption` | TEXT | テロップ文 |
| `narration` | TEXT | ナレーション文 |
| `startSec` | INT | 開始秒 |
| `durationSec` | INT | セグメント長 |
| `assetTag` | TEXT | 素材取得タグ |
| `assetPath` | TEXT | 保存先パス |
| `voicePath` | TEXT | 音声ファイルパス |
| `status` | ENUM | Draft / AssetsReady / Rendered / Posted / Error |

### Notion: `動画管理DB`

- プロパティ: `videoId`, `articleId`, `templateId`, `renderedAt`, `videoUrl`, `thumbUrl`, `subtitleUrl`, `renderStatus`, `retryCount`, `snsReadyAt`

---

## ワークフロー詳細

1. **受信〜台本整形**  
   - n8n Scenario AがWF6 Webhookを受信 → GPT APIで台本生成 → Sheets追記 → script.json保存。
2. **素材収集**  
   - Scenario BがSheetsの新規追加を検知 → Pexels APIで素材ダウンロード → Driveに保存 → assets.json作成。
3. **音声/字幕生成**  
   - Scenario Cが`needsNarration`を条件にVOICEVOX Dockerをコール → wav生成 → whisper.cppでSRT作成。
4. **レンダリング**  
   - Cronで夜間にPython CLIを実行（`python render_video.py --script script.json --assets assets.json --out video.mp4`）  
   - CLI内部でmoviepy → ffmpegでエンコード。中間ファイル（raw clips）はtmpディレクトリで管理し完了後削除。
5. **登録・通知**  
   - CLI終了時にNotion APIへ結果をPOSTし、Slack通知を出す。  
   - WF8が毎日20:00に`renderStatus = Rendered` の動画を取得し投稿テキストと合わせて配信。

---

## コストモデル

| 項目 | 月間費用目安 | 備考 |
|------|---------------|------|
| GPT API（台本整形） | 300〜500円 | 月150本想定 |
| 音声/TTS | 0円 | VOICEVOX利用 |
| 字幕 | 0円 | whisper.cpp |
| 動画レンダ | 0円 | 自前Python + ffmpeg |
| 素材API | 0円 | 無料枠内利用 |
| BGM | 0〜2,000円 | フリー音源なら0円 |
| インフラ | 0円 | 既存Railway/GDrive枠内 |
| **合計** | **〜2,500円/月** | BGM有料プラン込 |

---

## 運用と保守

- Dockerイメージ（`wf7-renderer`）をGitHub Actionsで自動ビルドし、ランナーに配布。  
- PythonスクリプトとテンプレJSONはGit管理し、Pull Requestベースで更新。  
- 週次でSheetsの`Error`行を確認し、台本/素材/レンダ失敗の分類をレビュー。  
- 月次でテンプレ効果測定（完走率・CTR）をLooker Studioに集約し、テンプレ改修計画を立案。

---

## リスクと対応策

| リスク | 影響 | 対策 |
|--------|------|------|
| ffmpegフィルタ指定ミス | 書き出し失敗 | 単体テスト（pytest）でフィルタ文字列を検証 |
| 素材不足 | 品質低下 | 事前にブランドアセットを200点以上用意、API失敗時はフォールバックを適用 |
| GPT出力ばらつき | 構成崩壊 | プロンプトにJSONスキーマを指定し、pydanticでバリデーション |
| whisper性能不足 | 認識誤り | 読み上げ速度を0.95xに調整、必要に応じて手動校正 |
| Docker環境差異 | 本番で失敗 | ローカル・ステージング・本番の3環境で同一イメージを使用 |
| APIレート制限 | 素材取得遅延 | キャッシュ層を実装し、前日分の素材を事前取得 |

---

## 導入ロードマップ

1. **Week 1**: 設計・テンプレ定義  
   - スクリプト仕様書、テンプレJSON、Sheets/Notionスキーマを確定  
   - PythonレンダラのPoC（1シーン）実装
2. **Week 2**: オーケストレーション構築  
   - n8n 3シナリオ（台本/素材/音声）を実装  
   - Dockerfile + ffmpeg環境整備、CIでテスト実行
3. **Week 3**: パイロット運用  
   - 5本の動画をバッチ生成、レビュー＆調整  
   - KPIダッシュボード構築、Slack通知導線整備
4. **Week 4**: 本番稼働  
   - 週5本の定常運用へ移行、WF8連携を本番化  
   - メンテ運用ガイドとトラブルシューティング手順書を確立

---

この要件定義書を基に、CLIベースの動画生成パイプラインを整備し、低コスト＋高再現性でSNS向け動画を量産できる体制を構築する。
