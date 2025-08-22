import os
import requests
from bs4 import BeautifulSoup
from time import sleep
import json
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ButtonsTemplate, URIAction

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

PRODUCT = {
    "name": "Nintendo Switch 2",
    "url": "https://books.rakuten.co.jp/rb/18210481/"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
STATE_FILE = "stock_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def check_stock(retries=3, delay=2):
    url = PRODUCT["url"]
    state = load_state()
    product_name = PRODUCT["name"]

    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                raise Exception(f"Error {res.status_code}")

            soup = BeautifulSoup(res.text, "html.parser")
            status = soup.find("span", class_="salesStatus")
            is_out_of_stock = status and "ご注文できない商品" in status.text

            # 前回の状態
            prev_out_of_stock = state.get(product_name, True)  # デフォルトは True（在庫なし）

            # 「ご注文できない商品」が消えたら通知
            if prev_out_of_stock and not is_out_of_stock:
                send_line_notification(product_name, url)
                print(f"{product_name} 在庫復活 → 通知送信")
            else:
                print(f"{product_name} 状態変化なし")

            # 状態を保存（在庫なしかどうか）
            state[product_name] = is_out_of_stock
            save_state(state)
            return

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                sleep(delay)
            else:
                print("取得失敗 → 通知なし")
                return

def send_line_notification(product_name, product_url):
    buttons_template = ButtonsTemplate(
        title=product_name,
        text="在庫があります！",
        actions=[URIAction(label="購入する", uri=product_url)]
    )
    template_message = TemplateSendMessage(
        alt_text=f"{product_name} が在庫あり！",
        template=buttons_template
    )
    line_bot_api.push_message(LINE_USER_ID, template_message)

if __name__ == "__main__":
    check_stock()
