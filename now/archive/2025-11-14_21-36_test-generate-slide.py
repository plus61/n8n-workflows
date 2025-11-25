#!/usr/bin/env python3
"""
WF7 Phase4a /generate-slide エンドポイントテストスクリプト

作成日時: 2025-11-14 21:36:28 JST

目的：
- FastAPI /generate-slide エンドポイントの機能検証
- 各セクションタイプ（hook, intro, point1-3, summary, cta）のテスト
- バリデーション機能のテスト
- レスポンス形式の検証
- 生成画像の視覚的検証（オプション）

前提条件：
- FastAPIサーバーがローカルで起動していること（uvicorn render_server:app --reload）
- requestsライブラリがインストールされていること（pip install requests）

実行方法：
    python3 now/2025-11-14_21-36_test-generate-slide.py
"""

import requests
import json
import base64
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# FastAPI エンドポイント URL（環境に応じて変更）
BASE_URL = "http://localhost:8000"
GENERATE_SLIDE_URL = f"{BASE_URL}/generate-slide"

# デフォルトブランドカラー（render_server.py と同じ）
DEFAULT_BRAND_COLORS = {
    "background": "#1a1a2e",
    "primary_text": "#ffffff",
    "secondary_text": "#e0e0e0",
    "accent": "#00d4ff",
    "highlight": "#ff6b35"
}

# テスト結果格納
test_results = []


