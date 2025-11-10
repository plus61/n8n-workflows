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
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_slide(text, section_type, duration, brand_colors, icon=None):
    bg_color = hex_to_rgb(brand_colors.get('background', '#1a1a2e'))
    img = Image.new('RGB', (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)
    
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
    
    if icon:
        accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
        draw.text((540, 400), icon, fill=accent_color, font=font_icon, anchor="mm")
    
    if section_type == "hook":
        wrapped = textwrap.fill(text, width=15)
        y_offset = 700
    elif section_type == "cta":
        wrapped = text
        y_offset = 900
    else:
        wrapped = textwrap.fill(text, width=18)
        y_offset = 600
    
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1080 - text_width) // 2
    y = y_offset
    
    draw.multiline_text((x+3, y+3), wrapped, fill="#000000", font=font_main, align="center")
    primary_text_color = hex_to_rgb(brand_colors.get('primary_text', '#ffffff'))
    draw.multiline_text((x, y), wrapped, fill=primary_text_color, font=font_main, align="center")
    
    label_text = f"{duration}秒"
    secondary_text_color = hex_to_rgb(brand_colors.get('secondary_text', '#aaaaaa'))
    draw.text((50, 1850), label_text, fill=secondary_text_color, font=font_label)
    
    section_label = SECTION_LABELS.get(section_type, "")
    accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
    draw.text((50, 100), section_label, fill=accent_color, font=font_label)
    
    return img

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()

