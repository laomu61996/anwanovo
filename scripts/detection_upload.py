import os
import time
import subprocess
from datetime import datetime

def check_and_upload():
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 遍历 /backup 下的每个子目录
    for subdir in os.listdir("/mnt/hdd/DanmakuRender/backup"):
        subdir_path = os.path.join("/mnt/hdd/DanmakuRender/backup", subdir)
        if os.path.isdir(subdir_path):
            # 检查子目录下是否有文件
            files = os.listdir(subdir_path)
            if files:
                print(f"检测到 {subdir} 文件夹下有文件，开始上传...")

                # 构造 rclone 的目标路径
                rclone_target = f"myod:lubo/{subdir}/{current_date}"

                # 对每个文件单独进行上传
                for file in files:
                    file_path = os.path.join(subdir_path, file)
                    if os.path.isfile(file_path):
                        # 使用 rclone 复制文件
                        result = subprocess.run(["rclone", "copy", file_path, rclone_target])
                        if result.returncode == 0:
                            os.remove(file_path)
                            print(f"文件 {file} 上传成功并已删除。")
                        else:
                            print(f"文件 {file} 上传失败。")
            else:
                print(f"{subdir} 文件夹下没有检测到文件，不执行操作。")

def main():
    while True:
        check_and_upload()
        time.sleep(300)  # 等待 5 分钟

if __name__ == "__main__":
    main()
