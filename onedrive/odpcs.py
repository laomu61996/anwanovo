import os
import re
import shutil
import subprocess
from datetime import datetime

def extract_anchor_name_and_date(file_path):
    # 使用正则表达式匹配文件名中的主播名和日期
    match = re.search(r"/([^/]+)(\d{4}-\d{2}-\d{2})T\d{2}_\d{2}_\d{2}", file_path)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

def main():
    print("开始处理文件...")

    first_line = True
    target_date = None
    anchor_name = None

    for line in sys.stdin:
        file_path = line.strip()
        
        if first_line:
            anchor_name, target_date = extract_anchor_name_and_date(file_path)
            if not anchor_name or not target_date:
                print(f"无法从第一个文件的路径中提取主播名或日期: {file_path}")
                return
            first_line = False

        if not first_line:
            target_dir = os.path.join("./backup", anchor_name, target_date)
            os.makedirs(target_dir, exist_ok=True)
            
            # 移动文件
            shutil.move(file_path, target_dir)
            print(f"文件已移动到: {target_dir}")

    if target_date and anchor_name:
        # 使用rclone copy上传到云端并删除本地文件
        target_cloudod_path = f"myod:/录播/{anchor_name}/{target_date}"
        target_cloudpcs_path = f"/录播/{anchor_name}"
        print(f"开始使用 rclone 上传 {target_dir} 到云端目录 {target_cloudod_path}...")
        cmd = ['rclone', 'copy', target_dir, target_cloudod_path]
        subprocess.run(cmd, check=True)
        print(f"开始使用 BaiduPCS 上传 {target_dir} 到云端目录 {target_cloudpcs_path}...")
        cmd = ['BaiduPCS', 'upload', target_dir, target_cloudpcs_path]
        subprocess.run(cmd, check=True)
        shutil.rmtree(target_dir)
        print(f"上传完成并已删除本地文件夹：{target_dir}")

if __name__ == "__main__":
    import sys
    main()
