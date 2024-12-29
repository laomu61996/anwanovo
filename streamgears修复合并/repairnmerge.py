import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

# 提取主播名和日期
def extract_anchor_name_and_date(file_path):
    # 使用正则表达式匹配文件名中的主播名和日期
    match = re.search(r"/([^/]+)(\d{4}-\d{2}-\d{2})T\d{2}_\d{2}_\d{2}", file_path)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

# 修复视频文件
def fix_video(file_path, luboji_dir):
    cmd = f"bililiverecorder.Cli tool fix {file_path} {file_path} --json-indented"
    subprocess.run(cmd, shell=True, check=True)
    os.remove(file_path)  # 删除原始文件

# 合并并转换视频文件格式
def merge_and_convert(flv_files, earliest_file, source_dir):
    temp_list_file = os.path.join(source_dir, "file_list.txt")
    
    # 使用绝对路径来确保没有路径重复问题
    with open(temp_list_file, 'w') as temp_list:
        for file in flv_files:
            # 使用相对路径或绝对路径，避免出现路径重复问题
            relative_path = os.path.relpath(file, source_dir)
            temp_list.write(f"file '{relative_path}'\n")
    
    # 从最早的文件提取基本名称
    earliest_base_name = os.path.basename(earliest_file).replace(".flv", "")
    
    # 使用ffmpeg合并所有flv文件，并将结果转换为.mkv格式
    output_file = os.path.join(source_dir, f"{earliest_base_name}.mkv")
    cmd = f"ffmpeg -loglevel quiet -f concat -safe 0 -i {temp_list_file} -c:v copy -c:a copy {output_file}"
    subprocess.run(cmd, shell=True, check=True)

    # 删除原始文件和临时列表文件
    for file in flv_files:
        os.remove(file)
    os.remove(temp_list_file)

# 上传到百度网盘
def upload_to_baidu(source_dir, anchor_name):
    target_cloud_path = f"/录播/{anchor_name}"
    cmd = f"BaiduPCS upload --norapid --policy overwrite {source_dir} {target_cloud_path}"
    subprocess.run(cmd, shell=True, check=True)

# 主函数
def main():
    print("开始处理文件...")

    first_line = True
    anchor_name = None
    target_date = None
    source_dir = "./backup"
    luboji_dir = "/root/luboji"
    
    # 从标准输入读取文件路径
    file_paths = [line.strip() for line in sys.stdin]

    for file_path in file_paths:
        # 提取主播名和日期
        if first_line:
            anchor_name, target_date = extract_anchor_name_and_date(file_path)
            if not anchor_name or not target_date:
                print(f"无法从第一个文件的路径中提取主播名或日期: {file_path}")
                return
            first_line = False

        # 创建备份目录
        target_dir = os.path.join(source_dir, anchor_name, target_date)
        os.makedirs(target_dir, exist_ok=True)
        
        # 移动文件到备份目录
        shutil.move(file_path, target_dir)
        print(f"文件已移动到: {target_dir}")

    # 获取备份目录中的所有 .flv 文件
    flv_files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith(".flv")]
    num_files = len(flv_files)
    
    # 修复所有 .flv 文件
    for file in flv_files:
        fix_video(file, luboji_dir)

    # 重命名修复后的文件
    for file in os.listdir(target_dir):
        if file.endswith(".fix_p001.flv"):
            new_filename = file.replace(".fix_p001", "")
            os.rename(os.path.join(target_dir, file), os.path.join(target_dir, new_filename))

    # 如果文件数量大于或等于设定值，进行合并操作
    if num_files >= 1:
        if num_files == 1:
            # 只有一个文件，直接转换为 .mkv 格式
            single_file = flv_files[0]
            earliest_base_name = os.path.basename(single_file).replace(".flv", "")
            output_file = os.path.join(target_dir, f"{earliest_base_name}.mkv")
            cmd = f"ffmpeg -i {single_file} -c:v copy -c:a copy {output_file}"
            subprocess.run(cmd, shell=True, check=True)
            os.remove(single_file)
        else:
            # 多个文件时，合并并转换为 .mkv 格式
            earliest_file = flv_files[0]  # 假设最早的文件为列表中的第一个文件
            merge_and_convert(flv_files, earliest_file, target_dir)

    # 上传到百度网盘并删除本地备份
    upload_to_baidu(target_dir, anchor_name)
    shutil.rmtree(target_dir)
    print(f"备份已上传到百度网盘并删除本地文件夹：{target_dir}")

if __name__ == "__main__":
    main()
