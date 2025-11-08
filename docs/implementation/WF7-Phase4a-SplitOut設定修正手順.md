# WF7 Phase4a Split Outノード設定修正手順

**作成日**: 2025-11-08  
**問題**: Split Outノード（Individual Slides）の出力が0になっている  
**原因**: Split Outノードの設定が不適切

---

## 🔍 問題の詳細

実行結果:
- **Code - Generate Slides with Pillow**: ✅ 7つのアイテムを出力
- **Individual Slides (Split Out)**: ❌ 出力が0（設定の問題）

---

## 🔧 修正手順

### Split Outノードの設定を確認・修正

1. n8n UIでワークフロー `qSN7EHj5yl0nPXij` を開く
2. `Individual Slides` (Split Out) ノードを選択
3. 設定を確認・修正:

#### 設定方法1: デフォルト設定（推奨）

**Field to Split Out**: **空欄のまま**（何も設定しない）

**説明**: Code Nodeが配列を返す場合、Split Outノードは自動的に配列の各要素を分割します。`fieldToSplitOut`を設定する必要はありません。

#### 設定方法2: 明示的に設定する場合

**Field to Split Out**: `={{ $json }}`

**Include**: `noOtherFields` は**使用しない**

**注意**: `include: noOtherFields`を設定すると、出力が0になる可能性があります。

---

## ✅ 正しい設定

Split Outノードの設定:

```json
{
  "fieldToSplitOut": "",
  "options": {}
}
```

または、`fieldToSplitOut`を完全に削除（空欄のまま）。

---

## 🧪 再テスト

修正後、再度テストを実行してください：

```bash
./test-phase4a-7slides.sh 2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9
```

期待される結果：
- Individual Slidesノードが7つのアイテムを出力
- Code - Convert to Binaryが7回実行される
- Google Drive - Upload Slide Imageが7回実行される
- Aggregateノードが7枚の結果を統合

---

## 📝 補足説明

### n8n Code Nodeの配列出力について

n8nのCode Nodeが配列を返す場合：
- **Mode: `runOnceForAllItems`**: 配列全体を1つのアイテムとして返す
- Split Outノードが必要: 配列の各要素を個別のアイテムに分割

### Split Outノードの動作

- **入力**: 配列を含む1つのアイテム `[{...}, {...}, ...]`
- **出力**: 配列の各要素が個別のアイテム `{...}`, `{...}`, ...

`fieldToSplitOut`を設定しない場合、n8nは自動的に配列を検出して分割します。

