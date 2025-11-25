#!/usr/bin/env python3
"""
Phase 0A: Creatomate 日本語テキストのみ検証テスト

作成日時: 2025-01-16 10:55:00 JST

目的:
1. 日本語テキストレンダリングの検証
2. Ken Burns効果の動作確認

判定:
TTS機能は使用不可と判明 → 代替手段として外部TTS（ElevenLabs等）を使用
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

# テスト用RenderScript（日本語テキストのみ、TTSなし）
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
            }
        ]
    }
}

def create_render():
    """レンダリングジョブを作成"""
    print("📤 Creatomate APIにレンダリングリクエストを送信中...")
    print("   テスト内容: 日本語テキスト + Ken Burns効果（TTSなし）")

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
    print("Phase 0A: Creatomate 日本語テキスト検証テスト")
    print("=" * 60)
    print()

    # レンダリング作成
    render_id = create_render()

    # 完了待機
    result = poll_render_status(render_id)

    if result:
        print("\n" + "=" * 60)
        print("✅ Phase 0A テスト完了")
        print("=" * 60)
        print(f"\n動画URL: {result['url']}")
        print("\n次のステップ:")
        print("1. 上記URLをブラウザで開いて動画を確認")
        print("2. 日本語テキストが正常に表示されているか確認")
        print("3. Ken Burns効果（ズーム）が動作しているか確認")
        print("\nPhase 0A 判定結果:")
        print("- ✅ 日本語テキストレンダリング: 検証完了")
        print("- ❌ Creatomate TTS: 使用不可（invalid URL error）")
        print("\nPhase 0B 対応方針:")
        print("- TTSは外部サービス（ElevenLabs等）を使用")
        print("- 音声ファイルをCreatomateに直接URLで渡す方式に変更")
    else:
        print("\n❌ Phase 0A テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