def print_section_header(title: str):
    """テストセクションのヘッダーを表示"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_generate_slide(
    section: str,
    text: str,
    duration: int,
    brand_colors: Optional[Dict[str, str]] = None,
    icon: Optional[str] = None,
    script_id: str = "test-script-id",
    save_image: bool = False,
    test_name: str = ""
) -> Dict[str, Any]:
    """
    /generate-slide エンドポイントをテスト

    Args:
        section: セクションタイプ
        text: 表示テキスト
        duration: スライド表示時間（秒）
        brand_colors: カスタムブランドカラー（オプション）
        icon: アイコン絵文字（オプション）
        script_id: NotionスクリプトID
        save_image: 画像をファイルに保存するか
        test_name: テスト名（ログ用）

    Returns:
        テスト結果を含む辞書
    """
    print(f"\n▶ テスト: {test_name}")
    print(f"  Section: {section}, Duration: {duration}s")
    if icon:
        print(f"  Icon: {icon}")
    if brand_colors:
        print(f"  Brand Colors: Custom")

    # リクエストペイロード作成
    payload = {
        "section": section,
        "text": text,
        "duration": duration,
        "script_id": script_id
    }

    if brand_colors:
        payload["brand_colors"] = brand_colors

    if icon:
        payload["icon"] = icon

    try:
        # POSTリクエスト送信
        print(f"  送信中... {GENERATE_SLIDE_URL}")
        response = requests.post(GENERATE_SLIDE_URL, json=payload, timeout=30)

        # ステータスコード確認
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            # 成功レスポンス
            data = response.json()

            # レスポンス形式検証
            required_fields = [
                "success", "section", "duration", "imageData",
                "image_size_bytes", "script_id", "filename", "mimeType"
            ]

            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                print(f"  ❌ 失敗: レスポンスに必須フィールドがありません: {missing_fields}")
                return {
                    "test_name": test_name,
                    "success": False,
                    "error": f"Missing fields: {missing_fields}"
                }

            # 画像サイズ確認
            image_size_kb = data["image_size_bytes"] / 1024
            print(f"  ✅ 成功: 画像サイズ {image_size_kb:.2f} KB")
            print(f"  ファイル名: {data['filename']}")

            # オプション: 画像をファイルに保存
            if save_image and data.get("imageData"):
                try:
                    output_dir = Path("now/test_output")
                    output_dir.mkdir(exist_ok=True)

                    output_path = output_dir / f"{section}_test.png"

                    # base64デコード
                    image_bytes = base64.b64decode(data["imageData"])

                    # ファイルに保存
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)

                    print(f"  💾 画像保存: {output_path}")
                except Exception as e:
                    print(f"  ⚠️  画像保存失敗: {e}")

            return {
                "test_name": test_name,
                "success": True,
                "section": data["section"],
                "duration": data["duration"],
                "image_size_bytes": data["image_size_bytes"],
                "filename": data["filename"]
            }

        else:
            # エラーレスポンス
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
            except:
                error_detail = response.text

            print(f"  ❌ 失敗: {error_detail}")

            return {
                "test_name": test_name,
                "success": False,
                "status_code": response.status_code,
                "error": error_detail
            }

    except requests.exceptions.RequestException as e:
        print(f"  ❌ リクエストエラー: {e}")
        return {
            "test_name": test_name,
            "success": False,
            "error": str(e)
        }


def test_invalid_section():
    """無効なセクションのバリデーションテスト"""
    print_section_header("バリデーションテスト: 無効なセクション")

    result = test_generate_slide(
        section="invalid_section",
        text="このセクションは無効です",
        duration=3,
        test_name="無効なセクション"
    )

    # ステータスコード 400 が期待される
    expected_success = result.get("status_code") == 400

    if expected_success:
        print(f"\n  ✅ バリデーション成功: 400エラーが正しく返されました")
    else:
        print(f"\n  ❌ バリデーション失敗: 期待される400エラーが返されませんでした")

    test_results.append({
        **result,
        "expected_validation": expected_success
    })


def test_invalid_duration():
    """無効なdurationのバリデーションテスト"""
    print_section_header("バリデーションテスト: 無効なduration")

    # duration = 0 (範囲外)
    result1 = test_generate_slide(
        section="hook",
        text="duration=0のテスト",
        duration=0,
        test_name="duration=0（範囲外）"
    )

    # duration = 21 (範囲外)
    result2 = test_generate_slide(
        section="hook",
        text="duration=21のテスト",
        duration=21,
        test_name="duration=21（範囲外）"
    )

    # 両方とも 400 エラーが期待される
    validation_success = (
        result1.get("status_code") == 400 and
        result2.get("status_code") == 400
    )

    if validation_success:
        print(f"\n  ✅ バリデーション成功: 無効なdurationが正しく拒否されました")
    else:
        print(f"\n  ❌ バリデーション失敗: 無効なdurationの処理が不正です")

    test_results.extend([
        {**result1, "expected_validation": result1.get("status_code") == 400},
        {**result2, "expected_validation": result2.get("status_code") == 400}
    ])


def test_all_sections():
    """全セクションタイプのテスト"""
    print_section_header("全セクションタイプのテスト")

    test_cases = [
        {
            "section": "hook",
            "text": "あなたは知っていますか？\nこの驚きの事実を...",
            "duration": 3,
            "icon": "⚡",
            "test_name": "Hook スライド"
        },
        {
            "section": "intro",
            "text": "今日は重要なテーマについて\nお話しします",
            "duration": 4,
            "icon": "📖",
            "test_name": "Intro スライド"
        },
        {
            "section": "point1",
            "text": "ポイント1：\n最初の重要なポイントです",
            "duration": 5,
            "icon": "1️⃣",
            "test_name": "Point1 スライド"
        },
        {
            "section": "point2",
            "text": "ポイント2：\n次の重要なポイントです",
            "duration": 5,
            "icon": "2️⃣",
            "test_name": "Point2 スライド"
        },
        {
            "section": "point3",
            "text": "ポイント3：\n最後の重要なポイントです",
            "duration": 5,
            "icon": "3️⃣",
            "test_name": "Point3 スライド"
        },
        {
            "section": "summary",
            "text": "まとめ：\n今日のポイントを振り返りましょう",
            "duration": 4,
            "icon": "📝",
            "test_name": "Summary スライド"
        },
        {
            "section": "cta",
            "text": "詳しくはプロフィールのリンクから\nご確認ください！",
            "duration": 3,
            "icon": "👉",
            "test_name": "CTA スライド"
        }
    ]

    for test_case in test_cases:
        result = test_generate_slide(
            save_image=True,  # 各セクションの画像を保存
            **test_case
        )
        test_results.append(result)


def test_custom_brand_colors():
    """カスタムブランドカラーのテスト"""
    print_section_header("カスタムブランドカラーのテスト")

    custom_colors = {
        "background": "#2c3e50",
        "primary_text": "#ecf0f1",
        "secondary_text": "#bdc3c7",
        "accent": "#e74c3c",
        "highlight": "#f39c12"
    }

    result = test_generate_slide(
        section="hook",
        text="カスタムカラーのテスト",
        duration=3,
        brand_colors=custom_colors,
        icon="🎨",
        save_image=True,
        test_name="カスタムブランドカラー"
    )

    test_results.append(result)


def test_default_brand_colors():
    """デフォルトブランドカラーのテスト"""
    print_section_header("デフォルトブランドカラーのテスト")

    result = test_generate_slide(
        section="hook",
        text="デフォルトカラーのテスト",
        duration=3,
        icon="🎨",
        save_image=True,
        test_name="デフォルトブランドカラー"
    )

    test_results.append(result)


def print_test_summary():
    """テスト結果サマリーを表示"""
    print_section_header("テスト結果サマリー")

    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.get("success", False))
    failed_tests = total_tests - passed_tests

    print(f"\n総テスト数: {total_tests}")
    print(f"成功: {passed_tests}")
    print(f"失敗: {failed_tests}")

    if failed_tests > 0:
        print("\n失敗したテスト:")
        for result in test_results:
            if not result.get("success", False):
                print(f"  ❌ {result['test_name']}: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)

    if failed_tests == 0:
        print("✅ すべてのテストが成功しました！")
    else:
        print(f"❌ {failed_tests}件のテストが失敗しました")

    print("=" * 70)

    return failed_tests == 0


def main():
    """メイン実行"""
    print("=" * 70)
    print("  WF7 Phase4a /generate-slide エンドポイントテスト")
    print("  作成日時: 2025-11-14 21:36:28 JST")
    print("=" * 70)

    # FastAPIサーバーの接続確認
    print(f"\nFastAPIサーバー接続確認: {BASE_URL}")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ サーバー接続成功")
        else:
            print(f"❌ サーバー接続失敗: Status {health_response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ サーバーに接続できません: {e}")
        print("\nFastAPIサーバーを起動してください:")
        print("  cd workflows/wf7-video-renderer")
        print("  uvicorn render_server:app --reload")
        sys.exit(1)

    # テスト実行
    test_all_sections()
    test_custom_brand_colors()
    test_default_brand_colors()
    test_invalid_section()
    test_invalid_duration()

    # 結果サマリー
    all_passed = print_test_summary()

    # 終了コード
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
