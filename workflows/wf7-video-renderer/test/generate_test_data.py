#!/usr/bin/env python3
"""
テストデータ生成スクリプト
サンプルJSONとダミー画像を生成
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_test_json():
    """テスト用JSONファイルを生成"""

    # script.json
    script_data = {
        "segments": [
            {
                "duration": 10,
                "telop": "FFmpeg直接実行テスト！"
            },
            {
                "duration": 8,
                "telop": "高速レンダリングを実現"
            },
            {
                "duration": 12,
                "telop": "12倍の速度改善を目指す"
            },
            {
                "duration": 10,
                "telop": "Phase1ハイブリッド方式"
            }
        ]
    }

    # assets.json
    assets_data = {
        "assets": [
            {
                "assetIndex": 0,
                "fileUrl": "/tmp/test_asset_0.jpg"
            },
            {
                "assetIndex": 1,
                "fileUrl": "/tmp/test_asset_1.jpg"
            },
            {
                "assetIndex": 2,
                "fileUrl": "/tmp/test_asset_2.jpg"
            },
            {
                "assetIndex": 3,
                "fileUrl": "/tmp/test_asset_3.jpg"
            }
        ]
    }

    # ファイル出力
    test_dir = Path(__file__).parent

    with open(test_dir / 'script.json', 'w', encoding='utf-8') as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Generated: {test_dir / 'script.json'}")

    with open(test_dir / 'assets.json', 'w', encoding='utf-8') as f:
        json.dump(assets_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Generated: {test_dir / 'assets.json'}")


def generate_dummy_images():
    """ダミー画像を生成（グラデーション背景+番号テキスト）"""

    colors = [
        (255, 99, 71),    # Tomato
        (60, 179, 113),   # MediumSeaGreen
        (30, 144, 255),   # DodgerBlue
        (238, 130, 238),  # Violet
    ]

    for i, color in enumerate(colors):
        # 1080x1920の画像生成
        img = Image.new('RGB', (1080, 1920), color=color)
        draw = ImageDraw.Draw(img)

        # 中央に大きな番号を描画
        try:
            font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 300)
        except:
            try:
                font = ImageFont.truetype("Arial", 300)
            except:
                font = ImageFont.load_default()

        text = f"#{i+1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (1080 - text_width) // 2
        y = (1920 - text_height) // 2

        draw.text((x, y), text, fill='white', font=font)

        # /tmpに保存
        output_path = f"/tmp/test_asset_{i}.jpg"
        img.save(output_path, 'JPEG', quality=95)
        print(f"✓ Generated: {output_path}")


if __name__ == '__main__':
    print("🎨 Generating test data...")
    generate_test_json()
    generate_dummy_images()
    print("\n✅ Test data generation complete!")
