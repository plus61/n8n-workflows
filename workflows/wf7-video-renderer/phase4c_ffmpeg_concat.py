"""
Phase 4c: FFmpeg 動画結合スクリプト

目的: FAL.aiで生成された7本の動画を1本に結合
出力: 最終的な80秒の完成動画（MP4）

使用方法（n8n Code Node内）:
  from phase4c_ffmpeg_concat import concat_videos
  result = concat_videos(items[0]['json'])
  return result
"""

import subprocess
import os
import json
import tempfile
import time
from pathlib import Path


def download_video(video_url, output_path):
    """
    動画URLからファイルをダウンロード

    Args:
        video_url (str): 動画のURL（Google DriveまたはFAL.ai）
        output_path (str): 保存先パス

    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # Google Drive URLの場合、直接ダウンロードURLに変換
        if "drive.google.com" in video_url:
            # https://drive.google.com/file/d/FILE_ID/view
            # → https://drive.google.com/uc?export=download&id=FILE_ID
            if "/file/d/" in video_url:
                file_id = video_url.split("/file/d/")[1].split("/")[0]
                video_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        # curlでダウンロード（Railwayで利用可能）
        result = subprocess.run(
            ["curl", "-L", "-o", output_path, video_url],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 0:
                print(f"✅ ダウンロード成功: {output_path} ({file_size} bytes)")
                return True
            else:
                print(f"❌ ファイルサイズが0: {output_path}")
                return False
        else:
            print(f"❌ ダウンロード失敗: {video_url}")
            print(f"   stderr: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ ダウンロードエラー: {e}")
        return False


def create_concat_file(video_paths, concat_file_path):
    """
    FFmpeg concat用のテキストファイルを作成

    Args:
        video_paths (list): 動画ファイルパスのリスト
        concat_file_path (str): concat.txtの保存先
    """
    with open(concat_file_path, 'w', encoding='utf-8') as f:
        for video_path in video_paths:
            # FFmpegのconcat形式: file '/path/to/video.mp4'
            f.write(f"file '{video_path}'\n")

    print(f"✅ concat.txt作成完了: {concat_file_path}")


def concat_videos_with_ffmpeg(video_paths, output_path, timeout=600):
    """
    FFmpegで動画を結合

    Args:
        video_paths (list): 動画ファイルパスのリスト（順序付き）
        output_path (str): 出力動画パス
        timeout (int): タイムアウト秒数（デフォルト600秒 = 10分）

    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # concat.txtを作成
        concat_file = os.path.join(os.path.dirname(output_path), 'concat.txt')
        create_concat_file(video_paths, concat_file)

        # FFmpegコマンド実行
        # -safe 0: ファイルパス制限を解除
        # -f concat: concat demuxerを使用
        # -c copy: 再エンコードなし（高速）
        cmd = [
            'ffmpeg',
            '-y',  # 既存ファイル上書き
            '-safe', '0',
            '-f', 'concat',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ]

        print(f"⏳ FFmpeg実行開始: {' '.join(cmd)}")
        start_time = time.time()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        elapsed_time = time.time() - start_time

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ FFmpeg結合成功: {output_path} ({file_size} bytes, {elapsed_time:.2f}秒)")

            # concat.txtを削除
            if os.path.exists(concat_file):
                os.remove(concat_file)

            return True
        else:
            print(f"❌ FFmpeg結合失敗")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ FFmpegタイムアウト（{timeout}秒経過）")
        return False
    except Exception as e:
        print(f"❌ FFmpegエラー: {e}")
        return False


