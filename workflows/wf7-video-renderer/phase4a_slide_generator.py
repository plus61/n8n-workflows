"""
Phase 4a: Pillow スライド画像生成スクリプト

目的: Notion DBのデータから7枚のスライド画像を生成
出力: 7つのbase64エンコード画像 + メタデータ

使用方法（n8n Code Node内）:
  from phase4a_slide_generator import generate_slides
  slides = generate_slides(items[0]['json'])
  return slides
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import base64
import io
import json


# フォント設定（Railway環境）
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/noto/NotoSansJP-Bold.ttf"

# デフォルトブランドカラー
DEFAULT_BRAND_COLORS = {
    'background': '#1a1a2e',
    'primary_text': '#ffffff',
    'secondary_text': '#aaaaaa',
    'accent': '#00d4ff',
    'cta_bg': '#ff6b6b',
    'cta_text': '#ffffff'
}

# セクションラベル
SECTION_LABELS = {
    "hook": "フック",
    "intro": "導入",
    "point1": "ポイント①",
    "point2": "ポイント②",
    "point3": "ポイント③",
    "summary": "まとめ",
    "cta": "今すぐ行動"
}


def hex_to_rgb(hex_color):
    """HEXカラーコードをRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_slide(text, section_type, duration, brand_colors, icon=None):
    """
    スライド画像を生成

    Args:
        text (str): 表示するテキスト
        section_type (str): セクションタイプ（hook, intro, point1-3, summary, cta）
        duration (int): 動画の秒数
        brand_colors (dict): ブランドカラー設定
        icon (str, optional): 表示するアイコン（絵文字）

    Returns:
        PIL.Image: 生成された画像
    """
    # 1080x1920 縦型画像
    bg_color = hex_to_rgb(brand_colors.get('background', '#1a1a2e'))
    img = Image.new('RGB', (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # フォント読み込み
    try:
        if section_type in ["hook", "cta"]:
            font_main = ImageFont.truetype(FONT_BOLD_PATH, 90)
        else:
            font_main = ImageFont.truetype(FONT_PATH, 70)

        font_label = ImageFont.truetype(FONT_PATH, 40)
        font_icon = ImageFont.truetype(FONT_PATH, 120)
    except Exception as e:
        print(f"フォント読み込みエラー: {e}")
        # フォールバック: デフォルトフォント
        font_main = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_icon = ImageFont.load_default()

    # アイコン描画（オプション）
    if icon:
        accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
        draw.text((540, 400), icon, fill=accent_color,
                  font=font_icon, anchor="mm")

    # テキスト折り返し
    if section_type == "hook":
        wrapped = textwrap.fill(text, width=15)
        y_offset = 700
    elif section_type == "cta":
        # CTAは短いので折り返し不要
        wrapped = text
        y_offset = 900
    else:
        wrapped = textwrap.fill(text, width=18)
        y_offset = 600

    # テキスト描画（中央配置）
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1080 - text_width) // 2
    y = y_offset

    # 影付きテキスト（可読性向上）
    draw.multiline_text((x+3, y+3), wrapped, fill="#000000",
                        font=font_main, align="center")

    # メインテキスト
    primary_text_color = hex_to_rgb(brand_colors.get('primary_text', '#ffffff'))
    draw.multiline_text((x, y), wrapped, fill=primary_text_color,
                        font=font_main, align="center")

    # 秒数ラベル（下部）
    label_text = f"{duration}秒"
    secondary_text_color = hex_to_rgb(brand_colors.get('secondary_text', '#aaaaaa'))
    draw.text((50, 1850), label_text, fill=secondary_text_color,
              font=font_label)

    # セクションラベル（上部）
    section_label = SECTION_LABELS.get(section_type, "")
    accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
    draw.text((50, 100), section_label, fill=accent_color,
              font=font_label)

    return img


def image_to_base64(img):
    """PIL画像をbase64文字列に変換"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def generate_slides(script_data):
    """
    7枚のスライド画像を生成

    Args:
        script_data (dict): Notion DBから取得したスクリプトデータ

    Returns:
        list: 7つのスライドデータ（base64画像 + メタデータ）
    """
    # 入力データ取得
    hook_text = script_data.get('hook_text_5options', ['フックテキストがありません'])[0]
    intro_text = script_data.get('introduction_text', '導入テキストがありません')
    point1 = script_data.get('main_point_1', 'ポイント1がありません')
    point2 = script_data.get('main_point_2', 'ポイント2がありません')
    point3 = script_data.get('main_point_3', 'ポイント3がありません')
    summary = script_data.get('summary_text', 'まとめがありません')
    cta = script_data.get('cta_text_3options', ['CTAがありません'])[0]

    # ブランドカラー取得（JSON文字列の場合はパース）
    brand_colors_raw = script_data.get('Brand Colors', DEFAULT_BRAND_COLORS)
    if isinstance(brand_colors_raw, str):
        try:
            brand_colors = json.loads(brand_colors_raw)
        except:
            brand_colors = DEFAULT_BRAND_COLORS
    else:
        brand_colors = brand_colors_raw if brand_colors_raw else DEFAULT_BRAND_COLORS

    # 視覚要素取得
    visual_elements_raw = script_data.get('Visual Elements', {})
    if isinstance(visual_elements_raw, str):
        try:
            visual_elements = json.loads(visual_elements_raw)
        except:
            visual_elements = {}
    else:
        visual_elements = visual_elements_raw if visual_elements_raw else {}

    # 秒数設定取得
    duration_config_raw = script_data.get('Duration Config', {})
    if isinstance(duration_config_raw, str):
        try:
            duration_config = json.loads(duration_config_raw)
        except:
            duration_config = {
                "hook": 3, "intro": 10, "point1": 13,
                "point2": 13, "point3": 14, "summary": 20, "cta": 7
            }
    else:
        duration_config = duration_config_raw if duration_config_raw else {
            "hook": 3, "intro": 10, "point1": 13,
            "point2": 13, "point3": 14, "summary": 20, "cta": 7
        }

    # Motion Prompts取得
    motion_prompts_raw = script_data.get('Motion Prompts', {})
    if isinstance(motion_prompts_raw, str):
        try:
            motion_prompts = json.loads(motion_prompts_raw)
        except:
            motion_prompts = {
                "hook": "dramatic zoom in effect, professional business style, sharp focus",
                "intro": "smooth slide transition, calm professional tone, steady camera",
                "point1": "gentle fade in with subtle zoom, educational style, clean motion",
                "point2": "gentle fade in with subtle zoom, educational style, clean motion",
                "point3": "gentle fade in with subtle zoom, educational style, clean motion",
                "summary": "cinematic pan effect, inspiring tone, smooth movement",
                "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
            }
    else:
        motion_prompts = motion_prompts_raw if motion_prompts_raw else {
            "hook": "dramatic zoom in effect, professional business style, sharp focus",
            "intro": "smooth slide transition, calm professional tone, steady camera",
            "point1": "gentle fade in with subtle zoom, educational style, clean motion",
            "point2": "gentle fade in with subtle zoom, educational style, clean motion",
            "point3": "gentle fade in with subtle zoom, educational style, clean motion",
            "summary": "cinematic pan effect, inspiring tone, smooth movement",
            "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
        }

    # 7枚のスライドを生成
    slides = []

    # 1. フック
    icon_hook = visual_elements.get('hook', {}).get('icon', '⚠️')
    slide_hook = create_slide(
        hook_text, "hook",
        duration_config.get('hook', 3),
        brand_colors,
        icon=icon_hook
    )
    slides.append({
        "section": "hook",
        "duration": duration_config.get('hook', 3),
        "image_base64": image_to_base64(slide_hook),
        "filename": "slide_1_hook.png",
        "motion_prompt": motion_prompts.get('hook', ''),
        "text": hook_text
    })

    # 2. 導入
    slide_intro = create_slide(
        intro_text, "intro",
        duration_config.get('intro', 10),
        brand_colors
    )
    slides.append({
        "section": "intro",
        "duration": duration_config.get('intro', 10),
        "image_base64": image_to_base64(slide_intro),
        "filename": "slide_2_intro.png",
        "motion_prompt": motion_prompts.get('intro', ''),
        "text": intro_text
    })

    # 3-5. 本編3ポイント
    points = [
        (point1, duration_config.get('point1', 13), "point1"),
        (point2, duration_config.get('point2', 13), "point2"),
        (point3, duration_config.get('point3', 14), "point3")
    ]

    for i, (point, duration, section_key) in enumerate(points, start=1):
        icon = visual_elements.get(section_key, {}).get('icon')
        slide = create_slide(point, section_key, duration, brand_colors, icon=icon)
        slides.append({
            "section": section_key,
            "duration": duration,
            "image_base64": image_to_base64(slide),
            "filename": f"slide_{i+2}_point{i}.png",
            "motion_prompt": motion_prompts.get(section_key, ''),
            "text": point
        })

    # 6. まとめ
    slide_summary = create_slide(
        summary, "summary",
        duration_config.get('summary', 20),
        brand_colors
    )
    slides.append({
        "section": "summary",
        "duration": duration_config.get('summary', 20),
        "image_base64": image_to_base64(slide_summary),
        "filename": "slide_6_summary.png",
        "motion_prompt": motion_prompts.get('summary', ''),
        "text": summary
    })

    # 7. CTA
    slide_cta = create_slide(
        cta, "cta",
        duration_config.get('cta', 7),
        brand_colors
    )
    slides.append({
        "section": "cta",
        "duration": duration_config.get('cta', 7),
        "image_base64": image_to_base64(slide_cta),
        "filename": "slide_7_cta.png",
        "motion_prompt": motion_prompts.get('cta', ''),
        "text": cta
    })

    return slides


# n8n Code Node用エントリーポイント
def main(items):
    """
    n8n Code Nodeから呼び出される関数

    Args:
        items (list): n8nから渡されるアイテム配列

    Returns:
        list: 7つのスライドデータ
    """
    if not items or len(items) == 0:
        raise ValueError("入力データがありません")

    script_data = items[0]['json']
    slides = generate_slides(script_data)

    return slides


# テスト用（ローカル実行時）
if __name__ == "__main__":
    # サンプルデータ
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

    # テスト実行
    print("スライド生成テスト開始...")
    slides = generate_slides(sample_data)
    print(f"✅ {len(slides)}枚のスライドを生成しました")

    for i, slide in enumerate(slides, 1):
        print(f"  {i}. {slide['section']}: {slide['duration']}秒 - {slide['filename']}")
        print(f"     テキスト: {slide['text'][:30]}...")
        print(f"     Motion: {slide['motion_prompt'][:50]}...")
