import json
import sys
import requests
from datetime import datetime

# 填入你的Telegram bot的token
TOKEN = '你的bot token'
# Telegram的API URL，用于发送消息
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_notification(name, start_time):
    # 将时间戳转换为更易读的格式
    readable_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    # 构造发送给Telegram的消息文本
    message = f"{name}已开播！开始时间为：{readable_time}"
    # 构建请求参数
    payload = {
        'chat_id': '你的chat id',  # 填入你的Telegram chat ID
        'text': message,
        'parse_mode': 'HTML'
    }
    # 发送POST请求到Telegram
    response = requests.post(URL, data=payload)
    if response.status_code == 200:
        print("消息成功发送到Telegram")
    else:
        print("发送消息失败", response.text)

if __name__ == "__main__":
    # 从标准输入读取JSON数据
    json_str = sys.stdin.read()
    data = json.loads(json_str)
    # 获取主播名和开播时间
    name = data.get("name", "未知主播")
    start_time = data.get("start_time", 0)  # 默认值为0，防止缺少数据导致错误
    # 发送通知
    send_notification(name, start_time)
