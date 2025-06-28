#!/usr/bin/env python3
"""
CSV Organizer Pro Build Script
PyInstallerを使用してアプリケーションを実行可能ファイルに変換
"""

import os
import sys
import subprocess
import shutil

def build_app():
    print("🔨 CSV Organizer Pro をビルドしています...")
    
    # 必要なパッケージをインストール
    print("📦 PyInstallerをインストールしています...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # ビルドコマンド
    build_command = [
        "pyinstaller",
        "--onefile",  # 単一ファイルにまとめる
        "--windowed",  # コンソールウィンドウを非表示（macOS/Linux）
        "--name=CSV_Organizer_Pro",  # アプリケーション名
        "--icon=icon.ico",  # アイコン（存在する場合）
        "--add-data=app.py;.",  # アプリケーションファイルを含める
        "launcher.py"  # エントリーポイント
    ]
    
    # macOS/Linux用の調整
    if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        build_command[2] = "--noconsole"  # macOS/Linux用
    
    try:
        # PyInstallerでビルド
        print("🔨 実行可能ファイルを作成しています...")
        subprocess.run(build_command, check=True)
        
        print("✅ ビルドが完了しました！")
        print(f"📁 実行可能ファイル: dist/CSV_Organizer_Pro")
        
        # 配布用フォルダを作成
        dist_folder = "CSV_Organizer_Pro_Distribution"
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        os.makedirs(dist_folder)
        
        # 必要なファイルをコピー
        if os.path.exists("dist/CSV_Organizer_Pro.exe"):
            shutil.copy("dist/CSV_Organizer_Pro.exe", dist_folder)
        elif os.path.exists("dist/CSV_Organizer_Pro"):
            shutil.copy("dist/CSV_Organizer_Pro", dist_folder)
        
        shutil.copy("README.md", dist_folder)
        shutil.copy("requirements.txt", dist_folder)
        
        print(f"📦 配布用フォルダ: {dist_folder}")
        print("\n🎉 アプリケーションの配布準備が完了しました！")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    
    return True

def create_installer():
    """インストーラー作成（オプション）"""
    print("\n🔧 インストーラーの作成は別途必要です")
    print("💡 推奨ツール:")
    print("   - Windows: Inno Setup")
    print("   - macOS: pkgbuild")
    print("   - Linux: AppImage")

if __name__ == "__main__":
    print("🚀 CSV Organizer Pro ビルドツール")
    print("=" * 50)
    
    if build_app():
        create_installer()
        print("\n📋 次のステップ:")
        print("1. dist/CSV_Organizer_Pro_Distribution フォルダを配布")
        print("2. ユーザーはREADME.mdの手順に従ってインストール")
        print("3. 必要に応じてインストーラーを作成")
    else:
        print("\n❌ ビルドに失敗しました")
        sys.exit(1) 