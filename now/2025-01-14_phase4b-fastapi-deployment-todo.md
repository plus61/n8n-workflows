# WF7 Phase4b TODO手順書

**参照元**: `now/CURRENT_STATE.md`（ソース・オブ・トゥルース）  
**目的**: Phase4b再設計後のデプロイとテストを安全に完了させ、Phase4統合テストを再開できる状態に戻す。

---

## 前提チェック

1. `workflows/wf7-video-renderer/render_server.py` に `/generate-single-video` 実装済みであること（lines 200-433）。  
2. `Dockerfile.fastapi` と `railway.fastapi.json` がプロジェクトルートに存在すること。  
3. Phase4cワークフロー（ID `tJNe4gkuv0vxe2Oy`）が有効化され、Webhook自動登録が成功していること。  
4. `CURRENT_STATE.md` に記載の禁止事項（26ノード版JSONや旧テストスクリプトの使用禁止など）を遵守すること。

---

## TODO 1: FastAPIサーバーのRailwayデプロイ

- RailwayでFastAPI用サービスを作成し、`Dockerfile.fastapi` をビルド対象にする。既存サービスを流用する場合はn8nとプロセスが分離されているか確認。  
- `railway.fastapi.json` の設定を用いて環境変数・ボリュームを反映。  
- デプロイ完了後、`/health` で200を確認し、公開URL（例: `https://wf7-fastapi-xxxx.up.railway.app`）を取得。  
- 取得URLを `DECISIONS.md` または `CURRENT_STATE.md` へ記録し、メンバーが参照できるようにする。

---

## TODO 2: Phase4bワークフロー修正（ID `hfhZijyKIt1DjI1V`）

1. Node 2 をPython Code NodeからHTTP Request Nodeへ置換。  
2. URL: `{FastAPI_URL}/generate-single-video`  
3. Method: POST、Headers: `Content-Type: application/json`  
4. Body:
   ```json
   {
     "section": "{{ $json.section }}",
     "duration": {{ $json.duration }},
     "image_url": "{{ $json.image_url }}",
     "motion_prompt": "{{ $json.motion_prompt }}",
     "text": "{{ $json.text }}",
     "script_id": "{{ $json.script_id }}"
   }
   ```  
5. MCPツール（`n8n_update_partial_workflow`）で編集し、UI上での手編集は避ける。

---

## TODO 3: テストシーケンス

1. **単一スライドテスト**  
   - `now/2025-01-14_11-45_Phase4b-FastAPI-Endpoint-Design.md` のテストペイロードを使用し、エンドポイント単体で動画Base64が返るか確認。  
   - 失敗時はRailwayログでFFmpeg実行ログやCloudinaryダウンロードの状態を確認。

2. **Phase4a → Phase4b 連携テスト**  
   - Phase4a Webhookを起動し、7スライドすべてがPhase4bで動画化されることを確認。  
   - `test-phase4b-pindata-for-phase4c.json` 等、最新テストデータを使用。

3. **Phase4c 結合テスト**  
   - Phase4b出力をPhase4c（10ノード版）へ渡し、`test-phase4c-new.sh` でconcatが成功するか確認。  
   - 出力動画にCTAや字幕が含まれているか目視チェックを1回実施。

---

## TODO 4: ドキュメント更新と統合テスト再開

1. `now/CURRENT_STATE.md` の「重要な状態変更」「進捗状況」「次のアクション」を最新化。  
2. RailwayデプロイURLとテスト結果を `DECISIONS.md` や `Phase4b-Test-Results` 系ファイルに追記。  
3. Phase4統合テスト（Phase4a→b→c→最終動画）を再開し、結果を `docs/testing/WF7-Phase4-最終総合テスト実行結果.md` に反映。  
4. 完了後、マーケ用動画クオリティの検証（LINE誘導の成果測定）を別タスクとして切り出す。

---

## 失敗時のリカバリガイド

- **FastAPIデプロイ失敗**: `docker build -f Dockerfile.fastapi .` をローカル実行して再現、もしくはRailway buildログで依存関係の不足を特定。  
- **HTTP Request Nodeエラー**: durationやURLバリデーションに引っ掛かっていないかをレスポンスで確認。必要に応じて入力データを調整。  
- **Phase4c結合失敗**: 古いスクリプトを使用していないか、動画順序に乱れがないかをチェック。`wf7-phase4c-e2e-test-execution-guide.md` を参照。

---

これらを順に実施すれば、Phase4bのブロッカーを解消し、Phase4全体の自動動画生成ラインを再稼働できます。
