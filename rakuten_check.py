import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def check_stock():
    product_name = "Nintendo Switch 2"
    url = "https://books.rakuten.co.jp/rb/18210481/"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"{product_name} の在庫情報取得失敗 → 通知スキップ ({e})")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    status = soup.find("span", class_="salesStatus")

    # 在庫チェック条件
    if status and "ご注文できない商品" in status.text:
        print(f"{product_name} 在庫なし → 通知スキップ")
    else:
        # 在庫が復活した場合に通知
        message = TextSendMessage(
            text=f"{product_name} 在庫復活！\n{url}"
        )
        try:
            line_bot_api.push_message(LINE_USER_ID, message)
            print(f"{product_name} 在庫復活 → 通知送信")
        except Exception as e:
            print(f"LINE通知失敗: {e}")

if __name__ == "__main__":
    check_stock()
