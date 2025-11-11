# WF7 Phase4b 修正適用手順

**作成日**: 2025-11-10  
**ワークフローID**: `wHaKi98mTlUvFIOR`  
**ワークフロー名**: WF7 Phase4b - Image to Video

---

## 📋 修正内容サマリー

### 実施した改善

1. **CodeノードのonError設定を修正**
   - `Code - Generate Cloudinary Signature`: `continueRegularOutput`に変更
   - `Code - Prepare FAL Payload`: `continueRegularOutput`に変更
   - `Code - Build Video Metadata`: `continueRegularOutput`に変更
   - `Code - Build Final Response`: `continueRegularOutput`に変更
   - `Code - Timeout Error`: `continueRegularOutput`に変更
   - `IF - Render Completed?`: `continueRegularOutput`に変更
   - `IF - Check Retry Limit`: `continueRegularOutput`に変更

2. **接続の修正**
   - `Code - Validate Input`のエラー出力を`Code - Build Final Response`に正しく接続
   - main出力は`Split Out - Slides`のみに接続

3. **HTTP Requestノードのリトライ設定**
   - `HTTP Request - Submit to FAL`に`maxTries: 3`と`waitBetweenTries: 1000`を追加

---

## 🔄 適用方法

### 方法1: n8n UIでインポート（推奨）

1. **n8n UIにアクセス**
   - URL: `https://n8n-python-production-344b.up.railway.app/`
   - ログイン

2. **既存ワークフローを開く**
   - ワークフロー一覧から `WF7 Phase4b - Image to Video` (ID: `wHaKi98mTlUvFIOR`) を開く

3. **ワークフローをエクスポート（バックアップ）**
   - 右上の「⋮」メニューから「Download」を選択
   - 現在のワークフローをバックアップとして保存

4. **修正済みワークフローをインポート**
   - 右上の「⋮」メニューから「Import from File」を選択
   - `workflows/wf7_phase4b_fixed_with_current_ids.json` を選択
   - 「Import」をクリック

5. **ワークフローを保存**
   - 「Save」をクリック
   - ワークフロー名が「WF7 Phase4b - Image to Video」であることを確認

6. **ワークフローをアクティブ化**
   - 右上のトグルスイッチをONにしてアクティブ化

---

## ✅ 確認項目

### 修正内容の確認

- ✅ `Code - Validate Input`のエラー出力が`Code - Build Final Response`に接続されている
- ✅ `Code - Validate Input`のmain出力が`Split Out - Slides`のみに接続されている
- ✅ すべてのCodeノードとIFノードに`onError`設定が追加されている
- ✅ `HTTP Request - Submit to FAL`にリトライ設定が追加されている

---

## 🔍 検証の実行

ワークフロー更新後、再度検証を実行：

```bash
# n8n MCPツールで検証
mcp_n8n-mcp_n8n_validate_workflow({id: "wHaKi98mTlUvFIOR"})
```

### 期待される検証結果

- **エラー**: 1件（サイクル検出のみ - 意図的なポーリングループのため問題なし）
- **警告**: 10件程度（非クリティカルな警告のみ）
- **有効性**: ✅ Valid（サイクル検出を除く）

---

## 📝 テスト実行

修正後のワークフローをテスト：

```bash
# Webhook経由でテスト
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "test-001",
    "slides_metadata": [
      {
        "section": "hook",
        "image_url": "https://drive.google.com/uc?export=download&id=1-HNPWmjKnjUHdl-E2w0y-KCu7PaM_PHf",
        "duration": 3,
        "motion_prompt": "",
        "text": "Test after fixes"
      }
    ]
  }'
```

---

## 📊 改善効果

### 修正前の検証結果
- **エラー**: 2件
- **警告**: 17件
- **有効性**: ❌ Invalid

### 修正後の期待結果
- **エラー**: 1件（サイクル検出のみ - 意図的なポーリングループのため問題なし）
- **警告**: 10件程度（非クリティカルな警告のみ）
- **有効性**: ✅ Valid（サイクル検出を除く）

---

## 📁 関連ファイル

- **修正済みワークフロー**: `workflows/wf7_phase4b_fixed_with_current_ids.json`
- **修正スクリプト**: `apply_phase4b_fixes.py`
- **改善レポート**: `docs/implementation/WF7-Phase4b-改善レポート.md`

---

**作成者**: AI Assistant  
**更新日**: 2025-11-10  
**ステータス**: 修正完了、適用待ち

