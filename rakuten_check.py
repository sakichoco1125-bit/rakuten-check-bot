import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ButtonsTemplate, URIAction

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

PRODUCTS = [
    {"name": "Nintendo Switch 2", "url": "https://books.rakuten.co.jp/rb/18210481/"},
]

STATE_FILE = "stock_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def send_line_notification(name, url):
    buttons_template = ButtonsTemplate(
        title=name,
        text="在庫があります！",
        actions=[URIAction(label="購入する", uri=url)]
    )
    template_message = TemplateSendMessage(
        alt_text=f"{name} が在庫あり！",
        template=buttons_template
    )
    line_bot_api.push_message(LINE_USER_ID, template_message)

def check_stock(product, prev_state):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(product["url"])
    driver.implicitly_wait(3)

    try:
        status_element = driver.find_element(By.CLASS_NAME, "salesStatus")
        status_text = status_element.text.strip()
    except:
        print(f"{product['name']} の在庫情報取得失敗 → 通知スキップ")
        driver.quit()
        # 安全のため「在庫なし」として保存
        prev_state[product["name"]] = True
        return

    driver.quit()

    is_out_of_stock = "ご注文できない商品" in status_text
    prev_out_of_stock = prev_state.get(product["name"], True)

    # 「在庫なし → 在庫あり」の場合のみ通知
    if prev_out_of_stock and not is_out_of_stock:
        send_line_notification(product["name"], product["url"])
        print(f"{product['name']} 在庫復活 → 通知送信")
    else:
        print(f"{product['name']} 状態変化なし")

    prev_state[product["name"]] = is_out_of_stock

if __name__ == "__main__":
    state = load_state()
    for product in PRODUCTS:
        check_stock(product, state)
    save_state(state)
