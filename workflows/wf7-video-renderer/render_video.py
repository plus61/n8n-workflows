#!/usr/bin/env python3
"""
WF7 動画レンダリング CLI
縦型ショート動画（1080×1920）を生成するPythonスクリプト

Requirements:
    - Python 3.11+
    - moviepy
    - ffmpeg
    - pillow
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class VideoRenderer:
    """動画レンダラークラス"""
    
    def __init__(self, output_width=1080, output_height=1920, fps=30):
        self.output_width = output_width
        self.output_height = output_height
        self.fps = fps
        
    def load_config(self, script_path: str, assets_path: str) -> tuple:
        """
        script.json と assets.json を読み込み
        
        Args:
            script_path: script.jsonのパス
            assets_path: assets.jsonのパス
            
        Returns:
            (script_data, assets_data)のタプル
        """
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
            
        with open(assets_path, 'r', encoding='utf-8') as f:
            assets_data = json.load(f)
            
        return script_data, assets_data
    
    def load_template(self, template_id: str = 'default') -> Dict:
        """
        テンプレートJSONを読み込み
        
        Args:
            template_id: テンプレートID
            
        Returns:
            テンプレート設定辞書
        """
        template_path = Path(__file__).parent / 'templates' / f'{template_id}.json'
        
        # デフォルトテンプレート
        default_template = {
            'font_family': 'Arial',
            'font_size': 60,
            'text_color': (255, 255, 255),
            'text_bg_color': (0, 0, 0, 180),
            'text_position': 'center',
            'animation': 'fade',
            'bgm': None
        }
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return default_template
    
    def create_text_clip(self, text: str, duration: float, template: Dict) -> mp.VideoClip:
        """
        テキストクリップを生成
        
        Args:
            text: 表示テキスト
            duration: 表示時間（秒）
            template: テンプレート設定
            
        Returns:
            moviepy TextClip
        """
        # PIL で背景付きテキスト画像を生成
        img = Image.new('RGBA', (self.output_width, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # フォント設定（システムフォントまたはデフォルト）
        try:
            font = ImageFont.truetype(template.get('font_family', 'Arial'), template.get('font_size', 60))
        except:
            font = ImageFont.load_default()
        
        # テキストサイズ取得
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 背景矩形
        padding = 20
        bg_color = tuple(template.get('text_bg_color', (0, 0, 0, 180)))
        draw.rectangle(
            [(self.output_width//2 - text_width//2 - padding, 50 - padding),
             (self.output_width//2 + text_width//2 + padding, 50 + text_height + padding)],
            fill=bg_color
        )
        
        # テキスト描画
        text_color = tuple(template.get('text_color', (255, 255, 255)))
        draw.text((self.output_width//2 - text_width//2, 50), text, font=font, fill=text_color)
        
        # PIL Image → moviepy ImageClip
        text_clip = mp.ImageClip(np.array(img)).set_duration(duration)
        
        return text_clip
    
    def create_scene(self, segment: Dict, asset_path: str, template: Dict) -> mp.VideoClip:
        """
        1つのシーンを生成（背景 + テキスト + B-roll）
        
        Args:
            segment: スクリプトセグメント
            asset_path: アセットファイルパス
            template: テンプレート設定
            
        Returns:
            合成されたVideoClip
        """
        duration = segment.get('duration', 10)
        
        # 背景動画/画像
        if asset_path.endswith(('.mp4', '.mov', '.avi')):
            bg_clip = mp.VideoFileClip(asset_path).resize((self.output_width, self.output_height))
        else:
            bg_img = Image.open(asset_path).resize((self.output_width, self.output_height))
            bg_clip = mp.ImageClip(np.array(bg_img))
        
        bg_clip = bg_clip.set_duration(duration)
        
        # テキストクリップ
        text_clip = self.create_text_clip(segment['telop'], duration, template)
        text_clip = text_clip.set_position(('center', 'top'))
        
        # 合成
        scene = mp.CompositeVideoClip([bg_clip, text_clip], size=(self.output_width, self.output_height))
        
        return scene
    
    def render_video(self, script_data: Dict, assets_data: Dict, template: Dict, 
                     output_path: str, subtitle_path: str = None) -> Dict:
        """
        動画をレンダリング
        
        Args:
            script_data: スクリプトデータ
            assets_data: アセットデータ
            template: テンプレート設定
            output_path: 出力動画パス
            subtitle_path: 字幕SRTパス（オプション）
            
        Returns:
            レンダリング結果（videoUrl, thumbUrl, duration）
        """
        scenes = []
        
        # 各セグメントをシーンに変換
        for i, segment in enumerate(script_data['segments']):
            # アセット取得
            asset = next((a for a in assets_data['assets'] if a['assetIndex'] == i), None)
            if not asset:
                print(f"Warning: Asset not found for segment {i}")
                continue
                
            asset_path = asset['fileUrl']  # 実際はダウンロードが必要
            
            # シーン生成
            scene = self.create_scene(segment, asset_path, template)
            scenes.append(scene)
        
        # シーンを連結
        final_video = mp.concatenate_videoclips(scenes, method='compose')
        
        # BGM追加（オプション）
        if template.get('bgm'):
            audio = mp.AudioFileClip(template['bgm']).volumex(0.3)
            audio = audio.audio_loop(duration=final_video.duration)
            final_video = final_video.set_audio(audio)
        
        # 字幕burn-in（オプション）
        if subtitle_path and Path(subtitle_path).exists():
            # ffmpegで字幕をburn-in
            pass  # 実装略
        
        # エンコード
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            preset='fast',
            audio_codec='aac',
            ffmpeg_params=['-crf', '23']
        )
        
        # サムネイル生成（RGBへ変換してJPEG保存）
        thumb_path = output_path.replace('.mp4', '_thumb.jpg')
        try:
            frame_time = min(1.0, max(0, final_video.duration) / 2 or 0)
            frame = final_video.get_frame(frame_time)
            Image.fromarray(frame).convert('RGB').save(thumb_path, format='JPEG')
        except Exception as exc:
            print(f"Warning: Thumbnail generation failed: {exc}")
            thumb_path = None
        
        return {
            'videoUrl': output_path,
            'thumbUrl': thumb_path,
            'duration': final_video.duration
        }


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='WF7 動画レンダリング CLI')
    parser.add_argument('--script', required=True, help='script.jsonのパス')
    parser.add_argument('--assets', required=True, help='assets.jsonのパス')
    parser.add_argument('--subtitle', help='subtitle.srtのパス（オプション）')
    parser.add_argument('--template', default='default', help='テンプレートID')
    parser.add_argument('--out', required=True, help='出力動画パス')
    
    args = parser.parse_args()
    
    # レンダラー初期化
    renderer = VideoRenderer()
    
    # 設定読み込み
    print(f"Loading script: {args.script}")
    script_data, assets_data = renderer.load_config(args.script, args.assets)
    
    print(f"Loading template: {args.template}")
    template = renderer.load_template(args.template)
    
    # レンダリング実行
    print(f"Rendering video to: {args.out}")
    result = renderer.render_video(
        script_data, 
        assets_data, 
        template, 
        args.out,
        args.subtitle
    )
    
    print(f"\n✅ Rendering complete!")
    print(f"Video: {result['videoUrl']}")
    print(f"Thumbnail: {result['thumbUrl']}")
    print(f"Duration: {result['duration']:.2f}s")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
