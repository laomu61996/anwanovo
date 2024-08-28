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

def convert_and_remove_xml(target_dir):
    # 遍历目标文件夹中的所有文件，寻找 .xml 文件
    for file_name in os.listdir(target_dir):
        if file_name.endswith(".xml"):
            xml_file_path = os.path.join(target_dir, file_name)
            ass_file_path = os.path.join(target_dir, file_name.replace(".xml", ".ass"))
            
            # 使用 DanmakuFactory CLI 转换为 .ass 文件
            cmd = ['DanmakuFactory', '-o', ass_file_path, '-i', xml_file_path, '-S', '36', '-s', '12.0']
            subprocess.run(cmd, check=True)
            print(f"已将 {xml_file_path} 转换为 {ass_file_path}")
            
            # 删除原始的 .xml 文件
            os.remove(xml_file_path)
            print(f"已删除原始的 XML 文件: {xml_file_path}")

def main():
    print("开始处理文件...")

    first_line = True
    target_date = None

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

    if target_date:
        # 转换 XML 弹幕文件为 ASS，并删除 XML 文件
        convert_and_remove_xml(target_dir)

        # 上传到百度网盘并删除本地文件
        target_cloud_path = f"/录播/{anchor_name}"
        print(f"开始上传 {target_dir} 到百度网盘目录 {target_cloud_path}...")
        cmd = ['BaiduPCS', 'upload', target_dir, target_cloud_path]
        subprocess.run(cmd, check=True)
        shutil.rmtree(target_dir)
        print(f"上传完成并已删除本地文件夹：{target_dir}")

if __name__ == "__main__":
    import sys
    main()
