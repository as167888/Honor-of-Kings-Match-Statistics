import os
import sys
import json
import time
from playwright.sync_api import sync_playwright
import datetime

def get_exe_dir():
    """获取 exe 所在的外部目录，用于保存输出的 JSON 文件"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """获取内嵌在 exe 中的 viewer.html 路径"""
    if getattr(sys, 'frozen', False):
        # 打包成 exe 后，文件会被解压到 sys._MEIPASS 临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def main():
    exe_dir = get_exe_dir()
    viewer_path = get_resource_path("viewer.html")
    
    if not os.path.exists(viewer_path):
        print("❌ 未找到 viewer.html 界面文件，程序终止！")
        input("按回车键退出...")
        return

    with sync_playwright() as p:
        print("🚀 正在启动系统自带浏览器...")
        
        # 【关键修改】优先调用系统自带的 Edge，如果失败再尝试 Chrome
        try:
            browser = p.chromium.launch(headless=False, channel="msedge", args=['--start-maximized'])
        except Exception:
            try:
                browser = p.chromium.launch(headless=False, channel="chrome", args=['--start-maximized'])
            except Exception:
                print("❌ 启动失败：您的电脑似乎没有安装 Edge 或 Chrome 浏览器。")
                input("按回车键退出...")
                return

        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("🌐 正在打开王者荣耀历史战绩页面...")
        page.goto("https://pvp.qq.com/web201605/hisrecord.shtml")

        print("\n" + "="*50)
        print("👉 请在弹出的浏览器中完成以下操作：")
        print("1. 微信/QQ扫码登录")
        print("2. 选择你要查询的游戏大区和角色")
        print("="*50 + "\n")
        input("✅ 登录并选择好角色后，请在此黑框控制台中按下【回车键】继续...")

        captured_data = None

        def handle_response(response):
            nonlocal captured_data
            if response.request.resource_type in ["fetch", "xhr", "script"]:
                try:
                    text = response.text()
                    if "AcntName2" in text and not captured_data:
                        print(f"🎯 成功捕获目标战绩数据包！")
                        captured_data = text
                except Exception:
                    pass

        page.on("response", handle_response)

        print("🔄 正在刷新网页以触发战绩数据请求...")
        page.reload()

        print("⏳ 等待数据包返回中...")
        timeout = 15
        start_time = time.time()
        while not captured_data:
            page.wait_for_timeout(500)
            if time.time() - start_time > timeout:
                print("❌ 抓包超时！未检测到完整战绩数据。")
                break

        if captured_data:
            # 生成日期前缀
            date_prefix = datetime.date.today().isoformat()
            # 将 JSON 保存到与 exe 同级的目录
            json_file_path = os.path.join(exe_dir, f"{date_prefix}_history.json")
            try:
                parsed_json = json.loads(captured_data)
                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                with open(json_file_path, "w", encoding="utf-8") as f:
                    f.write(captured_data)
            
            print(f"💾 原始数据已备份至: {json_file_path}")

            local_url = f"file:///{viewer_path.replace(os.sep, '/')}"
            print("📈 正在打开全景战绩看板...")
            page.goto(local_url)

            print("⚙️ 正在自动渲染视图...")
            page.wait_for_selector("#jsonInput")
            page.fill("#jsonInput", captured_data)
            page.click(".btn-parse")
            
            print("🎉 解析完成！请在浏览器中查看您的战绩。")
        else:
            print("⚠️ 未获取到目标数据，请确保选对了大区并有战绩。")

        print("\n🚪 在浏览器中看完后，在此控制台按下【回车键】即可关闭程序并退出...")
        input()
        browser.close()

if __name__ == "__main__":
    main()