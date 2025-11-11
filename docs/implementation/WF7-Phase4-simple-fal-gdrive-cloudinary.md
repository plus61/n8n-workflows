# WF7 Phase4 最小構成（FAL + Google Drive + Cloudinary）

2025-11-10 更新  
対象: Phase4 の設計/検証に行き詰まったときに参照するシンプルな実装例  

---

## 🎯 ゴール

1. Webhook で `script_id` と 7 セクション分のテキストを受け取り、FAL の Image-to-Video モデルで 7 本の短い動画を生成する。  
2. 生成した各動画を Google Drive に保存し、参照用 URL を取得する。  
3. Google Drive からダウンロードした 7 本を FFmpeg 互換の FAL ユーティリティで結合し、Cloudinary に公開する。  
4. Webhook 応答では Google Drive / Cloudinary の URL と Cloudinary public ID を返す。  

> 使うアプリは **fal / Google Drive / Cloudinary** の3つだけ。Notion など他アプリに依存しないため、動作検証が容易。

---

## 🧱 データ契約

```json
// Webhook入力
{
  "script_id": "wf7-script-20251110-001",
  "voiceover_url": "https://example.com/audio.mp3",
  "sections": [
    {"section": 1, "title": "Hook", "prompt": "dramatic promo, zoom-in", "duration": 3},
    {"section": 2, "title": "Intro", "prompt": "sleek office, camera pan", "duration": 6},
    ...
    {"section": 7, "title": "CTA", "prompt": "bold text overlay", "duration": 4}
  ]
}
```

```json
// Webhook応答
{
  "success": true,
  "script_id": "wf7-script-20251110-001",
  "videos_metadata": [
    {"section": 1, "drive_file_id": "...", "video_url": "https://drive.google.com/uc?id=..."},
    ...
  ],
  "final_video": {
    "cloudinary_public_id": "wf7/script-20251110-001/final",
    "cloudinary_url": "https://res.cloudinary.com/.../video/upload/wf7/script-20251110-001/final.mp4",
    "drive_file_id": "1G8....",
    "duration": 31
  }
}
```

---

## 🗺️ n8n ノード構成（10ノード）

| # | ノード | 役割 / 設定のポイント |
|---|--------|-----------------------|
| 1 | **Webhook - Phase4 Entry** | `POST /wf7-phase4/minimal`。JSON Body で `script_id` と `sections` を受信。 |
| 2 | **Code - Validate Payload** | TypeScript で `sections.length === 7` を強制。欠損時は `throw new Error("sections must be 7")`。 |
| 3 | **Item Lists - Explode Sections** | `sections` を 1 レコードずつ展開して FAL 呼び出しをループ処理できるようにする。 |
| 4 | **HTTP Request - FAL Submit** | `POST https://queue.fal.run/fal-ai/hunyuan-video`。Body 例は後述。`fal_key` は Node のヘッダでセット。 |
| 5 | **Wait 8s + HTTP Request - Poll FAL** | `GET https://queue.fal.run/status/{request_id}`。`Split In Batches` と組み合わせて完了まで最大 5 回ポーリング。 |
| 6 | **Google Drive - Upload** | Poll 結果の `video.url` を `binary` でダウンロード後、`/WF7/phase4/raw/{script_id}/{section}.mp4` に保存。出力に `drive_file_id` を追加。 |
| 7 | **Merge - Collect Videos** | 7件の `videos_metadata` を 1配列に戻す。 |
| 8 | **HTTP Request - FAL FFmpeg Concat** | `POST https://queue.fal.run/fal-ai/ffmpeg/concat` に Google Drive の共有リンクを渡し、単一動画を生成。 |
| 9 | **Cloudinary - Upload** | FALから返った `final_video_url` (signed URL) を `video/upload` で Cloudinary にコピー。`public_id = wf7/{script_id}/final`。 |
|10 | **Respond to Webhook** | 成功/失敗どちらも JSON 形式で返却。失敗時は `success:false` と Cloudinary / Drive にアップしたファイルIDを削除するか、Cleanup ノードを追加。 |

---

## 🧪 FAL API のリクエスト例

