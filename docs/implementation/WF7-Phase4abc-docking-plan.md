# WF7 Phase4a/b/c Docking 計画仕様書

## 1. ドキュメント情報
- 作成日: 2025-11-08
- 対象WF: WF7 Phase4 - V2 Fixed (`SDO8X6oR5W5y2s6A`)
- 実装環境: Railway n8n (https://n8n-python-production-344b.up.railway.app/)
- 参照資料: `WF7-Phase4-FAL実装変更点.md`, `Phase4-FAL移行-要件定義.md`, `docs/implementation/WF7-Phase4a-n8nワークフロー実装ガイド.md`, `docs/implementation/WF7-Phase4c-n8nワークフロー実装ガイド.md`, `docs/knowledge/wf7-phase4-troubleshooting-guide.md`

## 2. 背景と目的
Phase3までで整備したNotionスクリプトDB／Google Drive連携を前提に、Phase4a (スライド画像生成)・Phase4b (FAL Image-to-Video)・Phase4c (FFmpeg結合) を既存WF7 Phase4ワークフローへ段階的にドッキングする。Creatomate依存を廃止し、FAL.ai + 内製FFmpegのハイブリッド構成を本番稼働させる。

## 3. スコープ
- **In Scope**: Phase4a/b/cノード配置、データ契約定義、モニタリング／テスト計画、リリース手順
- **Out of Scope**: Phase2-3プロンプト改修、Phase5 SNS配信、Railway以外へのインフラ移行

## 4. 現状整理
- Workflow `SDO8X6oR5W5y2s6A` はFAL `/compose` APIを単一ペイロードで呼び出す暫定構成（参照: `workflows/wf7-sns-video-automation/PHASE4_FAL_API_STATUS.md`）
- 待機ノードやタイムアウト設定は `docs/knowledge/wf7-phase4-troubleshooting-guide.md` に従い修正済みだが、Phase4a/b/cの多段構成は未導入
- `workflows/wf7-video-renderer/` 配下に `phase4a_slide_generator.py`, `phase4c_ffmpeg_concat.py` が配置済み

## 5. 目標状態アーキテクチャ
```
Notion WF7_Scripts (motion_prompts/duration_config/visual_elements/brand_colors)
   ↓ (Webhook: script_id)
Phase4a: Pillow Slide Generator (Code Node) → Google Drive image assets
   ↓ (slides_metadata[7])
Phase4b: FAL image-to-video (7並列) → fal_video_urls[7]
   ↓ (videos_metadata)
Phase4c: FFmpeg concat (Python Code) → final_video.mp4
   ↓
Phase5: SNS投稿 / Notion Hub更新
```

## 6. 実装マイルストーン
| Stage | 期間目安 | 内容 | 出口判定 |
|-------|---------|------|-----------|
| S0 | 0.5🍅 | 既存WFバックアップ & version 73 snapshot | `mcp__n8n-mcp__n8n_get_workflow` でJSON保存 |
| S1 | 2🍅 | Phase4aノード群追加・slide generator動作確認 | 7枚PNG → Google Driveリンク生成 |
| S2 | 2🍅 | Phase4b実装 (FAL 7本並列 + ステータスポーリング) | 各セクションで `video_url` 取得 |
| S3 | 1🍅 | Phase4c FFmpeg結合ノード追加 | `/tmp` で結合結果 + サイズログ |
| S4 | 1🍅 | E2E統合テスト + モニタリング設定 | Execution #720以降で成功ログ |

## 7. Phase別ドッキング設計
### 7.1 Phase4a (Slide Generator)
- **入口**: Webhook `/wf7-phase4a-slide-generator` (POST bodyに `script_id`)
- **取得**: Notion DB Queryで `motion_prompts`, `duration_config`, `visual_elements`, `brand_colors`, `font_sizes` を取得
- **処理**: `Code - Generate Slides with Pillow` → `Split Out` → `Google Drive Upload` → `Aggregate`
- **出力契約**:
```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "motion_prompt": "dramatic zoom in effect...",
      "drive_file_id": "1abc...",
      "drive_url": "https://drive.google.com/file/d/1abc.../view",
      "image_url": "https://drive.google.com/uc?export=download&id=1abc..."
    }
  ]
}
```
- **Dockingポイント**: 既存WF冒頭の「Notionスクリプト取得」「データ統合」ノード後に `Set - Phase4a Payload` を挿入し、Phase4bに渡す
- **完了条件**: 7枚生成成功、Google Driveレスポンス200、Notion `status` を `rendering` へ更新

### 7.2 Phase4b (FAL Image-to-Video)
- **目的**: Phase4a出力7枚を各3-20秒の動画へ変換
- **ノード案**:
  1. `Split In Batches (size:1)` → 7セクションを逐次処理
  2. `HTTP Request - Submit to FAL` (POST `/fal-ai/ffmpeg-api/compose`) 画像＋motion_prompt＋durationを送信
  3. `Wait 5s` + `HTTP Request - Fetch Status` (request_id) でポーリング
  4. `Check Render Status` → `Get Result URL` (正しい `=https://queue.fal.run/.../compose/requests/{{request_id}}`)
  5. `Merge` で `videos_metadata` 配列へ集約
- **ペイロード雛形**:
```json
{
  "image_url": "https://drive.google.com/uc?...",
  "duration": 10,
  "motion_prompt": "smooth slide transition, calm professional tone, steady camera"
}
```
- **Dockingポイント**: 現行の単一「Submit to FAL」ノード (`f21d892c-8100-4b31-ba7c-9455a31e9cf5`) を `Split → Compose` 構成に差し替え。`Payload Builder` ノード (`9f3272e3-7d13-4c0a-b2a2-684e62a2b642`) を拡張し、セクション配列を生成
- **エラーハンドリング**: `Retry Counter` (max 5) + `Wait Before Retry` (5s) で指数バックオフ、失敗時 `Notion status = error`

### 7.3 Phase4c (FFmpeg Concat)
- **入口**: `videos_metadata` (7本) + `script_id`
- **ノード**: `Code - FFmpeg Concat` (python `phase4c_ffmpeg_concat.py` 呼び出し)
- **主要パラメータ**: `/tmp` に一時DL、`ffmpeg -y -safe 0 -f concat -i concat.txt -c copy`
- **出力契約**:
```json
{
  "success": true,
  "script_id": "29b68d5c-2986-817f-xxxx",
  "output_video_path": "/tmp/wf7_phase4c_x/final_video.mp4",
  "public_url": "https://drive.google.com/file/d/.../view",
  "videos_count": 7,
  "total_duration": 80
}
```
- **Dockingポイント**: Phase4b集約後にCodeノードを配置し、結果を Phase5 uploader へ渡す。完了後Notion `status` を `completed` に更新

## 8. データフロー & ペイロード定義
| ステップ | 主キー | 必須フィールド | 備考 |
|---------|--------|---------------|------|
| Notion → Phase4a | `script_id` | hook_texts, introduction_text, main_point_{1..3}, summary_text, cta_text, motion_prompts, duration_config, visual_elements, brand_colors | Notion DB: WF7_Scripts |
| Phase4a → Phase4b | `slides_metadata[]` | section, duration, image_url, motion_prompt | 順序維持 (hook→cta) |
| Phase4b → Phase4c | `videos_metadata[]` | section, duration, video_url, fal_request_id, render_elapsed | 7件固定 |
| Phase4c → Phase5 | `final_video` | public_url, total_duration, concat_log, drive_file_id | FFmpegログ含む |

## 9. リリース手順 (推奨)
1. **Preparation**: `mcp__n8n-mcp__n8n_get_workflow` で現行JSONをバックアップ
2. **Phase4a merge**: UIでノード追加 → `Execute Workflow` (テストモード) で `slides_metadata` を確認
3. **Phase4b merge**: FAL APIキー確認、`Split In Batches` + `HTTP Request` ノード追加、Execution #experimental で7本生成
4. **Phase4c merge**: Codeノード + Google Driveアップロード + cleanup処理を追加
5. **E2E validation**: Webhook実行 → Notion/Drive/FALログ突合、`docs/testing/Phase4a-テスト結果レポート.md` 手順を流用
6. **Version freeze**: 成功後 `mcp__n8n-mcp__n8n_update_full_workflow` / Git commit

## 10. テスト計画
- **Unit**: `python phase4a_slide_generator.py`, `python phase4c_ffmpeg_concat.py`
- **API Mock**: FAL `/compose` を `curl` で事前確認し、`options.timeout=300000` が効いていることを `docs/knowledge/wf7-phase4-troubleshooting-guide.md` の手順で検証
- **Integration**: 7枚画像→7動画→結合のシリアル実行ログを `execution.json` で採取
- **Regression**: 旧Creatomate経路が無効化されていることを `WF7-Phase4-FAL実装変更点.md` のチェックリストで確認

## 11. モニタリング & 運用
- `Wait for Processing` ノードは `resume = time (5s)` に固定し、`retryCount >= 5` でSlack通知（n8n Slack Nodeを追加）
- FAL APIレスポンスを `Notion: Render Logs` DBにappend（`script_id` 単位）
- FFmpeg結合エラー時: `/tmp/wf7_phase4c_*` ディレクトリのログを残し、`videos_metadata` をNotionへ保存して手動リトライ可能にする
- 実行後Runbook: `mcp__n8n-mcp__n8n_list_executions(limit:3)` で最新実行を確認し、`status != success` を検出したら即アラート

## 12. リスクと対策
| リスク | 影響 | 対策 |
|--------|------|------|
| Notion新カラム未入力 | Phase4aでフォーマット崩壊 | ブランドカラー／durationのデフォルト値をコード側に定義し、バリデーションノードで欠損検知 |
| FAL API同時実行制限 (429) | Phase4bでレンダリング失敗 | `Split In Batches` により逐次化、`Retry Counter` + `Wait Before Retry` で指数バックオフ |
| FFmpeg concat codec mismatch | Phase4c失敗 | 事前に `ffprobe` チェック、`-c copy` 失敗時に `-c:v libx264 -c:a aac` fallback をスクリプトへ実装 |
| Railway `/tmp` 容量超過 | 結合処理停止 | `phase4c_ffmpeg_concat.py` で `temp_dir` を確実に削除し、1実行 >1GB の場合Slack通知 |

## 13. 成果物チェックリスト
- [ ] 本仕様書（`docs/implementation/WF7-Phase4abc-docking-plan.md`）
- [ ] Phase4aノード構成スクリーンショット（Notion添付）
- [ ] Phase4bペイロードJSONサンプル
- [ ] Phase4c実行ログ（FFmpeg stdout/stderr）
- [ ] Notionステータス自動更新ノード定義

## 14. 次のアクション
1. S0バックアップ: `scripts/export_workflow.sh SDO8X6oR5W5y2s6A`（要CLI）を実行
2. Phase4aノードを `docs/implementation/WF7-Phase4a-n8nワークフロー実装ガイド.md` に沿ってUIへ配置
3. Phase4b実装ガイド作成（未着手）を優先度P0で起票
4. FFmpeg結合結果をGoogle Driveへ自動アップロードする `HTTP Request` ノードの仕様確定

---
本計画仕様書に従い、Phase4a/b/cの段階的リリースを進める。

