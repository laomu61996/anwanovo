#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import sys

# Telegram 配置
BOT_TOKEN = "xxxxxxxxxx"  # 替换为你的 Bot Token
CHAT_ID = "123456789"      # 替换为你的 Chat ID
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# 目标 URL
URL = "https://greencloudvps.com/billing/store/black-friday-2024/2222-jp-softbank"

# 请求头，模拟浏览器访问
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

# 发送 Telegram 消息
def send_telegram_message(message):
    try:
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(TELEGRAM_API, data=payload, timeout=10)
        response.raise_for_status()
        print(f"Telegram 消息已发送: {message}")
    except requests.RequestException as e:
        print(f"发送 Telegram 消息失败: {e}")

# 检查库存的函数
def check_stock():
    try:
        # 发送 GET 请求
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 检查是否有“Out of Stock”之类的内容
        page_text = soup.get_text().lower()
        if "out of stock" in page_text or "sold out" in page_text:
            return False
        else:
            # 检查是否有可购买的按钮
            buy_button = soup.find("button", {"type": "submit"}) or soup.find("input", {"type": "submit"})
            if buy_button and "add to cart" in buy_button.text.lower():
                return True
            return True  # 如果没有明确的“无货”信息，假设有货
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

# 主循环
def main():
    print("开始监控库存...")
    last_status = None  # 记录上一次的库存状态，避免重复发送消息
    
    while True:
        stock_status = check_stock()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if stock_status is None:
            print(f"[{current_time}] 网络错误，稍后重试...")
        elif stock_status and stock_status != last_status:
            message = f"[{current_time}] 有货！快去抢购！\n{URL}"
            send_telegram_message(message)
            last_status = stock_status
        elif not stock_status and stock_status != last_status:
            message = f"[{current_time}] 无货，继续监控..."
            send_telegram_message(message)
            last_status = stock_status
        else:
            print(f"[{current_time}] 状态未变: {'有货' if stock_status else '无货'}")
        
        time.sleep(10)  # 每隔60秒检查一次

if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("缺少依赖库，请先安装：pip3 install requests beautifulsoup4")
        sys.exit(1)
    
    # 检查 Telegram 配置
    if "你的Bot Token" in BOT_TOKEN or "你的Chat ID" in CHAT_ID:
        print("请先配置 BOT_TOKEN 和 CHAT_ID")
        sys.exit(1)
    
    main()