def generate_slides(script_data):
    # Notionプロパティ取得
    properties = script_data.get('properties', {})
    
    # Script JSONからsegments配列を取得
    script_json_raw = properties.get('Script JSON', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
    try:
        script_json = json.loads(script_json_raw) if script_json_raw else {}
        segments = script_json.get('segments', [])
    except Exception as e:
        print(f"Script JSON解析エラー: {e}")
        segments = []
    
    # segments配列から7つのセクションのテキストを抽出
    # セクション順序: hook, intro, point1, point2, point3, summary, cta
    section_keys = ['hook', 'intro', 'point1', 'point2', 'point3', 'summary', 'cta']
    
    # テキスト取得（segments配列から、またはフォールバック）
    texts = {}
    durations = {}
    if len(segments) >= 7:
        # segments配列から取得
        texts['hook'] = segments[0].get('telop', 'フックテキストがありません')
        texts['intro'] = segments[1].get('telop', '導入テキストがありません')
        texts['point1'] = segments[2].get('telop', 'ポイント1がありません')
        texts['point2'] = segments[3].get('telop', 'ポイント2がありません')
        texts['point3'] = segments[4].get('telop', 'ポイント3がありません')
        texts['summary'] = segments[5].get('telop', 'まとめがありません')
        texts['cta'] = segments[6].get('telop', 'CTAがありません')
        
        # durationもsegmentsから取得（フォールバック値あり）
        durations = {
            'hook': segments[0].get('duration', 3),
            'intro': segments[1].get('duration', 10),
            'point1': segments[2].get('duration', 13),
            'point2': segments[3].get('duration', 13),
            'point3': segments[4].get('duration', 14),
            'summary': segments[5].get('duration', 20),
            'cta': segments[6].get('duration', 7)
        }
    else:
        # フォールバック: 古い形式のプロパティから取得
        texts['hook'] = properties.get('hook_text_5options', {}).get('rich_text', [{}])[0].get('plain_text', 'フックテキストがありません')
        texts['intro'] = properties.get('introduction_text', {}).get('rich_text', [{}])[0].get('plain_text', '導入テキストがありません')
        texts['point1'] = properties.get('main_point_1', {}).get('rich_text', [{}])[0].get('plain_text', 'ポイント1がありません')
        texts['point2'] = properties.get('main_point_2', {}).get('rich_text', [{}])[0].get('plain_text', 'ポイント2がありません')
        texts['point3'] = properties.get('main_point_3', {}).get('rich_text', [{}])[0].get('plain_text', 'ポイント3がありません')
        texts['summary'] = properties.get('summary_text', {}).get('rich_text', [{}])[0].get('plain_text', 'まとめがありません')
        texts['cta'] = properties.get('cta_text_3options', {}).get('rich_text', [{}])[0].get('plain_text', 'CTAがありません')
        durations = {
            "hook": 3, "intro": 10, "point1": 13,
            "point2": 13, "point3": 14, "summary": 20, "cta": 7
        }
    
    # ブランドカラー取得
    brand_colors_raw = properties.get('Brand Colors', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
    try:
        brand_colors = json.loads(brand_colors_raw) if brand_colors_raw else DEFAULT_BRAND_COLORS
    except:
        brand_colors = DEFAULT_BRAND_COLORS
    
    # 視覚要素取得
    visual_elements_raw = properties.get('Visual Elements', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
    try:
        visual_elements = json.loads(visual_elements_raw) if visual_elements_raw else {}
    except:
        visual_elements = {}
    
    # Duration Config取得（segmentsから取得した場合は上書きされない）
    duration_config_raw = properties.get('Duration Config', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
    try:
        duration_config_override = json.loads(duration_config_raw) if duration_config_raw else {}
        # segmentsから取得したdurationを上書き（Duration Configが指定されている場合）
        for key in durations:
            if key in duration_config_override:
                durations[key] = duration_config_override[key]
    except:
        pass
    
    # Motion Prompts取得
    motion_prompts_raw = properties.get('Motion Prompts', {}).get('rich_text', [{}])[0].get('plain_text', '{}')
    try:
        motion_prompts = json.loads(motion_prompts_raw) if motion_prompts_raw else {
            "hook": "dramatic zoom in effect, professional business style, sharp focus",
            "intro": "smooth slide transition, calm professional tone, steady camera",
            "point1": "gentle fade in with subtle zoom, educational style, clean motion",
            "point2": "gentle fade in with subtle zoom, educational style, clean motion",
            "point3": "gentle fade in with subtle zoom, educational style, clean motion",
            "summary": "cinematic pan effect, inspiring tone, smooth movement",
            "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
        }
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
    
    slides = []
    
    # 1. フック
    icon_hook = visual_elements.get('hook', {}).get('icon', '⚠️')
    slide_hook = create_slide(texts['hook'], "hook", durations['hook'], brand_colors, icon=icon_hook)
    slides.append({
        "section": "hook",
        "duration": durations['hook'],
        "image_base64": image_to_base64(slide_hook),
        "filename": "slide_1_hook.png",
        "motion_prompt": motion_prompts.get('hook', ''),
        "text": texts['hook']
    })
    
    # 2. 導入
    slide_intro = create_slide(texts['intro'], "intro", durations['intro'], brand_colors)
    slides.append({
        "section": "intro",
        "duration": durations['intro'],
        "image_base64": image_to_base64(slide_intro),
        "filename": "slide_2_intro.png",
        "motion_prompt": motion_prompts.get('intro', ''),
        "text": texts['intro']
    })
    
    # 3-5. 本編3ポイント
    points = [
        (texts['point1'], durations['point1'], "point1"),
        (texts['point2'], durations['point2'], "point2"),
        (texts['point3'], durations['point3'], "point3")
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
    slide_summary = create_slide(texts['summary'], "summary", durations['summary'], brand_colors)
    slides.append({
        "section": "summary",
        "duration": durations['summary'],
        "image_base64": image_to_base64(slide_summary),
        "filename": "slide_6_summary.png",
        "motion_prompt": motion_prompts.get('summary', ''),
        "text": texts['summary']
    })
    
    # 7. CTA
    slide_cta = create_slide(texts['cta'], "cta", durations['cta'], brand_colors)
    slides.append({
        "section": "cta",
        "duration": durations['cta'],
        "image_base64": image_to_base64(slide_cta),
        "filename": "slide_7_cta.png",
        "motion_prompt": motion_prompts.get('cta', ''),
        "text": texts['cta']
    })
    
    return slides

# メイン処理
script_data = items[0]['json']
slides = generate_slides(script_data)

# n8nのCodeノードが配列を返す場合、自動的に各要素が個別のアイテムとして扱われる
return slides

