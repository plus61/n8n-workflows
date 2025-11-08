# WF7 Phase4c 動画ダウンロード失敗エラー対処法

**作成日**: 2025-11-09  
**更新日**: 2025-11-09  
**エラー**: `RuntimeError: 動画ダウンロード失敗: hook`  
**最新エラー**: `unknown url type: https` (Pyodide環境の制限)  
**対象ワークフロー**: WF7 Phase4 - V3 Fixed (ID: `r9Sp5n0mkUCcH8cw`)

---

## 🔍 エラー詳細

### エラーメッセージ
```
RuntimeError: 動画ダウンロード失敗: hook
```

### 発生箇所
- **ノード**: `Code - Phase4c FFmpeg Concat`
- **関数**: `download_video()`
- **失敗した動画**: hookセクション（最初の動画）

### エラー発生時の状況
- `Set - Phase4b Payload`ノードは正常に実行完了
- `IF - Phase4b Success Check`ノードはTrue分岐で正常に実行
- `Code - Phase4c FFmpeg Concat`ノードで動画ダウンロード時にエラー

---

## 🐛 原因分析

### 1. 動画URLが無効
**症状**: 動画URLにアクセスできない（404エラーなど）

**確認方法**:
```bash
# 動画URLに直接アクセスできるか確認
curl -I https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4
```

**期待される結果**:
- HTTP 200 OK
- Content-Type: video/mp4

**実際の結果**:
- HTTP 404 Not Found → URLが無効
- HTTP 403 Forbidden → アクセス権限なし
- タイムアウト → ネットワークエラー

### 2. n8n Code NodeのPyodide環境の制限
**症状**: `unknown url type: https` エラーが発生

**原因**: n8nのCode NodeはPyodide（ブラウザベースのPython）を使用しており、HTTPS接続が制限されている可能性があります。

**確認方法**:
- エラーメッセージに `unknown url type: https` が含まれている
- `urllib.request.urlopen()` がHTTPS URLをサポートしていない

**解決方法**:
- `http.client`と`ssl`を使用（現在の実装）
- または、HTTP Requestノードを使用して動画をダウンロード

### 3. curlコマンドが利用できない
**症状**: n8nサーバーでcurlコマンドがインストールされていない

**確認方法**:
```bash
# Railwayコンソールで実行
which curl
curl --version
```

### 3. タイムアウト（60秒）
**症状**: 動画ダウンロードに60秒以上かかっている

**現在の設定**:
```python
timeout=60  # 60秒でタイムアウト
```

**問題**: 大きな動画ファイルの場合、60秒では不十分な可能性

### 4. ネットワークエラー
**症状**: 一時的なネットワーク障害

**確認方法**:
- 複数回実行して再現性を確認
- 他の動画URLでも同じエラーが発生するか確認

---

## ✅ 解決方法

### 方法1: 動画URLの有効性を確認

1. **ブラウザで直接アクセス**
   - 動画URLをブラウザで開く
   - 動画が再生できるか確認

2. **curlで確認**
   ```bash
   curl -I https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4
   ```

3. **有効な動画URLに置き換え**
   - Phase4bで生成された実際の動画URLを使用
   - テスト用の有効な動画URLを使用

### 方法2: エラーメッセージを詳細化

`Code - Phase4c FFmpeg Concat`ノードのPythonコードを修正して、より詳細なエラーメッセージを出力：

```python
def download_video(video_url, output_path):
    try:
        if "drive.google.com" in video_url:
            if "/file/d/" in video_url:
                file_id = video_url.split("/file/d/")[1].split("/")[0]
                video_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        print(f"⏳ 動画ダウンロード開始: {video_url}")
        result = subprocess.run(
            ["curl", "-L", "-o", output_path, video_url],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"curl returncode: {result.returncode}")
        print(f"curl stdout: {result.stdout}")
        print(f"curl stderr: {result.stderr}")
        
        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ ダウンロード成功: {output_path} ({file_size} bytes)")
            if file_size > 0:
                return True
            else:
                print(f"❌ ファイルサイズが0: {output_path}")
                return False
        else:
            print(f"❌ curl失敗: returncode={result.returncode}")
            if result.stderr:
                print(f"   エラー: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ ダウンロードタイムアウト（60秒経過）: {video_url}")
        return False
    except Exception as e:
        print(f"❌ ダウンロードエラー: {e}")
        return False
```

