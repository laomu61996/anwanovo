import re

def parse_time(time_str):
    """将时间字符串转换为毫秒"""
    h, m, s, ms = map(int, re.match(r'(\d+):(\d+):(\d+).(\d+)', time_str).groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms

def format_time(ms):
    """将毫秒转换为时间字符串"""
    h = ms // 3600000
    ms -= h * 3600000
    m = ms // 60000
    ms -= m * 60000
    s = ms // 1000
    ms -= s * 1000
    return f'{h:01d}:{m:02d}:{s:02d}.{int(ms/10):02d}'

def shift_time(line, delta_ms):
    """调整时间戳"""
    start, end = re.match(r'Dialogue: .+?,(.*?),(.*?),', line).groups()
    start_ms = parse_time(start) + delta_ms
    end_ms = parse_time(end) + delta_ms
    return line.replace(start, format_time(start_ms), 1).replace(end, format_time(end_ms), 1)

def merge_ass_files(files, output_file):
    """合并多个ASS文件"""
    try:
        delta_ms = 0
        with open(output_file, 'w', encoding='utf-8') as output:
            for i, file in enumerate(files):
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if i == 0:  # 对于第一个文件，完整写入
                    for line in lines:
                        output.write(line)
                        if line.startswith('Dialogue:'):
                            _, end_time = re.match(r'Dialogue: .+?,(.*?),(.*?),', line).groups()
                            delta_ms = max(delta_ms, parse_time(end_time))

                else:  # 对于后续文件，仅添加[Events]部分，并调整时间
                    events_started = False
                    for line in lines:
                        if line.strip() == '[Events]':
                            events_started = True
                            continue
                        if events_started and line.startswith('Dialogue:'):
                            output.write(shift_time(line, delta_ms))
                            _, end_time = re.match(r'Dialogue: .+?,(.*?),(.*?),', line).groups()
                            delta_ms = max(delta_ms, parse_time(end_time))

        print(f"合并成功，已生成文件: {output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    files_input = input("请输入要合并的ASS文件路径，使用逗号分隔: ")
    output_file = input("请输入合并后的文件路径: ")

    files = files_input.split(',')
    merge_ass_files(files, output_file)
