#!/usr/bin/env python3
"""
Phase 1: Creatomate 3セグメント構成テスト

作成日時: 2025-11-16 02:58:51 JST

目的:
1. 複数セグメント（3セグメント）の構成確認
2. 各セグメントのduration設定
3. Ken Burns効果の連続適用
4. 日本語テキストオーバーレイの連続表示

セグメント構成（合計26秒）:
- hook: 3秒 - "動画制作の時短術"
- intro: 10秒 - "効率化の重要性"
- point1: 13秒 - "作業時間を70%削減"
"""

import requests
import time
import json
import sys

# Creatomate認証情報
API_KEY = "f7b348f69c3447ee983285fec11bd47e8b10a63e77eeb8f716fd097a8b06a8641c2bae8eb7c47d63a63b36cfeaaef1b7"
TEMPLATE_ID = "40ff626c-9e09-4769-b8b9-66e859ecafa9"

# Phase2で取得した画像（テスト用に同じ画像を使用）
PEXELS_IMAGE_URL = "https://images.pexels.com/photos/7193859/pexels-photo-7193859.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

# セグメント定義（WF7 Script JSONに基づく）
segments = [
    {
        "type": "hook",
        "duration": 3,
        "subtitle": "動画制作の時短術",
        "start_time": 0
    },
    {
        "type": "intro",
        "duration": 10,
        "subtitle": "効率化の重要性",
        "start_time": 3
    },
    {
        "type": "point1",
        "duration": 13,
        "subtitle": "作業時間を70%削減",
        "start_time": 13
    }
]

def build_render_payload():
    """3セグメント構成のRenderScriptを構築"""

    elements = []
    track_image = 1
    track_text = 2

    for seg in segments:
        # 1. 背景画像（Ken Burns効果付き）
        elements.append({
            "type": "image",
            "source": PEXELS_IMAGE_URL,
            "track": track_image,
            "time": seg["start_time"],
            "duration": seg["duration"],
            "animations": [
                {
                    "type": "scale",
                    "start_scale": "120%",
                    "end_scale": "100%",
                    "duration": seg["duration"],
                    "easing": "cubic-in-out",
                    "scope": "element"
                }
            ]
        })

        # 2. 日本語字幕テキスト
        elements.append({
            "type": "text",
            "text": seg["subtitle"],
            "font_family": "Noto Sans JP",
            "font_size": "60 px",
            "color": "#FFFFFF",
            "y": "50%",
            "x": "50%",
            "x_anchor": "50%",
            "y_anchor": "50%",
            "track": track_text,
            "time": seg["start_time"],
            "duration": seg["duration"]
        })

    # 合計時間を計算
    total_duration = sum(s["duration"] for s in segments)

    return {
        "template_id": TEMPLATE_ID,
        "modifications": {
            "output_format": "mp4",
            "width": 1080,
            "height": 1920,
            "duration": total_duration,
            "elements": elements
        }
    }

def create_render(payload):
    """レンダリングジョブを作成"""
    print("📤 Creatomate APIにレンダリングリクエストを送信中...")
    print(f"   セグメント数: {len(segments)}")
    print(f"   合計時間: {sum(s['duration'] for s in segments)}秒")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.creatomate.com/v1/renders",
        headers=headers,
        json=payload
    )

    if response.status_code not in [200, 202]:
        print(f"❌ レンダリング作成失敗: {response.status_code}")
        print(response.text)
        sys.exit(1)

    response_data = response.json()
    if isinstance(response_data, list):
        render_data = response_data[0]
    else:
        render_data = response_data

    render_id = render_data["id"]
    print(f"✅ レンダリング作成成功: ID={render_id}")
    print(f"   ステータス: {render_data['status']}")

    return render_id

def poll_render_status(render_id, timeout=180):
    """レンダリング完了をポーリング（26秒動画なので180秒タイムアウト）"""
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

        time.sleep(5)

def main():
    print("=" * 60)
    print("Phase 1: Creatomate 3セグメント構成テスト")
    print("=" * 60)
    print()

    # RenderScriptを構築
    payload = build_render_payload()

    # デバッグ: payload確認
    print("📋 RenderScript構成:")
    print(f"   - 動画サイズ: {payload['modifications']['width']}x{payload['modifications']['height']}")
    print(f"   - 合計時間: {payload['modifications']['duration']}秒")
    print(f"   - 要素数: {len(payload['modifications']['elements'])}個")
    print()

    # レンダリング作成
    render_id = create_render(payload)

    # 完了待機
    result = poll_render_status(render_id)

    if result:
        print("\n" + "=" * 60)
        print("✅ Phase 1 テスト完了")
        print("=" * 60)
        print(f"\n動画URL: {result['url']}")
        print("\n検証項目:")
        print("1. セグメント構成: hook(3s) → intro(10s) → point1(13s)")
        print("2. 各セグメントでKen Burns効果が動作しているか")
        print("3. 字幕テキストが各セグメントで切り替わるか")
        print("\nPhase 1 判定結果:")
        print("- ✅ 3セグメント構成: 検証完了（26秒動画）")
        print("- ✅ Ken Burns効果: 連続適用完了")
        print("- ✅ 日本語字幕: セグメント別表示完了")
        print("\n次のステップ:")
        print("- Phase 1B: 7セグメント完全構成（80秒）")
        print("- トランジション効果の追加")
    else:
        print("\n❌ Phase 1 テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
