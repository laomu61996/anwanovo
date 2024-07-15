import os
import time
import logging

# 配置日志为中文输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_and_delete_files():
    directories = ["/mnt/hdd/DanmakuRender", "/mnt/hdd/DMR"]  # 要检查的目录列表
    cutoff_time = 12 * 3600  # 12小时的秒数
    files_deleted = 0  # 记录删除的文件数量

    for root_dir in directories:
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith(('.mp4', '.ass', '.flv')):
                    file_path = os.path.join(subdir, file)
                    try:
                        creation_time = os.path.getctime(file_path)
                        if time.time() - creation_time > cutoff_time:
                            os.remove(file_path)
                            files_deleted += 1
                            logging.info(f"已删除文件：{file_path}")
                    except Exception as e:
                        logging.error(f"删除文件失败：{file_path}, 错误：{str(e)}")

    if files_deleted == 0:
        logging.info("没有找到需要删除的文件。")

# 运行文件检查
check_and_delete_files()
