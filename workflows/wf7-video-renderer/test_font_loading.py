#!/usr/bin/env python3
"""
WF7 Phase4a フォント読み込みテストスクリプト

Railway環境でフォントが正しくインストールされているかを検証
作成日時: 2025-11-14 19:24:54 JST
"""

from PIL import ImageFont
import sys
import os

# テスト対象のフォントパス（phase4a_code_node_fixed.py と同一）
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"

def test_font_file_exists():
    """フォントファイルが存在するかテスト"""
    print("=" * 60)
    print("テスト1: フォントファイルの存在確認")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    for font_name, font_path in [("Regular", FONT_PATH), ("Bold", FONT_BOLD_PATH)]:
        print(f"\n{font_name} フォント: {font_path}")

        if os.path.exists(font_path):
            print(f"  ✅ ファイルが存在します")
            file_size = os.path.getsize(font_path) / (1024 * 1024)  # MB
            print(f"  📊 ファイルサイズ: {file_size:.2f} MB")
            tests_passed += 1
        else:
            print(f"  ❌ ファイルが存在しません")
            tests_failed += 1

            # フォールバック候補のパスを提案
            print(f"  💡 フォールバック候補:")
            fallback_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            for fallback in fallback_paths:
                if os.path.exists(fallback):
                    print(f"    - {fallback} (存在)")
                else:
                    print(f"    - {fallback} (不在)")

    print(f"\n結果: {tests_passed}件成功 / {tests_failed}件失敗")
    return tests_failed == 0


def test_font_loading():
    """フォントが正しく読み込めるかテスト"""
    print("\n" + "=" * 60)
    print("テスト2: フォント読み込みテスト")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    test_cases = [
        ("Regular 70pt", FONT_PATH, 70),
        ("Bold 90pt", FONT_BOLD_PATH, 90),
        ("Regular 40pt", FONT_PATH, 40),
        ("Regular 120pt (icon)", FONT_PATH, 120),
    ]

    for test_name, font_path, font_size in test_cases:
        print(f"\n{test_name}:")
        try:
            font = ImageFont.truetype(font_path, font_size)
            print(f"  ✅ 読み込み成功")
            print(f"  📊 フォント情報: {font.getname()}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ 読み込み失敗: {e}")
            tests_failed += 1

    print(f"\n結果: {tests_passed}件成功 / {tests_failed}件失敗")
    return tests_failed == 0


def test_japanese_rendering():
    """日本語テキストのレンダリングテスト"""
    print("\n" + "=" * 60)
    print("テスト3: 日本語テキストレンダリングテスト")
    print("=" * 60)

    test_texts = [
        "CTAがありません",
        "フックテキストがありません",
        "導入テキストがありません",
        "ポイント1がありません",
    ]

    try:
        font = ImageFont.truetype(FONT_PATH, 70)
        print(f"\n使用フォント: {font.getname()}")

        for text in test_texts:
            bbox = font.getbbox(text)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            print(f"\nテキスト: '{text}'")
            print(f"  描画サイズ: {width}x{height}px")

            if width > 0 and height > 0:
                print(f"  ✅ レンダリング可能")
            else:
                print(f"  ❌ レンダリング失敗（サイズが0）")
                return False

        print(f"\n✅ すべての日本語テキストがレンダリング可能")
        return True

    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        return False


def test_system_fonts():
    """システムにインストールされているフォント一覧を表示"""
    print("\n" + "=" * 60)
    print("参考情報: システムフォント一覧")
    print("=" * 60)

    font_dirs = [
        "/usr/share/fonts/truetype/noto/",
        "/usr/share/fonts/opentype/noto/",
        "/usr/share/fonts/truetype/dejavu/",
    ]

    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            print(f"\n{font_dir}:")
            try:
                files = os.listdir(font_dir)
                for f in sorted(files):
                    if f.endswith(('.ttf', '.ttc', '.otf')):
                        file_path = os.path.join(font_dir, f)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)
                        print(f"  - {f} ({file_size:.2f} MB)")
            except Exception as e:
                print(f"  エラー: {e}")
        else:
            print(f"\n{font_dir}: ディレクトリが存在しません")


def main():
    """メイン実行"""
    print("=" * 60)
    print("WF7 Phase4a フォント読み込みテストスクリプト")
    print("作成日時: 2025-11-14 19:24:54 JST")
    print("=" * 60)

    # 環境情報
    print(f"\nPython バージョン: {sys.version}")
    print(f"実行環境: {os.uname().sysname} {os.uname().release}")

    # テスト実行
    test_results = []

    test_results.append(("フォントファイル存在確認", test_font_file_exists()))
    test_results.append(("フォント読み込み", test_font_loading()))
    test_results.append(("日本語レンダリング", test_japanese_rendering()))

    # システムフォント一覧表示
    test_system_fonts()

    # 最終結果
    print("\n" + "=" * 60)
    print("最終結果")
    print("=" * 60)

    all_passed = True
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ すべてのテストに合格しました")
        print("=" * 60)
        return 0
    else:
        print("❌ 一部のテストが失敗しました")
        print("=" * 60)
        print("\n修正手順:")
        print("1. Dockerfileに fonts-noto-cjk をインストール")
        print("2. Railway環境で再ビルド")
        print("3. このテストを再実行")
        return 1


if __name__ == "__main__":
    sys.exit(main())
