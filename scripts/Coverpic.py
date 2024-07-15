import os
from PIL import Image, ImageDraw, ImageFont   #pip install Pillow==9.5.0
from datetime import datetime

# 设置源目录和目标目录
source_directory = "/mnt/hdd/DanmakuRender/cover1"
target_directory = "/mnt/hdd/DanmakuRender/cover"

# 确保目标目录存在
os.makedirs(target_directory, exist_ok=True)

# 获取当前日期
current_date = datetime.now().strftime("%Y-%m-%d")

# 设置字体和字体大小
font_path = "/usr/local/share/fonts/HarmonyOS Sans/HarmonyOS Sans SC Bold.ttf"
font_size = 70
font = ImageFont.truetype(font_path, font_size)

# 描边偏移量
stroke_width = 3

for filename in os.listdir(source_directory):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        source_file_path = os.path.join(source_directory, filename)
        target_file_path = os.path.join(target_directory, filename)

        # 打开并编辑图片
        with Image.open(source_file_path) as img:
            draw = ImageDraw.Draw(img)

            # 获取文本尺寸
            text_width, text_height = draw.textsize(current_date, font=font)

            # 定义文本位置（图片右下区域居中）
            text_x = img.width - text_width - 90  # 留出一些边距
            text_y = img.height - text_height - 200  # 留出一些边距

            # 绘制带描边的文本
            # 首先绘制描边（较大的白色文字）
            for x_offset in range(-stroke_width, stroke_width+1):
                for y_offset in range(-stroke_width, stroke_width+1):
                    draw.text((text_x + x_offset, text_y + y_offset), current_date, font=font, fill="yellow")

            # 在上面绘制红色文字
            draw.text((text_x, text_y), current_date, font=font, fill="red")

            # 保存到目标目录，覆盖同名文件
            img.save(target_file_path)

print("所有图片已处理并保存到目标目录。")
