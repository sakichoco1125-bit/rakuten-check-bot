import requests
from bs4 import BeautifulSoup
from time import sleep
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ButtonsTemplate, URIAction

# LINE設定
LINE_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'  # ここに自分のトークン
USER_ID = 'YOUR_USER_ID'                   # ここに自分のLINEユーザーID
line_bot_api = LineBotApi(LINE_TOKEN)

# チェックしたい楽天商品リスト
products = [
    {
        "name": "Nintendo Switch 2",
        "url": "https://books.rakuten.co.jp/rb/18210481/"
    }
]

def check_stock(product_url, retries=3, delay=2):
    """
    楽天商品ページを確認して在庫ありならTrue
    - retries: エラー時の再試行回数
    - delay: 再試行時の待機秒数
    """
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(product_url, timeout=5)
            if response.status_code != 200:
                print(f"Error {response.status_code} fetching {product_url}")
                raise Exception("Bad status code")

            soup = BeautifulSoup(response.text, 'html.parser')
            # ページ内の「在庫あり」文字を検索（楽天ページによって調整必要）
            if soup.find(text="在庫あり"):
                return True
            else:
                return False

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                sleep(delay)
            else:
                return False

def send_line_notification(product_name, product_url):
    """LINEにボタン付き通知を送信"""
    buttons_template = ButtonsTemplate(
        title=product_name,
        text='在庫があります！',
        actions=[URIAction(label='購入する', uri=product_url)]
    )

    template_message = TemplateSendMessage(
        alt_text=f"{product_name} が在庫あり！",
        template=buttons_template
    )

    line_bot_api.push_message(USER_ID, template_message)

# メイン処理
for product in products:
    if check_stock(product['url']):
        send_line_notification(product['name'], product['url'])
        print(f"{product['name']} は在庫あり！通知送信完了。")
    else:
        print(f"{product['name']} は在庫なし、または取得失敗。")
