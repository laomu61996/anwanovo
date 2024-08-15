import os
import re
import subprocess
import sys
from playwright.sync_api import sync_playwright
import time

# 全局变量
browser = None
save_dir = ''
login_screenshot_path = ''

# 打开登录页面并截图
def open_login_page_and_screenshot(page):
    page.goto("https://login.dingtalk.com/oauth2/challenge.htm?redirect_uri=https%3A%2F%2Foa.dingtalk.com%2Fomp%2Flogin%2Fdingtalk_sso_call_back%3Fcontinue%3Dhttps%253A%252F%252Foa.dingtalk.com%252Findex.htm&response_type=code&client_id=dingoaltcsv4vlgoefhpec&scope=openid+corpid&org_type=management#/login")
    img_element = page.query_selector('img[src*="204-204.png"]')
    if img_element:
        img_element.click()
        print("图片元素点击成功")
    else:
        print("未找到图片元素")
    time.sleep(10)
    global login_screenshot_path
    page.screenshot(path=login_screenshot_path)
    print(f"登录页面截图已保存为: {login_screenshot_path}")
    input("请扫码登录后按Enter键继续...")
    post_login_screenshot_path = os.path.join(os.path.dirname(login_screenshot_path), 'post_login_screenshot.png')
    page.screenshot(path=post_login_screenshot_path)
    print(f"登录后页面截图已保存为: {post_login_screenshot_path}")

def download_m3u8_file(url, filename, headers, page):
    m3u8_content = page.evaluate('''async ({url, headers}) => {
            const response = await fetch(url, { method: 'GET', headers: headers });
            return await response.text();
        }''', {'url': url, 'headers': headers})
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    return filename

def extract_prefix(url):
    pattern = re.compile(r'(https?://[^/]+/live_hp/[0-9a-f-]+)')
    match = pattern.search(url)
    return match.group(1) if match else url

def replace_prefix(m3u8_file, prefix):
    updated_lines = []
    with open(m3u8_file, 'r') as file:
        for line in file:
            index = line.find('/')
            if index != -1:
                updated_line = prefix + line[index:]
            else:
                updated_line = line
            updated_lines.append(updated_line)
    output_file = os.path.join(os.path.dirname(m3u8_file), 'modified_' + os.path.basename(m3u8_file))
    with open(output_file, 'w') as file:
        file.writelines(updated_lines)
    return output_file

def auto_download_m3u8_with_options(m3u8_file, save_name):
    command = [
        "N_m3u8DL-RE",
        m3u8_file,
        "--del-after-done",
        "--save-name",
        save_name,
        "--save-dir",
        save_dir,
        "--thread-count",
        "16"
    ]
    subprocess.run(command)
    print("视频下载成功完成。")

    # 检查并处理重命名
    final_save_path = os.path.join(save_dir, save_name + ".mp4")
    if not os.path.exists(final_save_path):
        base_name = save_name
        counter = 1
        while not os.path.exists(final_save_path):
            save_name = f"{base_name}_{counter}"
            final_save_path = os.path.join(save_dir, save_name + ".mp4")
            counter += 1

    return final_save_path

def upload_to_aliyun(file_path):
    upload = input("下载完成，是否上传到阿里云盘？(yes/no): ").strip().lower()
    if upload == 'yes':
        aliyun_dir = input("请输入阿里云盘的目标目录: ").strip()
        upload_command = f"aliyunpan upload {file_path} {aliyun_dir}"
        subprocess.run(upload_command, shell=True)
        print("文件已成功上传到阿里云盘。")
    else:
        print("已跳过上传。")

def main():
    global save_dir, login_screenshot_path
    save_dir = input("请输入保存下载文件的目录路径: ").strip()
    
    while True:
        dingtalk_url = input("请输入钉钉直播回放分享链接，或输入 'q' 退出程序: ").strip()
        if dingtalk_url.lower() == 'q':
            print("程序已退出。")
            break

        login_screenshot_path = os.path.join(save_dir, 'login_screenshot.png')

        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            open_login_page_and_screenshot(page)
            page.goto(dingtalk_url)
            time.sleep(15)

            m3u8_links = page.evaluate('''
                () => {
                    let links = [];
                    let requests = performance.getEntriesByType('resource');
                    for (let request of requests) {
                        if (request.name.includes("m3u8")) {
                            links.push(request.name);
                        }
                    }
                    return links;
                }
            ''')

            if m3u8_links:
                for link in m3u8_links:
                    m3u8_file = download_m3u8_file(link, 'output.m3u8', {}, page)
                    prefix = extract_prefix(link)
                    modified_m3u8_file = replace_prefix(m3u8_file, prefix)
                    save_name = "live_video"
                    final_save_path = auto_download_m3u8_with_options(modified_m3u8_file, save_name)
                    upload_to_aliyun(final_save_path)
            else:
                print("未找到包含 'm3u8' 字符的请求链接。")

            browser.close()

if __name__ == "__main__":
    main()
