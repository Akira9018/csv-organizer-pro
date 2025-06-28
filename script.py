import pandas as pd

def main():
    # 1. ファイル読み込み
    path = input("読み込む CSV/XLSX ファイルのパスを入力してください: ").strip()
    try:
        if path.lower().endswith(".csv"):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
    except Exception as e:
        print(f"ファイルが見つからないか、読み込みに失敗しました: {e}")
        return

    # 2. 列一覧を表示
    print("\n---- 列一覧 ----")
    for idx, col in enumerate(df.columns):
        print(f"{idx}: {col}")
    print("----------------\n")

    # 3. 抽出したい列番号を入力
    nums = input("出力したい列の番号をカンマ区切りで入力: ").split(",")
    try:
        indices = [int(n.strip()) for n in nums if n.strip() != ""]
    except ValueError:
        print("番号はカンマ区切りの整数で入力してください。")
        return

    # 4. 空列追加（任意）
    empty = input("追加したい空列名があれば入力（不要なら Enter）: ").strip()
    if empty:
        df[empty] = ""              # 空列を追加
        indices.append(len(df.columns)-1)

    # 5. 並び替え：入力した順序で列を並べる
    selected_cols = [df.columns[i] for i in indices]

    # 6. 出力ファイル名取得＆拡張子自動付与
    out = input("出力ファイル名を入力（例: out.csv）: ").strip() or "out.csv"
    if not out.lower().endswith((".csv", ".xlsx")):
        out += ".csv"              # 書き忘れ自動付与

    # 7. 保存
    try:
        if out.lower().endswith(".csv"):
            df[selected_cols].to_csv(out, index=False)
        else:
            df[selected_cols].to_excel(out, index=False)
        print(f"\n完了しました。{out} を生成しました。")
    except Exception as e:
        print(f"ファイルの書き出しに失敗しました: {e}")

if __name__ == "__main__":
    main()
