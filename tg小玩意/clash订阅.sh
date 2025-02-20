#!/bin/bash

# 配置项
CADDYFILE_PATH="/etc/caddy/Caddyfile"   # Caddyfile 路径
TELEGRAM_API_TOKEN="xxxxxxxxxxxxxx"  # 你的 Telegram 机器人 API Token
TELEGRAM_CHAT_IDS=("123456789" "987654321")  # 仅私人聊天的 Telegram Chat IDs
GROUP_CHAT_IDS=("-123456789")  # 需要置顶的群组 Chat IDs（示例，替换为实际 ID）
CADDY_SERVICE="caddy"                   # Caddy 服务名称

# 生成 URL 安全的 token
new_token=$(openssl rand -base64 32 | tr -d '=/+')

# 生成新的 URL，包含 token 查询参数
new_url="https://xxxx.uord.de/clash.yaml?token=${new_token}"

# 更新 Caddyfile 中的 token，使用 "#" 作为分隔符
sed -i "s/token=[^&]*\$/token=${new_token}/" "$CADDYFILE_PATH"
if [ $? -ne 0 ]; then
  echo "更新 Caddyfile 中的 token 失败。"
  exit 1
fi

# 重新加载 Caddy 配置
systemctl reload "$CADDY_SERVICE"
if [ $? -ne 0 ]; then
  echo "重新加载 Caddy 配置失败。"
  exit 1
fi

# 定义一个发送消息的函数，方便复用
send_message() {
  local chat_id=$1
  response=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_API_TOKEN}/sendMessage" \
    -d "chat_id=${chat_id}" \
    -d "text=新的clash订阅来咯: ${new_url}")
  
  if [[ $response != *"ok"* ]]; then
    echo "发送消息到 Telegram 失败，chat_id=${chat_id}，响应：$response"
    return 1
  fi
  echo "$response"  # 返回响应内容，以便提取 message_id
  return 0
}

# 发送消息给所有私人聊天 ID
for chat_id in "${TELEGRAM_CHAT_IDS[@]}"; do
  send_message "$chat_id"
done

# 发送消息给所有群组并置顶
for group_chat_id in "${GROUP_CHAT_IDS[@]}"; do
  response=$(send_message "$group_chat_id")
  if [ $? -eq 0 ]; then
    # 从响应中提取 message_id
    message_id=$(echo "$response" | grep -o '"message_id":[0-9]*' | cut -d':' -f2)

    if [ -n "$message_id" ]; then
      pin_response=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_API_TOKEN}/pinChatMessage" \
        -d "chat_id=${group_chat_id}" \
        -d "message_id=${message_id}" \
        -d "disable_notification=true")
  
      if [[ $pin_response != *"ok"* ]]; then
        echo "置顶消息失败，chat_id=${group_chat_id}，message_id=${message_id}，响应：$pin_response"
      else
        echo "消息已成功置顶，chat_id=${group_chat_id}，message_id=${message_id}"
      fi
    else
      echo "无法获取 message_id，chat_id=${group_chat_id}"
    fi
  fi
done

# 输出新的 URL 到终端（可选）
echo "New token generated: ${new_url}"
