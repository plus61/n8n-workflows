#!/usr/bin/env python3
"""
WF7 FFmpeg Direct Execution Video Renderer
Phase1ハイブリッド方式: MoviePyラッパーを排除し、FFmpegを直接実行して12x速度改善

Requirements:
    - Python 3.11+
    - ffmpeg (system)
    - PIL/Pillow (font verification)
"""

import argparse
import json
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import os


class FFmpegVideoRenderer:
    """FFmpeg直接実行による動画レンダラークラス"""

    def __init__(self, output_width=1080, output_height=1920, fps=30):
        self.output_width = output_width
        self.output_height = output_height
        self.fps = fps
        self.font_path = self._detect_japanese_font()

    def _detect_japanese_font(self) -> str:
        """
        日本語フォントを検出

        Returns:
            フォントファイルパス
        """
        # Railwayコンテナでの候補
        font_candidates = [
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",  # macOS
            "C:\\Windows\\Fonts\\msgothic.ttc",  # Windows
        ]

        for font in font_candidates:
            if Path(font).exists():
                print(f"✓ Found Japanese font: {font}")
                return font

        print("⚠ Japanese font not found, using default")
        return "Arial"  # Fallback

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

    def build_ffmpeg_command(
        self,
        script_data: Dict,
        assets_data: Dict,
        output_path: str,
        bgm_path: Optional[str] = None,
        narration_path: Optional[str] = None
    ) -> List[str]:
        """
        FFmpegコマンドを構築

        Args:
            script_data: スクリプトデータ
            assets_data: アセットデータ
            output_path: 出力動画パス
            bgm_path: BGMファイルパス（オプション）
            narration_path: ナレーションファイルパス（オプション）

        Returns:
            FFmpegコマンドリスト
        """
        segments = script_data['segments']
        assets = assets_data['assets']

        # 1. Input files (-i) を構築
        cmd = ['ffmpeg', '-y']  # -y: 上書き確認なし

        input_index = 0
        for i, segment in enumerate(segments):
            # 対応するasset取得
            asset = next((a for a in assets if a['assetIndex'] == i), None)
            if not asset:
                raise ValueError(f"Asset not found for segment {i}")

            asset_path = asset['fileUrl']
            duration = segment.get('duration', 10)

            # 静止画を動画として扱う（-loop 1 -t duration）
            cmd.extend(['-loop', '1', '-t', str(duration), '-i', asset_path])
            input_index += 1

        # BGM追加（オプション）
        bgm_index = None
        if bgm_path and Path(bgm_path).exists():
            cmd.extend(['-i', bgm_path])
            bgm_index = input_index
            input_index += 1

        # Narration追加（オプション）
        narration_index = None
        if narration_path and Path(narration_path).exists():
            cmd.extend(['-i', narration_path])
            narration_index = input_index
            input_index += 1

        # 2. Filter_complex を構築
        filter_parts = []
        video_labels = []

        for i, segment in enumerate(segments):
            telop = segment['telop'].replace("'", "\\'").replace('"', '\\"')

            # 各セグメントに対して：スケール → クロップ → テキストオーバーレイ
            filter_parts.append(
                f"[{i}:v]scale={self.output_width}:{self.output_height}:"
                f"force_original_aspect_ratio=increase,"
                f"crop={self.output_width}:{self.output_height},"
                f"drawtext="
                f"text='{telop}':"
                f"fontfile={self.font_path}:"
                f"fontsize=60:"
                f"fontcolor=white:"
                f"box=1:"
                f"boxcolor=black@0.7:"
                f"boxborderw=10:"
                f"x=(w-text_w)/2:"
                f"y=h-150[v{i}]"
            )
            video_labels.append(f"[v{i}]")

        # 3. セグメント連結
        concat_inputs = ''.join(video_labels)
        filter_parts.append(
            f"{concat_inputs}concat=n={len(segments)}:v=1:a=0[outv]"
        )

        # 4. オーディオミキシング
        audio_inputs = []

        if narration_index is not None:
            # Narrationは100%音量
            filter_parts.append(f"[{narration_index}:a]volume=1.0[narration]")
            audio_inputs.append("[narration]")

        if bgm_index is not None:
            # BGMは30%音量にしてループ
            # Note: BGMループは duration=longest で自動調整
            filter_parts.append(f"[{bgm_index}:a]volume=0.3,aloop=loop=-1:size=2e+09[bgm]")
            audio_inputs.append("[bgm]")

        if audio_inputs:
            # 複数オーディオをミックス
            audio_mix = ''.join(audio_inputs)
            filter_parts.append(
                f"{audio_mix}amix=inputs={len(audio_inputs)}:duration=first[outa]"
            )
            has_audio = True
        else:
            has_audio = False

        # Filter_complex 文字列結合
        filter_complex = ';'.join(filter_parts)
        cmd.extend(['-filter_complex', filter_complex])

        # 5. Output mapping
        cmd.extend(['-map', '[outv]'])
        if has_audio:
            cmd.extend(['-map', '[outa]'])

        # 6. Encoding parameters
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'fast',  # fast encoding
            '-crf', '23',  # quality (lower = better, 18-28 recommended)
            '-pix_fmt', 'yuv420p',  # compatibility
            '-aspect', '9:16',
        ])

        if has_audio:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '128k',
            ])

        cmd.append(output_path)

        return cmd

    def generate_thumbnail(self, video_path: str, thumb_path: str, frame_time: float = 1.0):
        """
        動画からサムネイルを生成

        Args:
            video_path: 動画ファイルパス
            thumb_path: サムネイル出力パス
            frame_time: 抽出するフレーム時間（秒）
        """
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', str(frame_time),
            '-vframes', '1',
            '-q:v', '2',  # quality (1-31, lower = better)
            thumb_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Thumbnail generation failed: {result.stderr}")

    def get_video_duration(self, video_path: str) -> float:
        """
        動画の長さを取得（ffprobe使用）

        Args:
            video_path: 動画ファイルパス

        Returns:
            動画の長さ（秒）
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Duration detection failed: {result.stderr}")

        return float(result.stdout.strip())

    def render_video(
        self,
        script_data: Dict,
        assets_data: Dict,
        output_path: str,
        bgm_path: Optional[str] = None,
        narration_path: Optional[str] = None
    ) -> Dict:
        """
        動画をレンダリング（FFmpeg直接実行）

        Args:
            script_data: スクリプトデータ
            assets_data: アセットデータ
            output_path: 出力動画パス
            bgm_path: BGMファイルパス（オプション）
            narration_path: ナレーションファイルパス（オプション）

        Returns:
            レンダリング結果（videoUrl, thumbUrl, duration）
        """
        print(f"🎬 Starting FFmpeg rendering...")
        print(f"   Segments: {len(script_data['segments'])}")
        print(f"   Assets: {len(assets_data['assets'])}")
        print(f"   Font: {self.font_path}")

        # FFmpegコマンド構築
        cmd = self.build_ffmpeg_command(
            script_data,
            assets_data,
            output_path,
            bgm_path,
            narration_path
        )

        # デバッグ用にコマンド表示
        print(f"\n📝 FFmpeg command:")
        print(' '.join(cmd))

        # FFmpeg実行 (timeout=600秒, stderr出力抑制)
        print(f"\n⚡ Executing FFmpeg...")
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                # エラー時のみstderrの最後の50行を表示
                stderr_lines = result.stderr.strip().split('\n')
                stderr_tail = '\n'.join(stderr_lines[-50:]) if len(stderr_lines) > 50 else result.stderr
                print(f"❌ FFmpeg failed:")
                print(stderr_tail)
                raise RuntimeError(f"FFmpeg rendering failed: {stderr_tail}")

        except subprocess.TimeoutExpired:
            print(f"❌ FFmpeg timeout after 600 seconds")
            raise RuntimeError(f"FFmpeg rendering timeout (600s limit exceeded)")

        print(f"✅ Video rendered: {output_path}")

        # サムネイル生成
        thumb_path = output_path.replace('.mp4', '_thumb.jpg')
        try:
            duration = self.get_video_duration(output_path)
            frame_time = min(1.0, duration / 2)
            self.generate_thumbnail(output_path, thumb_path, frame_time)
            print(f"✅ Thumbnail generated: {thumb_path}")
        except Exception as exc:
            print(f"⚠ Thumbnail generation failed: {exc}")
            thumb_path = None
            duration = 0

        return {
            'videoUrl': output_path,
            'thumbUrl': thumb_path,
            'duration': duration
        }


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='WF7 FFmpeg Direct Video Renderer')
    parser.add_argument('--script', required=True, help='script.jsonのパス')
    parser.add_argument('--assets', required=True, help='assets.jsonのパス')
    parser.add_argument('--bgm', help='BGMファイルパス（オプション）')
    parser.add_argument('--narration', help='ナレーションファイルパス（オプション）')
    parser.add_argument('--out', required=True, help='出力動画パス')

    args = parser.parse_args()

    # レンダラー初期化
    renderer = FFmpegVideoRenderer()

    # 設定読み込み
    print(f"📂 Loading configuration...")
    print(f"   Script: {args.script}")
    print(f"   Assets: {args.assets}")
    script_data, assets_data = renderer.load_config(args.script, args.assets)

    # レンダリング実行
    result = renderer.render_video(
        script_data,
        assets_data,
        args.out,
        args.bgm,
        args.narration
    )

    print(f"\n✅ Rendering complete!")
    print(f"   Video: {result['videoUrl']}")
    print(f"   Thumbnail: {result['thumbUrl']}")
    print(f"   Duration: {result['duration']:.2f}s")

    return 0


if __name__ == '__main__':
    sys.exit(main())
