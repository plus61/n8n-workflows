#!/usr/bin/env python3
"""
Phase 0: Creatomate API単体テスト - 日本語テキスト + TTS検証

作成日時: 2025-01-16 10:30:00 JST

目的:
1. 日本語テキストレンダリングの検証
2. 日本語TTS品質の検証
3. Ken Burns効果の動作確認

Go/No-Go基準:
- 日本語テキスト: 正常表示、文字化けなし
- 日本語TTS: 聞き取れる品質（主観評価70点以上）
- レンダリング時間: 3秒動画が60秒以内に完成
"""

import requests
import time
import json
import sys

# ユーザーのCreatomate認証情報
API_KEY = "f7b348f69c3447ee983285fec11bd47e8b10a63e77eeb8f716fd097a8b06a8641c2bae8eb7c47d63a63b36cfeaaef1b7"
TEMPLATE_ID = "40ff626c-9e09-4769-b8b9-66e859ecafa9"

# Phase2で取得した最初の画像（Pexels）
PEXELS_IMAGE_URL = "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

# テスト用RenderScript（3秒の日本語テキスト + TTS）
render_payload = {
    "template_id": TEMPLATE_ID,
    "modifications": {
        "output_format": "mp4",
        "width": 1080,
        "height": 1920,
        "duration": 3,
        "elements": [
            # 1. 背景画像（Ken Burns効果付き）
            {
                "type": "image",
                "source": PEXELS_IMAGE_URL,
                "track": 1,
                "time": 0,
                "duration": 3,
                "animations": [
                    {
                        "type": "scale",
                        "start_scale": "120%",
                        "end_scale": "100%",
                        "duration": 3,
                        "easing": "cubic-in-out",
                        "scope": "element"
                    }
                ]
            },

            # 2. 日本語テキストオーバーレイ（CRITICAL検証）
            {
                "type": "text",
                "text": "動画制作の時短術",
                "font_family": "Noto Sans JP",
                "font_size": "60 px",
                "color": "#FFFFFF",
                "y": "50%",
                "x": "50%",
                "x_anchor": "50%",
                "y_anchor": "50%",
                "track": 2,
                "time": 0,
                "duration": 3
            },

            # 3. 日本語TTS（CRITICAL検証）
            {
                "type": "audio",
                "source": "tts://ja-JP:動画制作の時短術を知りたいですか？",
                "track": 3,
                "time": 0,
                "duration": 3
            }
        ]
    }
}

def create_render():
    """レンダリングジョブを作成"""
    print("📤 Creatomate APIにレンダリングリクエストを送信中...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.creatomate.com/v1/renders",
        headers=headers,
        json=render_payload
    )

    # 200 OK または 202 Accepted を成功として扱う
    if response.status_code not in [200, 202]:
        print(f"❌ レンダリング作成失敗: {response.status_code}")
        print(response.text)
        sys.exit(1)

    # レスポンスは配列で返ってくる場合がある
    response_data = response.json()
    if isinstance(response_data, list):
        render_data = response_data[0]
    else:
        render_data = response_data

    render_id = render_data["id"]
    print(f"✅ レンダリング作成成功: ID={render_id}")
    print(f"   ステータス: {render_data['status']}")

    return render_id

def poll_render_status(render_id, timeout=120):
    """レンダリング完了をポーリング"""
    print(f"\n⏳ レンダリング完了を待機中（最大{timeout}秒）...")

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    start_time = time.time()
    poll_count = 0

    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            print(f"\n❌ タイムアウト: {timeout}秒経過しても完了しませんでした")
            return None

        response = requests.get(
            f"https://api.creatomate.com/v1/renders/{render_id}",
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ ステータス取得失敗: {response.status_code}")
            return None

        render_data = response.json()
        status = render_data["status"]
        poll_count += 1

        print(f"   [{poll_count}回目] ステータス: {status} ({elapsed:.1f}秒経過)")

        if status == "succeeded":
            print(f"\n✅ レンダリング完了！")
            print(f"   所要時間: {elapsed:.1f}秒")
            print(f"   動画URL: {render_data['url']}")
            return render_data

        elif status == "failed":
            print(f"\n❌ レンダリング失敗")
            if "error_message" in render_data:
                print(f"   エラー: {render_data['error_message']}")
            return None

        # 5秒待機してリトライ
        time.sleep(5)

def main():
    print("=" * 60)
    print("Phase 0: Creatomate 日本語テキスト + TTS検証テスト")
    print("=" * 60)
    print()

    # レンダリング作成
    render_id = create_render()

    # 完了待機
    result = poll_render_status(render_id)

    if result:
        print("\n" + "=" * 60)
        print("✅ Phase 0テスト完了")
        print("=" * 60)
        print(f"\n動画URL: {result['url']}")
        print("\n次のステップ:")
        print("1. 上記URLをブラウザで開いて動画を確認")
        print("2. 日本語テキストが正常に表示されているか確認")
        print("3. 日本語TTSの音声品質を評価（主観評価）")
        print("4. Ken Burns効果（ズーム）が動作しているか確認")
        print("\nGo/No-Go判定:")
        print("- ✅ 日本語テキスト正常表示")
        print("- ✅ TTS品質70点以上")
        print("- ✅ レンダリング60秒以内")
        print("\n全て✅の場合 → Phase 1へ進行")
        print("いずれか❌の場合 → 代替手段を検討")
    else:
        print("\n❌ Phase 0テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
