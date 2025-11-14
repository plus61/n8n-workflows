# WF7 Phase4a 接続修正手順

**作成日**: 2025-11-08  
**問題**: Code - Generate Slides with PillowからCode - Convert to Binaryへの接続にSplit Outノードが欠けている  
**影響**: 7つのアイテムが1つの配列として処理され、1枚の画像しか生成されない

---

## 🔍 問題の詳細

現在の接続:
```
Code - Generate Slides with Pillow → Code - Convert to Binary
```

正しい接続:
```
Code - Generate Slides with Pillow → Split Out - Individual Slides → Code - Convert to Binary
```

---

## 🔧 修正手順

### Step 1: Split Outノードを追加

1. n8n UIでワークフロー `qSN7EHj5yl0nPXij` を開く
2. `Code - Generate Slides with Pillow`ノードを選択
3. 右側に新しいノードを追加
4. ノードタイプ: **Split Out** を選択
5. ノード名: `Split Out - Individual Slides`

#### Split Outノードの設定

- **Field to Split Out**: `={{ $json }}`
- **Include**: `noOtherFields`

### Step 2: 接続の修正

1. `Code - Generate Slides with Pillow` → `Code - Convert to Binary` の接続を削除
2. `Code - Generate Slides with Pillow` → `Split Out - Individual Slides` を接続
3. `Split Out - Individual Slides` → `Code - Convert to Binary` を接続

---

## ✅ 確認事項

修正後、以下の接続が正しく設定されていることを確認：

- ✅ `Code - Generate Slides with Pillow` → `Split Out - Individual Slides`
- ✅ `Split Out - Individual Slides` → `Code - Convert to Binary`
- ✅ `Code - Convert to Binary` → `Google Drive - Upload Slide Image`
- ✅ `Google Drive - Upload Slide Image` → `Aggregate - Combine All Slides`
- ✅ `Aggregate - Combine All Slides` → `Set - Phase4a Payload New`

---

## 🧪 再テスト

修正後、再度テストを実行してください：

```bash
./test-phase4a-7slides.sh 2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9
```

期待される結果：
- Split Outノードが7つのアイテムに分割
- Code - Convert to Binaryが7回実行される
- Google Drive - Upload Slide Imageが7回実行される
- Aggregateノードが7枚の結果を統合




