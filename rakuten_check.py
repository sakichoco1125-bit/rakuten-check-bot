import os
import requests
from bs4 import BeautifulSoup
from time import sleep
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# ブラウザっぽくアクセスするためのヘッダー
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def check_stock(retries=3, delay=2):
    url = "https://books.rakuten.co.jp/rb/1234567890/"  # ★商品ページURLに差し替え

    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Error {res.status_code} fetching {url}")
                raise Exception("Bad status code")

            soup = BeautifulSoup(res.text, "html.parser")
            # 在庫判定（警告が出ないように string を使用）
            status = soup.find("span", class_="salesStatus")
            if status and "ご注文できない商品" not in status.string:
                # 在庫がある場合LINEに通知
                line_bot_api.push_message(
                    LINE_USER_ID,
                    TextSendMessage(text=f"在庫あり！ {url}")
                )
                print("在庫あり → 通知送信")
                return  # 通知したら終了
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

if __name__ == "__main__":
    check_stock()
