import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 🚩 テストモード（True にすると強制的に「在庫復活通知」を送る）
TEST_MODE = True

def check_stock():
    url = "https://books.rakuten.co.jp/rb/18210481/"  # Nintendo Switch 2 商品ページ

    if TEST_MODE:
        # テスト通知を送信
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=f"[テスト通知] Nintendo Switch 2 在庫復活！ {url}")
        )
        print("[テスト通知] Nintendo Switch 2 在庫復活！ → 通知送信")
        return

    # --- 通常の在庫チェック処理 ---
    res = requests.get(url, timeout=10)
    if res.status_code != 200:
        print("ページ取得失敗 → 通知スキップ")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    status = soup.find("span", class_="salesStatus")

    if status and "ご注文できない商品" in status.text:
        print("Nintendo Switch 2 在庫なし → 通知スキップ")
    else:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=f"Nintendo Switch 2 在庫復活！ {url}")
        )
        print("Nintendo Switch 2 在庫復活！ → 通知送信")

if __name__ == "__main__":
    check_stock()
