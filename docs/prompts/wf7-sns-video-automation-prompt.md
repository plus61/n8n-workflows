# WF7 SNS動画化ワークフロー実装プロンプト

**作成日**: 2025-10-29
**ベース要件**: WF7_SNS動画化_要件定義書.md v2.0（フルスペック版）
**カテゴリー**: ワークフロー作成（新規・複雑）
**推定所要時間**: 120-180分

---

## 📝 実行プロンプト

```markdown
@mcp-sequential-thinking
@n8n-workflows-docs
@n8n-mcp

CLIベースのSNS動画自動生成パイプライン（WF7）を段階的に設計・実装したいです。

【背景・現状】
- WF6（note記事生成）が完了すると、Webhookで台本データを受信
- CapCutなどGUIツール依存を排除し、完全スクリプト化を実現したい
- 現在はMVP版（v2.1）で効果検証中だが、フルスペック版への移行を検討
- 月150本の動画を生成し、X/Instagram/TikTokに展開する計画
- 既存環境: n8n on Railway、Google Drive、Notion、Slack

【目標・要件】
目的: note記事から縦型ショート動画（1080×1920）を自動生成し、SNS投稿を準備

## トリガー
- WF6完了Webhook（articleId, title, keyPoints[]を受信）
- 毎日09:00の定時バッチ実行（任意）

## 入力データ構造
```json
{
  "articleId": "note-abc123",
  "title": "MEO対策の基本",
  "keyPoints": [
    "Googleビジネスプロフィールの最適化",
    "口コミ管理の重要性",
    "写真投稿の効果"
  ]
}
```

## 処理フロー（5段階構成）

### Phase 1: 台本整形（n8n Scenario A）
1. Webhook受信またはScheduledトリガー
2. GPT-4o-mini APIで30-45秒の動画スクリプト生成
   - セクション: Hook（0-10秒）/ Pain（10-20秒）/ Solution（20-35秒）/ CTA（35-45秒）
   - 各セクションに: テロップ文、読み上げ文、アセットタグを生成
3. Google Sheets「SNS動画マスタ」にスクリプト保存
4. script.jsonをGoogle Driveに保存

### Phase 2: 素材取得（n8n Scenario B）
1. Sheets新規追加をトリガーに起動
2. アセットタグから以下APIで素材取得:
   - Pexels API（縦型動画・画像）
   - Unsplash API（フォールバック用）
3. ブランドライブラリ（Drive固定素材）で補完
4. 取得素材をDrive `assets/{articleId}/` に保存
5. assets.json生成、Sheetsにパスを記録

### Phase 3: 音声・字幕生成（n8n Scenario C）※任意
条件: `needsNarration = TRUE` の場合のみ
1. VOICEVOX Docker CLIで音声生成（voice.wav）
2. whisper.cppでテキスト化→SRT字幕作成（subtitle.srt）
3. DriveにアップロードしURLをSheetsに記録

### Phase 4: 動画レンダリング（Python CLI Batch）
**実行環境**: Docker（wf7-renderer）
**ツール**: Python 3.11 + moviepy + ffmpeg

実行コマンド例:
```bash
python render_video.py \
  --script /path/to/script.json \
  --assets /path/to/assets.json \
  --subtitle /path/to/subtitle.srt \
  --template hook01 \
  --out /path/to/video.mp4
