"""
Phase 4a: ローカルテスト用スクリプト
画像ファイルを実際に保存してテストします
"""

import sys
import json
import base64
from pathlib import Path

# phase4a_slide_generator.pyをインポート
from phase4a_slide_generator import generate_slides, DEFAULT_BRAND_COLORS

# テストデータ
sample_data = {
    "hook_text_5options": ["あなたのビジネス、本当に見つけられていますか？"],
    "introduction_text": "多くの地域ビジネスが、Googleマップで見つけられずに機会を失っています",
    "main_point_1": "MEO対策で検索順位を大幅に改善できます",
    "main_point_2": "実際の成功事例では3ヶ月で問い合わせが3倍に",
    "main_point_3": "今すぐ始めれば、競合に差をつけられます",
    "summary_text": "MEO対策は地域ビジネス成長の鍵です",
    "cta_text_3options": ["無料診断を今すぐ申し込む"],
    "Brand Colors": json.dumps(DEFAULT_BRAND_COLORS),
    "Visual Elements": json.dumps({
        "hook": {"icon": "⚠️"},
        "point1": {"icon": "📊"},
        "point2": {"icon": "🎯"},
        "point3": {"icon": "✅"}
    }),
    "Duration Config": json.dumps({
        "hook": 3, "intro": 10, "point1": 13,
        "point2": 13, "point3": 14, "summary": 20, "cta": 7
    }),
    "Motion Prompts": json.dumps({
        "hook": "dramatic zoom in effect, professional business style, sharp focus",
        "intro": "smooth slide transition, calm professional tone, steady camera",
        "point1": "gentle fade in with subtle zoom, educational style, clean motion",
        "point2": "gentle fade in with subtle zoom, educational style, clean motion",
        "point3": "gentle fade in with subtle zoom, educational style, clean motion",
        "summary": "cinematic pan effect, inspiring tone, smooth movement",
        "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
    })
}

print("=" * 80)
print("Phase 4a: スライド画像生成テスト")
print("=" * 80)

# 出力ディレクトリ作成
output_dir = Path("test_output")
output_dir.mkdir(exist_ok=True)

print(f"\n📁 出力ディレクトリ: {output_dir.absolute()}")

# スライド生成
print("\n⏳ スライド生成開始...")
slides = generate_slides(sample_data)

print(f"\n✅ {len(slides)}枚のスライドを生成しました\n")

# 各スライドを保存
total_size = 0
for i, slide in enumerate(slides, 1):
    # base64デコードして画像保存
    image_data = base64.b64decode(slide['image_base64'])
    output_path = output_dir / slide['filename']

    with open(output_path, 'wb') as f:
        f.write(image_data)

    file_size = len(image_data)
    total_size += file_size

    print(f"  [{i}/7] {slide['filename']}")
    print(f"       セクション: {slide['section']}")
    print(f"       秒数: {slide['duration']}秒")
    print(f"       サイズ: {file_size / 1024:.1f} KB")
    print(f"       テキスト: {slide['text'][:40]}...")
    print(f"       Motion: {slide['motion_prompt'][:50]}...")
    print()

print("=" * 80)
print(f"✅ テスト完了")
print(f"   生成枚数: {len(slides)}枚")
print(f"   合計サイズ: {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.2f} MB)")
print(f"   出力先: {output_dir.absolute()}")
print("=" * 80)

# メタデータをJSON保存
metadata = {
    "slides_count": len(slides),
    "total_size_bytes": total_size,
    "slides": [
        {
            "section": s['section'],
            "duration": s['duration'],
            "filename": s['filename'],
            "motion_prompt": s['motion_prompt'],
            "text": s['text'],
            "size_bytes": len(base64.b64decode(s['image_base64']))
        }
        for s in slides
    ]
}

metadata_path = output_dir / "metadata.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"\n📄 メタデータ: {metadata_path}")
