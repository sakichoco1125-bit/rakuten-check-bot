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
    url = "https://books.rakuten.co.jp/rb/1234567890/"  # ★商品ページURLに差し替え
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    status = soup.find("span", class_="salesStatus")
    if status and "ご注文できない商品" not in status.text:
        # 在庫がある場合LINEに通知
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=f"在庫あり！ {url}")
        )

if __name__ == "__main__":
    # 本番用
    check_stock()
    # ↓テスト用（必ず通知が来る）
    line_bot_api.push_message(
        LINE_USER_ID,
        TextSendMessage(text="テスト通知です！GitHub Actions OK 🎉")
    )