```

処理内容:
1. テンプレートJSON読み込み（シーン構成、フォント、位置、アニメーション）
2. moviepyでシーンごとに背景・テキスト・B-roll合成
3. BGMループ＋音量調整（ffmpeg filter）
4. 字幕burn-in（ffmpeg drawtext）
5. エンコード: `ffmpeg -vf scale=1080:1920 -r 30 -c:v libx264 -preset fast -crf 23`
6. サムネイル生成（thumbnail.jpg）

出力:
- video.mp4（1080×1920、30fps、H.264）
- thumbnail.jpg（1080×1920）

### Phase 5: メタデータ登録・WF8連携
1. Notion「動画管理DB」へ登録
   - videoId, articleId, templateId
   - renderedAt, videoUrl, thumbUrl
   - renderStatus: "Rendered"
2. Slack通知（#動画生成完了）
3. WF8用Webhook送信（videoId, SNS推奨コピー、ハッシュタグ）
4. Sheetsステータスを `Ready` に更新

## 出力
- Google Sheets: ステータス更新済み
- Google Drive: script.json, assets.json, voice.wav, subtitle.srt, video.mp4, thumbnail.jpg
- Notion: 動画管理DB新規レコード
- Slack: 完了通知
- WF8: 投稿準備完了データ

【制約条件】
- コスト: 月2,500円以内（GPT API 300-500円 + BGM 0-2,000円）
- スループット: 夜間バッチで20本/日（同時4ジョブ、3時間以内）
- パフォーマンス: 1バッチ（4本）45分以内、1本あたり実コスト80円以下
- 可搬性: Dockerコンテナ化（Mac/Ubuntu/Cloud Run共通稼働）
- 信頼性: 自動生成成功率95%以上、失敗時再実行で100%到達
- セキュリティ: Webhook署名検証必須、API認証情報の安全管理

【技術スタック】
- オーケストレーション: n8n（Railway）
- AI: OpenAI GPT-4o-mini / Claude Haiku
- 素材: Pexels API / Unsplash API（無料）
- 音声: VOICEVOX Docker / OpenAI TTS
- 字幕: whisper.cpp + ffmpeg
- レンダリング: Python moviepy + ffmpeg（Remotion CLI代替可）
- ストレージ: Google Drive
- DB: Google Sheets + Notion
- 通知: Slack

【依頼内容】

## 1. Sequential Thinkingで全体設計（30分）
タスク:
- 5つのPhaseの最適な実装順序を検討
- 各PhaseのMVP版（最小限の機能）を定義
- エラーハンドリング戦略（リトライ、フォールバック、通知）
- データフロー設計（各Phase間の依存関係とデータ受け渡し）
- パフォーマンス最適化ポイント（並列処理、キャッシュ、バッチサイズ）

質問事項:
- Phase 1-3はn8nで実装し、Phase 4はCloud Run/Functions/EC2で実行する構成が最適か？
- 音声生成（Phase 3）はオプション扱いで、スキップ可能にすべきか？
- Python CLIレンダラーとRemotionの使い分け基準は？

## 2. n8n-workflows-docsで参考例探索（30分）
Zie619から以下のパターンを検索:
- Webhook受信 → AI API呼び出し → Sheets書き込みのパターン（10例）
- Google Drive素材管理とファイルアップロードのベストプラクティス（5例）
- 外部CLI/Docker呼び出しの実装例（HTTP Request / Execute Command）（5例）
- バッチ処理とスケジューリングのパターン（5例）
- エラーハンドリングとSlack通知の標準実装（10例）

重点調査項目:
- GPT-4o-miniでJSONスキーマ指定してスクリプト生成する実装
- Pexels/Unsplash APIの効率的な呼び出しとレート制限対策
- 大量ファイルアップロード時のDrive API最適化
- n8nからDockerコンテナを起動する方法

## 3. n8n-mcpで段階的実装（60-90分）

### Step 3-1: Phase 1実装（台本整形）
実装ノード構成:
1. Webhook / Schedule Triggerノード
2. Set Variable（入力データ整形）
3. OpenAI / Anthropic API（GPT-4o-mini呼び出し）
   - プロンプト設計: JSONスキーマ指定
   - pydanticバリデーション用のスキーマ定義
4. Google Sheets（行追加）
5. Google Drive（script.json保存）
6. Error Triggerノード → Slack通知

テストデータ:
```json
{
  "articleId": "note-test001",
  "title": "MEO対策の基本",
  "keyPoints": ["最適化", "口コミ", "写真"]
}
```

バリデーション:
- スクリプト生成時間: 5秒以内
- JSON形式の正確性: pydanticで検証
- Sheets書き込み成功率: 100%

### Step 3-2: Phase 2実装（素材取得）
実装ノード構成:
1. Google Sheets Triggerノード（新規行追加を検知）
2. Loop Over Items（各アセットタグを処理）
3. HTTP Request（Pexels API → Unsplash APIフォールバック）
4. Google Drive（ファイルアップロード）
5. Code（assets.json生成）
6. Google Sheets（パス書き戻し）
7. Error Trigger → Slack通知

API設定:
- Pexels API: orientation=portrait, size=large
- Unsplash API: orientation=portrait
- レート制限: 3 req/sec、エクスポネンシャルバックオフ実装

バリデーション:
- 素材取得成功率: 95%以上
- フォールバック機能: Pexels失敗時Unsplash自動切替
- 処理時間: 5素材で30秒以内

### Step 3-3: Phase 3実装（音声・字幕生成）※オプション
実装ノード構成:
1. IFノード（needsNarration判定）
2. HTTP Request（VOICEVOXコンテナAPI呼び出し）
   - エンドポイント: `POST http://voicevox:50021/audio_query`
