#!/bin/bash

# 检查包管理器
if command -v dnf > /dev/null; then
    PKG_MANAGER="dnf"
elif command -v apt > /dev/null; then
    PKG_MANAGER="apt"
else
    echo "无法识别的包管理器。脚本仅支持dnf和apt。"
    exit 1
fi

# 更新系统
sudo $PKG_MANAGER update -y && sudo $PKG_MANAGER upgrade -y

# 安装常用工具
sudo $PKG_MANAGER install -y wget curl git python3-pip tar unzip

# 安装Docker
curl -fsSL https://get.docker.com | bash

# 安装Nexttrace
curl -fsSL nxtrace.org/nt | bash

# 安装Rclone
curl https://rclone.org/install.sh | sudo bash

# 安装Aliyunpan CLI
ALIYUNPAN_VERSION="v0.3.3"
wget https://github.com/tickstep/aliyunpan/releases/download/$ALIYUNPAN_VERSION/aliyunpan-$ALIYUNPAN_VERSION-linux-amd64.zip
unzip aliyunpan-$ALIYUNPAN_VERSION-linux-amd64.zip
sudo mv aliyunpan-$ALIYUNPAN_VERSION-linux-amd64/aliyunpan /usr/local/bin/
sudo chmod 777 /usr/local/bin/aliyunpan
rm -rf aliyunpan-$ALIYUNPAN_VERSION-linux-amd64 aliyunpan-$ALIYUNPAN_VERSION-linux-amd64.zip

# 安装FFmpeg
FFMPEG_URL="https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
wget $FFMPEG_URL
tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz
mv ffmpeg-master-latest-linux64-gpl ffmpeg
rm ffmpeg-master-latest-linux64-gpl.tar.xz

# 更新系统环境变量
echo 'export PATH=$PWD/ffmpeg/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# 使用pip安装biliup和quickjs
pip install biliup quickjs --break-system-packages

# 改用BBR
echo "net.core.default_qdisc=fq" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 设置IPv4网络优先
echo "precedence ::ffff:0:0/96  100" | sudo tee -a /etc/gai.conf

# 设置时区为Asia/Shanghai
sudo timedatectl set-timezone Asia/Shanghai

# 设置系统编码为UTF-8
sudo localectl set-locale LANG=en_US.UTF-8
sudo localectl set-locale LC_CTYPE=en_US.UTF-8
