import os
import subprocess
import re

# 1. 获取用户输入的参数
url_or_file = input("请输入Bilibili视频的URL或包含链接的文本文件路径: ")
upload_dir = input("请输入上传到百度网盘的目录 (例如 '/课程'): ")

# 设置默认值
part = 'ALL'
use_aria2 = True
quality = '8K 超高清'
download_dir = './'

# 确保下载目录存在
if not os.path.isdir(download_dir):
    raise ValueError(f"下载目录不存在: {download_dir}")

# 生成唯一的文件夹名称 (使用固定名称)
unique_folder = os.path.join(download_dir, "BBDown_Video")
unique_folder = os.path.abspath(unique_folder)

# 确保文件夹存在
os.makedirs(unique_folder, exist_ok=True)

# 处理输入的链接或文件
urls = []
if os.path.isfile(url_or_file):
    with open(url_or_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
else:
    urls.append(url_or_file.strip())

if not urls:
    raise ValueError("未找到有效的URL")

# 2. 构建并执行BBDown下载命令
for url in urls:
    bbdown_command = [
        "BBDown",
        url,
        "-q", quality,
        "--work-dir", unique_folder,
        "-hs",
        "--upos-host", "upos-sz-mirrorcos.bilivideo.com"  # 固定选项
    ]

    # 使用默认的分P和aria2
    bbdown_command.append("-p")
    bbdown_command.append(part)

    if use_aria2:
        bbdown_command.append("-aria2")

    # 打印并执行BBDown命令
    print(f"执行下载命令: {' '.join(bbdown_command)}")

    try:
        subprocess.run(bbdown_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        exit(1)

# 3. 构建并执行BaiduPCS上传命令
BaiduPCS_command = [
    "BaiduPCS",
    "upload",
    "--norapid",
    "--policy",
    "overwrite",
    unique_folder,
    upload_dir
]

# 打印并执行BaiduPCS上传命令
print(f"执行上传命令: {' '.join(BaiduPCS_command)}")

try:
    subprocess.run(BaiduPCS_command, check=True)
except subprocess.CalledProcessError as e:
    print(f"上传失败: {e}")
    exit(1)

print(f"上传成功：{unique_folder} 到百度网盘的 {upload_dir} 文件夹")