def concat_videos(input_data):
    """
    7本の動画を結合するメイン関数

    Args:
        input_data (dict): Phase 4bからの入力データ
            {
                "script_id": "Notion Record ID",
                "videos_metadata": [
                    {
                        "section": "hook",
                        "duration": 3,
                        "video_url": "https://...",
                        "fal_video_id": "...",
                        "filename": "video_1_hook.mp4"
                    },
                    ...
                ]
            }

    Returns:
        dict: 結合結果
            {
                "success": true,
                "script_id": "...",
                "output_video_path": "/tmp/final_video_xxx.mp4",
                "output_video_size": 12345678,
                "total_duration": 80,
                "videos_count": 7
            }
    """
    script_id = input_data.get('script_id', 'unknown')
    videos_metadata = input_data.get('videos_metadata', [])

    if len(videos_metadata) != 7:
        raise ValueError(f"動画数が不正です。期待: 7本、実際: {len(videos_metadata)}本")

    print(f"🎬 Phase 4c開始: script_id={script_id}, videos={len(videos_metadata)}本")

    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp(prefix='wf7_phase4c_')
    print(f"📁 一時ディレクトリ: {temp_dir}")

    try:
        # 1. 各動画をダウンロード
        downloaded_paths = []
        for i, video_meta in enumerate(videos_metadata, 1):
            section = video_meta.get('section', f'video_{i}')
            video_url = video_meta.get('video_url')

            if not video_url:
                raise ValueError(f"動画URL未設定: section={section}")

            # ダウンロード先パス
            video_filename = f"video_{i}_{section}.mp4"
            video_path = os.path.join(temp_dir, video_filename)

            # ダウンロード実行
            print(f"⏳ [{i}/7] ダウンロード中: {section} ({video_url[:50]}...)")
            if not download_video(video_url, video_path):
                raise RuntimeError(f"動画ダウンロード失敗: {section}")

            downloaded_paths.append(video_path)

        print(f"✅ 全動画ダウンロード完了: {len(downloaded_paths)}本")

        # 2. FFmpegで結合
        output_filename = f"final_video_{script_id}_{int(time.time())}.mp4"
        output_path = os.path.join(temp_dir, output_filename)

        print(f"⏳ FFmpeg結合開始...")
        if not concat_videos_with_ffmpeg(downloaded_paths, output_path):
            raise RuntimeError("FFmpeg結合失敗")

        # 3. 結果情報を取得
        output_size = os.path.getsize(output_path)
        total_duration = sum(v.get('duration', 0) for v in videos_metadata)

        result = {
            "success": True,
            "script_id": script_id,
            "output_video_path": output_path,
            "output_video_size": output_size,
            "total_duration": total_duration,
            "videos_count": len(videos_metadata),
            "temp_dir": temp_dir  # Google Driveアップロード後にクリーンアップ
        }

        print(f"✅ Phase 4c完了: {output_path} ({output_size} bytes, {total_duration}秒)")
        return result

    except Exception as e:
        print(f"❌ Phase 4cエラー: {e}")
        # エラー時は一時ファイルを削除
        cleanup_temp_files(temp_dir)
        raise


def cleanup_temp_files(temp_dir):
    """
    一時ファイルをクリーンアップ

    Args:
        temp_dir (str): 削除する一時ディレクトリ
    """
    try:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            print(f"🧹 一時ファイル削除完了: {temp_dir}")
    except Exception as e:
        print(f"⚠️ 一時ファイル削除エラー: {e}")


# n8n Code Node用エントリーポイント
def main(items):
    """
    n8n Code Nodeから呼び出される関数

    Args:
        items (list): n8nから渡されるアイテム配列

    Returns:
        dict: 結合結果
    """
    if not items or len(items) == 0:
        raise ValueError("入力データがありません")

    input_data = items[0]['json']
    result = concat_videos(input_data)

    return [result]


# テスト用（ローカル実行時）
if __name__ == "__main__":
    # サンプルデータ
    sample_data = {
        "script_id": "29b68d5c-2986-817f-test",
        "videos_metadata": [
            {
                "section": "hook",
                "duration": 3,
                "video_url": "https://example.com/video1.mp4",
                "fal_video_id": "fal_xxx_1",
                "filename": "video_1_hook.mp4"
            },
            {
                "section": "intro",
                "duration": 10,
                "video_url": "https://example.com/video2.mp4",
                "fal_video_id": "fal_xxx_2",
                "filename": "video_2_intro.mp4"
            },
            {
                "section": "point1",
                "duration": 13,
                "video_url": "https://example.com/video3.mp4",
                "fal_video_id": "fal_xxx_3",
                "filename": "video_3_point1.mp4"
            },
            {
                "section": "point2",
                "duration": 13,
                "video_url": "https://example.com/video4.mp4",
                "fal_video_id": "fal_xxx_4",
                "filename": "video_4_point2.mp4"
            },
            {
                "section": "point3",
                "duration": 14,
                "video_url": "https://example.com/video5.mp4",
                "fal_video_id": "fal_xxx_5",
                "filename": "video_5_point3.mp4"
            },
            {
                "section": "summary",
                "duration": 20,
                "video_url": "https://example.com/video6.mp4",
                "fal_video_id": "fal_xxx_6",
                "filename": "video_6_summary.mp4"
            },
            {
                "section": "cta",
                "duration": 7,
                "video_url": "https://example.com/video7.mp4",
                "fal_video_id": "fal_xxx_7",
                "filename": "video_7_cta.mp4"
            }
        ]
    }

    # テスト実行（注意: 実際の動画URLが必要）
    print("動画結合テスト開始...")
    print("⚠️ 注意: 実際の動画URLを使用してください")

    # 実際のテストは実際の動画URLで実行
    # result = concat_videos(sample_data)
    # print(f"✅ テスト完了: {result}")
