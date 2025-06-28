import PySimpleGUIQt as sg

# シンプルなウィンドウテスト用レイアウト
layout = [
    [sg.Text("テスト：ウィンドウが表示されました！")],
    [sg.Button("閉じる")]
]

# ウィンドウ作成
window = sg.Window("テストウィンドウ", layout)

# イベントループ
while True:
    event, _ = window.read()
    if event in (None, "閉じる"):
        break

# ウィンドウを閉じる
window.close()