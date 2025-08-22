import os
import requests
from bs4 import BeautifulSoup
from time import sleep

# v3 SDK
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessage, TemplateMessage, ButtonsTemplate, UriAction

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

messaging_api = MessagingApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)

# チェックしたい楽天商品
PRODUCT = {
    "name": "Nintendo Switch 2",
    "url": "https://books.rakuten.co.jp/rb/18210481/"  # 実際の商品URL
}

# ブラウザっぽくアクセスするためのヘッダー
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def check_stock(retries=3, delay=2):
    url = PRODUCT["url"]

    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Error {res.status_code} fetching {url}")
                raise Exception("Bad status code")

            soup = BeautifulSoup(res.text, "html.parser")
            status = soup.find("span", class_="salesStatus")
            if status and "ご注文できない商品" not in status.string:
                send_line_notification(PRODUCT["name"], PRODUCT["url"])
                print("在庫あり → 通知送信")
                return
            else:
                print("在庫なし → 通知しない")
                return

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                sleep(delay)
            else:
                print("取得失敗 → 通知なし")
                return

def send_line_notification(product_name, product_url):
    """LINEにボタン付き通知を送信（v3対応）"""
    buttons_template = ButtonsTemplate(
        title=product_name,
        text='在庫があります！',
        actions=[UriAction(label='購入する', uri=product_url)]
    )

    template_message = TemplateMessage(
        alt_text=f"{product_name} が在庫あり！",
        template=buttons_template
    )

    messaging_api.push_message(LINE_USER_ID, template_message)

if __name__ == "__main__":
    check_stock()