3. Code（whisper.cpp実行スクリプト）
4. Google Drive（voice.wav, subtitle.srt保存）
5. Google Sheets（URL更新）

代替実装:
- OpenAI TTS APIを使った実装も並行して用意
- コスト比較: VOICEVOX（無料）vs OpenAI TTS（$0.015/1K chars）

### Step 3-4: Phase 4実装（動画レンダリング呼び出し）
実装ノード構成:
1. HTTP Request（Cloud Run / Lambda / EC2エンドポイント呼び出し）
   - POST `/render-video`
   - Body: { scriptUrl, assetsUrl, subtitleUrl, templateId }
2. Wait（完了待機、最大30分）
3. Polling（ステータス確認、10秒間隔）
4. Google Drive（完成動画URL取得）

Python CLIレンダラー実装ガイド:
```python
# render_video.py スケルトン
import moviepy.editor as mp
import json

def load_config(script_path, assets_path):
    # script.json, assets.jsonを読み込み
    pass

def create_scene(template, segment):
    # moviepyでシーン生成
    # 背景、テキスト、B-rollを合成
    pass

def render_video(scenes, output_path):
    # ffmpegでエンコード
    # scale=1080:1920, fps=30, libx264
    pass

if __name__ == "__main__":
    # CLI引数パース
    # レンダリング実行
    pass
```

Docker化:
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install moviepy pillow requests
COPY render_video.py /app/
WORKDIR /app
ENTRYPOINT ["python", "render_video.py"]
```

### Step 3-5: Phase 5実装（メタデータ登録・連携）
実装ノード構成:
1. Notion API（動画管理DB新規ページ作成）
2. Slack通知（#動画生成完了）
3. HTTP Request（WF8へWebhook送信）
4. Google Sheets（ステータス更新: Ready）

Notionプロパティ設定:
```json
{
  "videoId": { "title": [{ "text": { "content": "video-abc123" } }] },
  "articleId": { "rich_text": [{ "text": { "content": "note-abc123" } }] },
  "templateId": { "select": { "name": "hook01" } },
  "renderedAt": { "date": { "start": "2025-10-29T12:00:00Z" } },
  "videoUrl": { "url": "https://drive.google.com/..." },
  "renderStatus": { "select": { "name": "Rendered" } }
}
```

## 4. バリデーションと最適化（30分）
実施項目:
- エンドツーエンドテスト（WF6 Webhook受信 → WF8連携完了まで）
- エラーケーステスト:
  - GPT API障害時のリトライ
  - Pexels/Unsplash API障害時のフォールバック
  - 動画レンダリング失敗時の通知とマニュアル再実行
- パフォーマンス計測:
  - Phase 1-3の合計実行時間（目標: 5分以内）
  - Phase 4の実行時間（目標: 10分/本）
  - 4本バッチの合計時間（目標: 45分以内）
- コスト検証:
  - GPT-4o-mini API: 1本あたり0.3円（150トークン想定）
  - 素材API: 0円（無料枠内）
  - 音声生成: 0円（VOICEVOX）
  - レンダリング: 0円（自前インフラ）
  - 合計: 80円/本以下を達成

品質基準:
- 動画生成成功率: 95%以上
- エラー自動復旧率: 80%以上（リトライ・フォールバックで）
- ユーザー介入なし完了率: 90%以上

【参考情報】
- 既存MVP版: `/WF7_SNS動画化_要件定義書_MVP版.md` v2.1
- アーカイブ: `/_archive/WF7/`
- n8nナレッジベース: `/docs/knowledge/n8n-workflow-construction-knowledge.md`
- ベストプラクティス: `/docs/best-practices.md`

【特に重視する点】
1. **段階的実装**: Phase 1→2→3→5を先行実装し、Phase 4（Python CLI）は後回しでも可
2. **エラーハンドリング**: 各Phaseで失敗時にSlack通知 + ステータス記録
3. **再実行可能性**: 各Phaseを独立したワークフローとし、任意のPhaseから再実行可能に
4. **コスト監視**: GPT API呼び出し数、レンダリング時間をNotion/Sheetsでトラッキング
5. **MVP版との互換性**: MVP版で検証済みの機能は優先的に実装

【成功の基準】
- [ ] 5つのPhaseすべてがn8nワークフローとして実装完了
- [ ] Python CLIレンダラーのDockerイメージをビルド可能
- [ ] エンドツーエンドテストで1本の動画生成に成功
- [ ] エラーハンドリングが全Phaseに実装済み
- [ ] コスト目標（80円/本以下）を達成
- [ ] ドキュメント完備（README, セットアップガイド、トラブルシューティング）
```

