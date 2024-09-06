import os
import re
import subprocess
import shutil
from datetime import datetime

# 提取主播名和日期
def extract_anchor_name_and_date(file_path):
    match = re.search(r"/([^/]+)(\d{4}-\d{2}-\d{2})T\d{2}_\d{2}_\d{2}", file_path)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

# 转换 .xml 文件为 .ass
def convert_xml_to_ass(target_dir):
    for file_name in os.listdir(target_dir):
        if file_name.endswith(".xml"):
            xml_file_path = os.path.join(target_dir, file_name)
            ass_file_path = xml_file_path.replace(".xml", ".ass")

            # 调用 DanmakuFactory 转换 xml 为 ass
            cmd = ['DanmakuFactory', '-o', ass_file_path, '-i', xml_file_path, '-S', '45', '-s', '12.0', '--displayarea', '0.4', '-N', 'HarmonyOS Sans SC Bold']
            subprocess.run(cmd, check=True)
            print(f"{xml_file_path} 已转换为 {ass_file_path}")

# 压制带弹幕的视频
def process_video_and_barrage(target_dir):
    # 遍历目标文件夹中的所有文件，寻找 .mp4 和相同文件名的 .ass 文件
    for file_name in os.listdir(target_dir):
        if file_name.endswith(".mp4"):
            video_file_path = os.path.join(target_dir, file_name)
            ass_file_path = os.path.join(target_dir, file_name.replace(".mp4", ".ass"))

            # 检查是否有与 .mp4 文件同名的 .ass 文件
            if os.path.exists(ass_file_path):
                output_file_path = video_file_path.replace(".mp4", "_带弹幕版.mp4")
                # 使用 ffmpeg 压制带有相同文件名的弹幕
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
                print(f"已将 {ass_file_path} 的弹幕压制到 {output_file_path}")
            else:
                print(f"没有找到对应的 .ass 文件用于 {video_file_path}")

# 主处理逻辑
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

    if target_date:
        # 第四步：转换所有 xml 弹幕文件为 ass 文件
        convert_xml_to_ass(target_dir)

        # 第五步：处理视频和弹幕，压制新的视频文件
        process_video_and_barrage(target_dir)

        # 第六步：上传到Onedrive并删除本地文件
        target_cloud_path = f"myod:/lubo/{anchor_name}/{target_date}"
        print(f"开始上传 {target_dir} 到Onedrive目录 {target_cloud_path}...")
        cmd = ['rclone', 'copy', target_dir, target_cloud_path]
        subprocess.run(cmd, check=True)
        shutil.rmtree(target_dir)
        print(f"上传完成并已删除本地文件夹：{target_dir}")

if __name__ == "__main__":
    import sys
    main()