### 4. Image-to-Video 送信

```json
{
  "prompt": "sleek office motion graphics, camera panning, depth of field, 4k",
  "duration": 6,
  "seed": 42,
  "aspect_ratio": "16:9",
  "guidance_scale": 3,
  "enable_audio": false,
  "callback_url": "",
  "metadata": {
    "script_id": "wf7-script-20251110-001",
    "section": 2
  }
}
```

ポーリング時は `GET /status/{request_id}`。`status === "completed"` のとき `result.video.url` を取得できる。

### 8. FFmpeg Concat（FALユーティリティ）

```json
{
  "videos": [
    {"url": "https://drive.google.com/uc?id=...", "duration": 3},
    {"url": "https://drive.google.com/uc?id=...", "duration": 6}
  ],
  "transitions": "crossfade",
  "audio_url": "https://example.com/audio.mp3",
  "metadata": {"script_id": "wf7-script-20251110-001"}
}
```

> Google Drive の共有リンクは `uc?id=...&export=download` 形式にする。n8n では Google Drive ノードの出力 `webContentLink` を `Replace` で変換するのが簡単。

---

## ✅ 検証テスト手順

1. **ダミーデータ送信**  
   ```
   curl -X POST https://n8n.example.com/wf7-phase4/minimal \
     -H "Content-Type: application/json" \
     -d @test-phase4c-mock-data.json
   ```
   既存の `test-phase4c-mock-data.json` を流用可。`sections` の `prompt` / `duration` を7本分に調整する。

2. **FAL レンダリング確認**  
   - n8n 実行画面でノード #4/#5 を開き、`request_id` と `result.video.url` を確認。  
   - CloudWatch 等は不要。Error 時は FAL レスポンスの `error` をログに残す。

3. **Google Drive 配置確認**  
   - `/WF7/phase4/raw/{script_id}/` に 7 本の mp4 ができているか確認。  
   - `drive_file_id` を `curl "https://www.googleapis.com/drive/v3/files/{id}?fields=webContentLink"` でチェックしても良い。

4. **Cloudinary 公開確認**  
   - `https://res.cloudinary.com/<cloud_name>/video/upload/wf7/script-xxxx/final.mp4` にアクセスし再生。  
   - Cloudinary ダッシュボードで `wf7/script-xxx/final` のビットレート/Duration を確認し、`duration == sum(sections.duration)` になっているかを検証。

5. **自動テスト（オプション）**  
   - `test-phase4c-http-based.json` の `final_video_url` を Cloudinary URL に差し替え、`test-phase4c-execution.sh` を流用して再生時間チェックを行う。  
   - 失敗時は n8n 実行IDを添えて Slack 通知を飛ばす。

---

## 🛠️ よくある失敗と対処

| 症状 | 原因 | 対処 |
|------|------|------|
| FAL ポーリングが timeout | `duration` を 8 以上にしているのに Wait が短い | Wait を 8-10秒に、リトライ上限を 8 回に伸ばす |
| Google Drive からのダウンロードに失敗 | `webContentLink` をそのまま渡している | `replace(webContentLink, 'open?id=', 'uc?id=')` または `webContentLink + '&export=download'` にする |
| Cloudinary へアップロード後に 404 | `resource_type` が `image` のまま | Cloudinary ノードで `resource_type = video` を明示 |
| 7本以外のセクション数が流れてくる | Phase3からのデータ揺れ | ノード #2 で `sections.length !== 7` の場合に即座に Webhook 応答でエラーを返す |

---

## 📌 追加メモ

- Phase4b を既存実装から切り出す際は、本ドキュメントのノード構成をテンプレートとして `Execute Workflow` で呼び出せばよい。  
- Phase4c を外部 FastAPI で実装済みの場合でも、Cloudinary へのアップロードは n8n から行うと API キーを一元管理できる。  
- コスト試算は `videos_metadata[*].render_elapsed` と `final_video.duration` から算出し、Notion 更新は後段フローで行う。ここでは扱わない。  

---

この手順でまず動くミニマム構成を作り、問題がなければ Phase4a/b/c の既存ワークフローに接続していく。