### 方法3: タイムアウト時間を延長

動画ファイルが大きい場合、タイムアウト時間を延長：

```python
result = subprocess.run(
    ["curl", "-L", "-o", output_path, video_url],
    capture_output=True,
    text=True,
    timeout=120  # 60秒 → 120秒に延長
)
```

### 方法4: リトライロジックを追加

一時的なネットワークエラーに対応するため、リトライロジックを追加：

```python
def download_video_with_retry(video_url, output_path, max_retries=3):
    for attempt in range(max_retries):
        if download_video(video_url, output_path):
            return True
        if attempt < max_retries - 1:
            print(f"⏳ リトライ {attempt + 1}/{max_retries - 1}...")
            time.sleep(2)  # 2秒待機
    return False
```

### 方法5: Pythonのrequestsライブラリを使用（推奨）

curlコマンドの代わりに、Pythonのrequestsライブラリを使用：

```python
import requests

def download_video(video_url, output_path):
    try:
        print(f"⏳ 動画ダウンロード開始: {video_url}")
        
        # Google Drive URLの変換
        if "drive.google.com" in video_url:
            if "/file/d/" in video_url:
                file_id = video_url.split("/file/d/")[1].split("/")[0]
                video_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(output_path)
        if file_size > 0:
            print(f"✅ ダウンロード成功: {output_path} ({file_size} bytes)")
            return True
        else:
            print(f"❌ ファイルサイズが0: {output_path}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ ダウンロードタイムアウト: {video_url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ダウンロードエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
```

**注意**: n8nのCode Nodeで`requests`ライブラリが利用可能か確認が必要です。

---

## 🛠️ 実装手順

### Step 1: 現在のエラーを確認

1. n8n UIで `Code - Phase4c FFmpeg Concat` ノードを開く
2. **"OUTPUT"** タブでエラーメッセージを確認
3. エラーメッセージの内容を記録

### Step 2: 動画URLを確認

1. `Set - Phase4b Payload`ノードの出力を確認
2. `videos_metadata[0].video_url`の値を確認
3. ブラウザで動画URLに直接アクセス

### Step 3: エラーハンドリングを改善

1. `Code - Phase4c FFmpeg Concat`ノードのPythonコードを修正
2. より詳細なエラーメッセージを追加
3. リトライロジックを追加（オプション）

### Step 4: 再テスト

1. 修正後のノードを実行
2. エラーメッセージが改善されたか確認
3. 動画ダウンロードが成功するか確認

---

## 📝 確認チェックリスト

- [ ] 動画URLが有効か確認（ブラウザで直接アクセスできるか）
- [ ] curlコマンドがn8nサーバーで利用可能か確認
- [ ] エラーメッセージが詳細化されているか確認
- [ ] タイムアウト時間が適切か確認（60秒で不十分な場合）
- [ ] リトライロジックが実装されているか確認（オプション）

---

## 🔗 関連ドキュメント

- `docs/testing/WF7-Phase4c-タイムアウト問題解決.md`: タイムアウト問題の対処法
- `docs/testing/WF7-Phase4c-テスト実行トラブルシューティング.md`: 一般的なトラブルシューティング
- `docs/implementation/WF7-Phase4c-ClaudeCode実装指示書.md`: Phase4c実装指示書

---

## 💡 次のステップ

1. **動画URLの確認**: Phase4bで生成された実際の動画URLを使用
2. **エラーメッセージの詳細化**: より詳細なエラーメッセージを出力するように修正
3. **タイムアウトの調整**: 必要に応じてタイムアウト時間を延長
4. **リトライロジックの追加**: 一時的なネットワークエラーに対応

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-09

