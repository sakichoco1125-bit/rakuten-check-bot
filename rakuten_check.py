import requests
from bs4 import BeautifulSoup
import os

# 環境変数から読み込む
ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")

URL = "https://books.rakuten.co.jp/rb/18210481/"

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    status = soup.select_one("span.salesStatus")
    if status and "ご注文できない商品" not in status.text:
        send_line("📚 在庫あり！楽天ブックスをチェック 👉 " + URL)
    else:
        print("在庫なし")

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    check_stock()