---

## 🎯 実行ガイド

### 前提条件
- [ ] n8n on Railway（アクセス権限あり）
- [ ] Google Sheets「SNS動画マスタ」作成済み
- [ ] Notion「動画管理DB」作成済み
- [ ] OpenAI API / Anthropic APIキー設定済み
- [ ] Pexels API / Unsplash APIキー設定済み
- [ ] Google Drive API認証設定済み
- [ ] Slack Webhook URL設定済み

### 実行手順
1. 上記プロンプトをコピー
2. Cursor / Claudeに貼り付け
3. MCPが起動し、Sequential Thinkingで設計開始
4. n8n-workflows-docsから参考例を自動検索
5. n8n-mcpで段階的に実装
6. 各Phaseごとにテスト実行
7. 完了後、ドキュメント生成

### 推定所要時間
- Phase 1実装: 30分
- Phase 2実装: 30分
- Phase 3実装: 20分
- Phase 5実装: 20分
- Phase 4準備（Python CLI）: 60分
- テスト・調整: 30分
- **合計**: 120-180分

### トラブルシューティング

#### よくある問題
1. **GPT API呼び出しエラー**
   - リトライロジック実装（最大3回）
   - Claude APIへのフォールバック設定

2. **素材取得失敗**
   - Pexels → Unsplash フォールバック
   - ブランドライブラリから固定素材を使用

3. **動画レンダリングタイムアウト**
   - Polling間隔を調整（10秒→30秒）
   - タイムアウト時間を延長（30分→60分）

4. **Notion API書き込みエラー**
   - プロパティ型の確認（titleはarray、urlはstring）
   - データベースIDの再確認

---

## 📋 チェックリスト

### プロンプト実行前
- [ ] 要件定義書（WF7）を再確認
- [ ] MVP版の実装状況を確認
- [ ] 必要なAPI認証情報を準備
- [ ] Google Sheets/Notionのスキーマを確認

### 実装中
- [ ] Sequential Thinkingの設計提案をレビュー
- [ ] 各Phaseの実装をテスト
- [ ] エラーハンドリングを確認
- [ ] パフォーマンスを計測

### 実装後
- [ ] エンドツーエンドテスト実行
- [ ] コスト計算（80円/本以下を確認）
- [ ] ドキュメント作成
- [ ] WF6, WF8との連携テスト

---

## 🔗 関連ドキュメント

- [WF7要件定義書（フルスペック版）](../../WF7_SNS動画化_要件定義書.md) - v2.0
- [WF7要件定義書（MVP版）](../../WF7_SNS動画化_要件定義書_MVP版.md) - v2.1
- [n8nワークフロー構築ナレッジ](../knowledge/n8n-workflow-construction-knowledge.md)
- [プロンプト設計指針書](../prompt-design-guide.md)
- [ベストプラクティス](../best-practices.md)

---

**作成者**: Claude Code
**レビュー**: 未実施
**ステータス**: 初版完成
