#!/bin/bash

# 定义颜色
RED='\033[31m'
NC='\033[0m' # No Color

# 检查包管理器
if [ -f /etc/redhat-release ] && command -v dnf > /dev/null; then
    PKG_MANAGER="dnf"
elif [ -f /etc/debian_version ] && command -v apt > /dev/null; then
    PKG_MANAGER="apt"
else
    echo -e "${RED}不支持的系统或包管理器。仅支持dnf和apt。${NC}"
    exit 1
fi

# 更新系统
if [ "$PKG_MANAGER" = "dnf" ]; then
    sudo dnf update -y && sudo dnf upgrade -y
elif [ "$PKG_MANAGER" = "apt" ]; then
    sudo apt update -y && sudo apt upgrade -y
fi

# 安装常用工具（移除python3-pip）
sudo $PKG_MANAGER install -y wget curl git tar unzip || {
    echo -e "${RED}安装常用工具失败，请检查包名或网络。${NC}"
    exit 1
}

# 设置时区和编码
if ! locale -a | grep -q "en_US.utf8"; then
    sudo locale-gen en_US.UTF-8
fi
sudo timedatectl set-timezone Asia/Shanghai
sudo localectl set-locale LANG=en_US.UTF-8
sudo localectl set-locale LC_CTYPE=en_US.UTF-8

# 安装Docker
curl -fsSL https://get.docker.com | bash || {
    echo -e "${RED}Docker 安装失败，请检查网络或权限。${NC}"
    exit 1
}

# 安装UV
curl -LsSf https://astral.sh/uv/install.sh | sh || {
    echo -e "${RED}UV 安装失败。${NC}"
    exit 1
}
source ~/.cargo/env

# 安装FFmpeg，根据架构选择下载链接
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl-shared.tar.xz"
    FFMPEG_DIR="ffmpeg-master-latest-linux64-gpl"
elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl-shared.tar.xz"
    FFMPEG_DIR="ffmpeg-master-latest-linuxarm64-gpl"
else
    echo -e "${RED}不支持的系统架构：$ARCH${NC}"
    exit 1
fi

wget "$FFMPEG_URL" || { echo -e "${RED}FFmpeg 下载失败。${NC}"; exit 1; }
tar -xf "${FFMPEG_DIR}.tar.xz" || { echo -e "${RED}FFmpeg 解压失败。${NC}"; exit 1; }
mv "$FFMPEG_DIR" /root/ffmpeg
rm "${FFMPEG_DIR}.tar.xz"
echo 'export PATH=/root/ffmpeg/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH="/root/ffmpeg/lib:$LD_LIBRARY_PATH"' >> ~/.bashrc
export PATH=/root/ffmpeg/bin:$PATH
export LD_LIBRARY_PATH="/root/ffmpeg/lib:$LD_LIBRARY_PATH"

# 安装biliup
uv tool install biliup || { echo -e "${RED}biliup 安装失败。${NC}"; exit 1; }

# 安装nvm和nodejs
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash || {
    echo -e "${RED}nvm 安装失败。${NC}"
    exit 1
}
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts

# 网络优化
if lsmod | grep -q tcp_bbr; then
    echo "net.core.default_qdisc=fq" | sudo tee -a /etc/sysctl.conf
    echo "net.ipv4.tcp_congestion_control=bbr" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
else
    echo -e "${RED}当前内核不支持 BBR，跳过设置。${NC}"
fi
echo "precedence ::ffff:0:0/96  100" | sudo tee -a /etc/gai.conf

echo -e "${RED}脚本执行完成！${NC}"
