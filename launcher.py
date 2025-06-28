#!/usr/bin/env python3
"""
CSV Organizer Pro Launcher
ローカルアプリケーションとして起動するためのランチャー
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def main():
    print("🚀 CSV Organizer Pro を起動しています...")
    
    # 現在のディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Streamlitアプリのパス
    app_path = os.path.join(current_dir, "app.py")
    
    try:
        # Streamlitアプリを起動
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
        
        print("✅ アプリケーションが起動しました")
        print("🌐 ブラウザで http://localhost:8501 にアクセスしてください")
        
        # 少し待ってからブラウザを開く
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        print("\n📋 使用方法:")
        print("1. ブラウザでCSVまたはExcelファイルをアップロード")
        print("2. データの整理・変換を行います")
        print("3. 処理済みファイルをダウンロード")
        print("\n❌ 終了するには Ctrl+C を押してください")
        
        # プロセスが終了するまで待機
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 アプリケーションを終了します...")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("💡 必要なパッケージがインストールされているか確認してください:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main() 