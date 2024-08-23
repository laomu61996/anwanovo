import os
import re
import subprocess
import time
from playwright.sync_api import sync_playwright

#playwright依赖
#sudo dnf install libxcb libX11 libXext libXrandr libXcomposite libXcursor libXdamage libXfixes libXi gtk3 pango cairo cairo-gobject gdk-pixbuf2 xorg-x11-server-Xvfb libXrender alsa-lib freetype fontconfig


# 全局变量
save_dir = ''
login_screenshot_path = ''

def open_login_page_and_screenshot(page):
    # 打开登录页面
    page.goto("https://login.dingtalk.com/oauth2/challenge.htm?client_id=dingavo6at488jbofmjs&response_type=code&scope=openid&redirect_uri=https%3A%2F%2Flv.dingtalk.com%2Fsso%2Flogin%3Fcontinue%3Dhttps%253A%252F%252Fn.dingtalk.com%252Fdingding%252Flive-room%252Findex.html%253FroomId%253DpoGdt15QapkpQ1IM%2526liveUuid%253D1b33d77a-704f-4fad-9290-64f11ee3ea7d")
    
    # 等待页面加载
    page.wait_for_load_state('networkidle')
    
    # 输出页面内容以供调试
    page_content = page.content()
    with open('page_content.html', 'w', encoding='utf-8') as file:
        file.write(page_content)
    
    # 使用 locator 定位包含特定字符串的图片并点击
    try:
        img_element = page.locator('img[src*="204-204.png"]')
        img_element.click()
        print("图片元素点击成功")
    except Exception as e:
        print(f"点击图片元素时发生错误: {e}")
    
    # 等待页面完全加载，增加额外的10秒等待时间
    time.sleep(10)
    
    # 截图登录页面
    global login_screenshot_path
    page.screenshot(path=login_screenshot_path)
    print(f"登录页面截图已保存为: {login_screenshot_path}")

    # 等待用户扫码登录
    input("请扫码登录后按Enter键继续...")

    # 截图登录后的页面
    post_login_screenshot_path = os.path.join(os.path.dirname(login_screenshot_path), 'post_login_screenshot.png')
    page.screenshot(path=post_login_screenshot_path)
    print(f"登录后页面截图已保存为: {post_login_screenshot_path}")

def download_m3u8_file(url, filename, headers, page):
    # 使用 Playwright 执行 JavaScript 获取 m3u8 内容
    m3u8_content = page.evaluate('''
        async ({url, headers}) => {
            const response = await fetch(url, { method: 'GET', headers: headers });
            return await response.text();
        }
    ''', {'url': url, 'headers': headers})
    
    # 将 m3u8 内容保存到文件
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
        "8"
    ]
    subprocess.run(command)
    print("视频下载成功完成。")

def main():
    global save_dir, login_screenshot_path

    # 输入保存下载文件的目录路径
    save_dir = input("请输入保存下载文件的目录路径: ").strip()
    
    # 输入钉钉直播链接
    dingtalk_url = input("请输入钉钉直播回放分享链接: ").strip()
    
    # 设置登录页面截图的路径
    login_screenshot_path = os.path.join(save_dir, 'login_screenshot.png')

    # 使用 Playwright 进行浏览器自动化
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        # 打开登录页面并截图
        open_login_page_and_screenshot(page)
        
        # 打开直播页面
        page.goto(dingtalk_url)

        # 增加额外的等待时间以确保所有请求都被捕获
        time.sleep(10)
        
        # 查找 m3u8 链接
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
                # 调用下载函数时使用正确的参数
                headers = {}
                m3u8_file = download_m3u8_file(link, 'output.m3u8', headers, page)
                prefix = extract_prefix(link)
                modified_m3u8_file = replace_prefix(m3u8_file, prefix)
                save_name = "live_video"

                auto_download_m3u8_with_options(modified_m3u8_file, save_name)
        else:
            print("未找到包含 'm3u8' 字符的请求链接。")

        browser.close()

if __name__ == "__main__":
    main()
