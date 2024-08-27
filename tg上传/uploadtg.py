import sys
import subprocess

def main():
    # 初始化一个列表，用于保存文件路径
    file_paths = []

    # 从标准输入逐行读取文件路径
    for line in sys.stdin:
        file_path = line.strip()
        if file_path:  # 检查是否为空行
            file_paths.append(file_path)

    if not file_paths:
        print("未提供任何文件路径。")
        return

    # 构建 tdl up 命令
    tdl_command = ['tdl', 'up']
    
    # 添加文件路径
    for file_path in file_paths:
        tdl_command.extend(['-p', file_path])

    # 设置其他参数（你给出的参数）
    tdl_command.extend(['-t', '8', '-s', '524288', '-l', '4', '-c', '2096470375', '--rm'])

    # 使用 subprocess 运行 tdl 命令
    try:
        subprocess.run(tdl_command, check=True)
        print("上传完成。")
    except subprocess.CalledProcessError as e:
        print(f"上传过程中出错: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    main()
