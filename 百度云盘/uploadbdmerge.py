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
            
            # 使用 DanmakuFactory CLI 转换为 .ass 文件，设置字体大小和滚动速度
            cmd = ['DanmakuFactory', '-o', ass_file_path, '-i', xml_file_path, '-S', '42', '-s', '12.0', '-N', 'HarmonyOS Sans SC Bold']
            subprocess.run(cmd, check=True)
            print(f"已将 {xml_file_path} 转换为 {ass_file_path}")
            
            # 删除原始的 .xml 文件
            os.remove(xml_file_path)
            print(f"已删除原始的 XML 文件: {xml_file_path}")

def process_video_and_barrage(video_file_path, ass_file_path, output_file_path):
    # 使用 ffmpeg 压制弹幕
    cmd = [
        'ffmpeg',
        '-y',  # 覆盖输出文件
        '-fflags', '+discardcorrupt',  # 忽略损坏的数据
        '-i', video_file_path,  # 输入视频文件
        '-filter_complex', f'subtitles=filename={ass_file_path}',  # 添加字幕（弹幕）
        '-c:v', 'h264_qsv',  # 使用 QSV 编码器
        '-profile:v', 'high',  # 设置编码器配置
        '-global_quality:v', '21',  # 设置质量
        '-look_ahead', '0',  # 设置编码器预测
        '-g', '600',  # 设置关键帧间隔
        '-low_power', 'False',  # 设置编码器低功耗模式
        '-preset', 'medium',  # 设置编码器预设
        '-scenario', 'archive',  # 设置编码器场景
        '-c:a', 'aac',  # 使用 AAC 音频编码器
        '-b:a', '320K',  # 设置音频比特率
        output_file_path  # 输出视频文件
    ]
    subprocess.run(cmd, check=True)
    print(f"已将弹幕压制到视频中: {output_file_path}")

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
        
        # 遍历目标文件夹中的所有文件，处理视频和弹幕
        video_file_path = None
        ass_file_path = None
        
        for file_name in os.listdir(target_dir):
            if file_name.endswith(".mp4"):  # 假设视频文件为 mp4 格式
                video_file_path = os.path.join(target_dir, file_name)
            elif file_name.endswith(".ass"):
                ass_file_path = os.path.join(target_dir, file_name)
        
        if video_file_path and ass_file_path:
            output_file_path = video_file_path.replace(".mp4", "_带弹幕版.mp4")
            process_video_and_barrage(video_file_path, ass_file_path, output_file_path)

            # 上传到百度网盘并删除本地文件
            target_cloud_path = f"/录播/{anchor_name}"
            print(f"开始上传 {output_file_path} 到百度网盘目录 {target_cloud_path}...")
            cmd = ['BaiduPCS', 'upload', output_file_path, target_cloud_path]
            subprocess.run(cmd, check=True)
            os.remove(output_file_path)
            shutil.rmtree(target_dir)
            print(f"上传完成并已删除本地文件夹：{target_dir}")
        else:
            print("找不到视频文件或弹幕文件，无法完成压制和上传过程。")

if __name__ == "__main__":
    import sys
    main()
