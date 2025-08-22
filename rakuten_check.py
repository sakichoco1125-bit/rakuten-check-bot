import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from linebot import LineBotApi
from linebot.models import TextSendMessage

# ===== LINE設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# ===== 監視する商品リスト =====
products = [
    {
        "name": "Nintendo Switch 2",
        "url": "https://books.rakuten.co.jp/rb/18210481/"
    }
]

# ===== 状態を保存するファイル =====
STATE_FILE = "stock_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def check_stock(product, prev_state):
    options = Options()
    options.add_argument("--headless=new")  # headless モード
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(product["url"])

        # ページ全体の読み込み完了を待機
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page_text = driver.page_source
    except Exception as e:
        print(f"{product['name']} の在庫情報取得失敗 ({e}) → 通知スキップ")
        driver.quit()
        prev_state[product["name"]] = True
        return prev_state

    driver.quit()

    # 「ご注文できない商品」がページにあるかどうか
    is_out_of_stock = "ご注文できない商品" in page_text

    # 前回は在庫なし、今回在庫あり → 通知
    if prev_state.get(product["name"], True) and not is_out_of_stock:
        message = f"{product['name']} 在庫復活！\n{product['url']}"
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
        print(message)
        prev_state[product["name"]] = False
    else:
        print(f"{product['name']} 在庫なし → 通知スキップ")
        prev_state[product["name"]] = is_out_of_stock

    return prev_state

if __name__ == "__main__":
    state = load_state()
    for product in products:
        state = check_stock(product, state)
    save_state(state)
