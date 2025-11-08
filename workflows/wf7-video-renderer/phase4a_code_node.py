"""
Phase4a Code Node用エントリーポイント

n8n Code Nodeで直接使用するためのコード
phase4a_slide_generator.pyの全機能を含む
"""

# phase4a_slide_generator.pyの全コードをここにコピー
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
    """スライド画像を生成"""
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
        font_main = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_icon = ImageFont.load_default()

    # アイコン描画（オプション）
    if icon:
        accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
        draw.text((540, 400), icon, fill=accent_color, font=font_icon, anchor="mm")

    # テキスト折り返し
    if section_type == "hook":
        wrapped = textwrap.fill(text, width=15)
        y_offset = 700
    elif section_type == "cta":
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
    draw.multiline_text((x+3, y+3), wrapped, fill="#000000", font=font_main, align="center")

    # メインテキスト
    primary_text_color = hex_to_rgb(brand_colors.get('primary_text', '#ffffff'))
    draw.multiline_text((x, y), wrapped, fill=primary_text_color, font=font_main, align="center")

    # 秒数ラベル（下部）
    label_text = f"{duration}秒"
    secondary_text_color = hex_to_rgb(brand_colors.get('secondary_text', '#aaaaaa'))
    draw.text((50, 1850), label_text, fill=secondary_text_color, font=font_label)

    # セクションラベル（上部）
    section_label = SECTION_LABELS.get(section_type, "")
    accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
    draw.text((50, 100), section_label, fill=accent_color, font=font_label)

    return img


def image_to_base64(img):
    """PIL画像をbase64文字列に変換"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def generate_slides(script_data):
    """7枚のスライド画像を生成"""
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
            duration_config = {"hook": 3, "intro": 10, "point1": 13, "point2": 13, "point3": 14, "summary": 20, "cta": 7}
    else:
        duration_config = duration_config_raw if duration_config_raw else {"hook": 3, "intro": 10, "point1": 13, "point2": 13, "point3": 14, "summary": 20, "cta": 7}

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
    slide_hook = create_slide(hook_text, "hook", duration_config.get('hook', 3), brand_colors, icon=icon_hook)
    slides.append({
        "section": "hook",
        "duration": duration_config.get('hook', 3),
        "image_base64": image_to_base64(slide_hook),
        "filename": "slide_1_hook.png",
        "motion_prompt": motion_prompts.get('hook', ''),
        "text": hook_text
    })

    # 2. 導入
    slide_intro = create_slide(intro_text, "intro", duration_config.get('intro', 10), brand_colors)
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
    slide_summary = create_slide(summary, "summary", duration_config.get('summary', 20), brand_colors)
    slides.append({
        "section": "summary",
        "duration": duration_config.get('summary', 20),
        "image_base64": image_to_base64(slide_summary),
        "filename": "slide_6_summary.png",
        "motion_prompt": motion_prompts.get('summary', ''),
        "text": summary
    })

    # 7. CTA
    slide_cta = create_slide(cta, "cta", duration_config.get('cta', 7), brand_colors)
    slides.append({
        "section": "cta",
        "duration": duration_config.get('cta', 7),
        "image_base64": image_to_base64(slide_cta),
        "filename": "slide_7_cta.png",
        "motion_prompt": motion_prompts.get('cta', ''),
        "text": cta
    })

    return slides


# ============================================
# n8n Code Node用エントリーポイント
# ============================================
# このコードはn8n Code Nodeに直接コピーして使用します
# Code Nodeの設定:
#   - Language: Python
#   - Mode: runOnceForAllItems

# データ統合ノードからの出力を処理
# items[0]['json']には、Notionページのデータが含まれています

try:
    # Notionページのpropertiesを取得
    notionPageData = items[0]['json']
    
    # データ構造に応じて調整
    # パターン1: データ統合ノードがNotionページのpropertiesを含む場合
    if 'properties' in notionPageData:
        notionProps = notionPageData['properties']
    # パターン2: データ統合ノードがscriptDataを含む場合
    elif 'scriptData' in notionPageData:
        notionProps = notionPageData['scriptData']
    # パターン3: 直接propertiesが渡される場合
    else:
        notionProps = notionPageData
    
    # スライド生成
    slides = generate_slides(notionProps)
    
    # 7つのスライドを個別アイテムとして返す
    # n8n Code Nodeでは、配列を返すと自動的にSplit Outされます
    return slides
    
except Exception as e:
    # エラーハンドリング
    error_msg = f"Phase4aスライド生成エラー: {str(e)}"
    print(error_msg)
    # エラー時は空配列を返す（後続ノードでエラーハンドリング可能）
    return []

