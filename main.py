import os
import pandas as pd
import PySimpleGUIQt as sg # type: ignore

# テンプレート保存先
TEMPLATE_DIR = "templates"
os.makedirs(TEMPLATE_DIR, exist_ok=True)

def load_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    else:
        return pd.read_excel(path)

def save_file(df, path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df.to_csv(path, index=False)
    else:
        df.to_excel(path, index=False)

def main():
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("元ファイル"), sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("CSV/XLSX", "*.csv;*.xlsx"),))],
        [sg.Button("読み込み")],
        [sg.Listbox(values=[], key="-COLUMNS-", size=(30, 15), enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE),
         sg.Column([
             [sg.Button("↑", key="-UP-"), sg.Button("↓", key="-DOWN-")],
             [sg.Button("空列挿入", key="-INSERT-")],
         ])],
        [sg.Button("出力")]
    ]

    window = sg.Window("列選択抽出アプリ", layout)

    df = None

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        if event == "読み込み":
            path = values["-FILE-"]
            try:
                df = load_file(path)
                window["-COLUMNS-"].update(list(df.columns))
            except Exception as e:
                sg.popup_error(f"読み込みエラー:\n{e}")

        if event in ("-UP-", "-DOWN-"):
            curr = window["-COLUMNS-"].get_list_values()
            sel = window["-COLUMNS-"].get_indexes()
            if sel:
                i = sel[0]
                if event == "-UP-" and i > 0:
                    curr[i-1], curr[i] = curr[i], curr[i-1]
                    window["-COLUMNS-"].update(curr, set_to_index=[i-1])
                if event == "-DOWN-" and i < len(curr)-1:
                    curr[i+1], curr[i] = curr[i], curr[i+1]
                    window["-COLUMNS-"].update(curr, set_to_index=[i+1])

        if event == "-INSERT-":
            curr = window["-COLUMNS-"].get_list_values()
            sel = window["-COLUMNS-"].get_indexes()
            pos = sel[-1] + 1 if sel else len(curr)
            col_name = sg.popup_get_text("空列のヘッダー名を入力してください", default_text="空列")
            curr.insert(pos, col_name)
            window["-COLUMNS-"].update(curr)

        if event == "出力" and df is not None:
            cols = window["-COLUMNS-"].get_list_values()
            out_df = pd.DataFrame()
            for col in cols:
                if col in df.columns:
                    out_df[col] = df[col]
                else:
                    out_df[col] = ""
            out_path = sg.pop_
