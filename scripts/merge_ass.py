import re

def parse_time(time_str):
    """将时间字符串转换为毫秒"""
    match = re.match(r'(\d+):(\d+):(\d+).(\d+)', time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms

def format_time(ms):
    """将毫秒转换为时间字符串"""
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    ms = int(ms / 10)  # 保证毫秒精度为两位
    return f'{h:01d}:{m:02d}:{s:02d}.{ms:02d}'

def shift_time(line, delta_ms):
    """调整时间戳"""
    match = re.match(r'Dialogue: .+?,(.*?),(.*?),', line)
    if not match:
        return line
    start, end = match.groups()
    start_ms = parse_time(start) + delta_ms
    end_ms = parse_time(end) + delta_ms
    return line.replace(start, format_time(start_ms), 1).replace(end, format_time(end_ms), 1)

def get_max_end_time(lines):
    """获取文件中所有Dialogue的最大结束时间"""
    max_end_time = 0
    for line in lines:
        if line.startswith('Dialogue:'):
            match = re.match(r'Dialogue: .+?,(.*?),(.*?),', line)
            if match:
                _, end_time = match.groups()
                max_end_time = max(max_end_time, parse_time(end_time))
    return max_end_time

def merge_ass_files(files, output_file):
    """合并多个ASS文件"""
    try:
        total_delta_ms = 0  # 用于累计所有文件的时间偏移
        with open(output_file, 'w', encoding='utf-8') as output:
            for i, file in enumerate(files):
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if i == 0:  # 第一个文件完整写入
                    for line in lines:
                        output.write(line)
                    # 获取第一个文件的最大结束时间
                    total_delta_ms = get_max_end_time(lines)

                else:  # 对后续文件，跳过[Events]和Format行，并调整时间
                    events_started = False
                    for line in lines:
                        if line.strip() == '[Events]':
                            events_started = True
                            continue  # 跳过[Events]标记
                        if events_started and line.startswith('Format:'):
                            continue  # 跳过Format行
                        if events_started and line.startswith('Dialogue:'):
                            output.write(shift_time(line, total_delta_ms))  # 调整时间并写入
                        elif events_started:
                            output.write(line)

                    # 更新total_delta_ms，将当前文件的最大结束时间累加到总偏移中
                    total_delta_ms += get_max_end_time(lines)

        print(f"合并成功，已生成文件: {output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"时间格式错误: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    files_input = input("请输入要合并的ASS文件路径，使用逗号分隔: ")
    output_file = input("请输入合并后的文件路径: ")

    files = files_input.split(',')
    merge_ass_files(files, output_file)
