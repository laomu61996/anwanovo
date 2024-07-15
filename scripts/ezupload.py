import subprocess

def upload_videos(biliup_path, line, limit, title, tid, files):
    # 拼接命令
    command = [biliup_path, 'upload']
    
    if line:
        command.extend(['--line', line])
    
    if limit:
        command.extend(['--limit', str(limit)])
    
    if title:
        command.extend(['--title', f'"{title}"'])
    
    if tid:
        command.extend(['--tid', str(tid)])
    
    command.extend(files)  # 添加文件路径列表

    # 打印命令以供调试
    print('Running command:', ' '.join(command))
    
    # 调用biliup命令
    result = subprocess.run(command, capture_output=True, text=True)
    
    # 打印输出和错误信息
    print('Output:', result.stdout)
    print('Error:', result.stderr)

if __name__ == "__main__":
    # 获取用户输入
    biliup_path = input("请输入 biliup 二进制文件的路径: ")
    line = input("请输入上传线路 (--line): ")
    limit = input("请输入单视频文件最大并发数 (--limit): ")
    title = input("请输入视频标题 (--title): ")
    tid = input("请输入投稿分区 (--tid): ")
    files = input("请输入文件路径（多个文件用空格分隔）: ").split()

    # 调用上传函数
    upload_videos(biliup_path, line, limit, title, tid, files)
