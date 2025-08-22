import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ButtonsTemplate, URIAction

# 環境変数からLINEトークンとユーザーIDを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 商品リスト
PRODUCTS = [
    {"name": "Nintendo Switch 2", "url": "https://books.rakuten.co.jp/rb/18210481/"},
    # 追加商品もここに辞書で追加可能
]

STATE_FILE = "stock_state.json"

# 前回の在庫状態をロード
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# LINE通知
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

# 在庫チェック
def check_stock(product, prev_state):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモード
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(product["url"])
    driver.implicitly_wait(3)

    try:
        status_element = driver.find_element(By.CLASS_NAME, "salesStatus")
        status_text = status_element.text.strip()
    except:
        status_text = ""

    driver.quit()

    # 「ご注文できない商品」があるかどうかで在庫判定
    is_out_of_stock = "ご注文できない商品" in status_text
    prev_out_of_stock = prev_state.get(product["name"], True)

    # 前回在庫なし → 今回在庫あり の場合のみ通知
    if prev_out_of_stock and not is_out_of_stock:
        send_line_notification(product["name"], product["url"])
        print(f"{product['name']} 在庫復活 → 通知送信")
    else:
        print(f"{product['name']} 状態変化なし")

    # 状態を更新
    prev_state[product["name"]] = is_out_of_stock

if __name__ == "__main__":
    state = load_state()
    for product in PRODUCTS:
        check_stock(product, state)
    save_state(state)
