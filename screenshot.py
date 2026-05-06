import os
import sys
from playwright.sync_api import sync_playwright

html_path = os.path.abspath('viewer.html').replace('\\', '/')
file_url = 'file:///' + html_path

print(f"正在访问: {file_url}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 800})

    # 注入示例数据并渲染
    page.goto(file_url)
    page.wait_for_load_state('networkidle')

    # 注入样例JSON数据
    sample_data = '''{
        "jData": {
            "user": {
                "charac_name": "Sample%E7%8E%A9%E5%AE%B6",
                "head_url": "",
                "credit_value": 100,
                "ranking_star": 85,
                "mmr_value": 1523,
                "grade_level": "星耀"
            },
            "history": [
                {
                    "GameResult": "1",
                    "GameTypeName": "5V5%E6%8E%92%E4%BD%8D%E8%B5%9B",
                    "HeroID": "186",
                    "UsedTime": 1245,
                    "KillCnt": "8",
                    "DeadCnt": "2",
                    "AssistCnt": "12",
                    "dtEventTime": "2026-05-06 20:30:00",
                    "KDA": "10.0",
                    "TotalHurtHeroCnt": "125430",
                    "TotalInBattleCoin": "13200",
                    "AcntName1": "TestPlayer1",
                    "AcntName2": "TestPlayer2",
                    "AcntName3": "TestPlayer3",
                    "ScoreOfRank": "28",
                    "MvpCnt": "1",
                    "DestoryTowerCnt": "3",
                    "KillMonsterCnt": "24",
                    "GameType": "5",
                    "MapType": "1",
                    "AcntCamp": "1",
                    "WinCamp": "1"
                },
                {
                    "GameResult": "2",
                    "GameTypeName": "5V5%E6%8E%92%E4%BD%8D%E8%B5%9B",
                    "HeroID": "112",
                    "UsedTime": 987,
                    "KillCnt": "4",
                    "DeadCnt": "5",
                    "AssistCnt": "7",
                    "dtEventTime": "2026-05-06 19:10:00",
                    "KDA": "2.2",
                    "TotalHurtHeroCnt": "87320",
                    "TotalInBattleCoin": "10800",
                    "AcntName1": "TestPlayer1",
                    "AcntName2": "TestPlayer2",
                    "ScoreOfRank": "-18",
                    "MvpCnt": "0",
                    "DestoryTowerCnt": "1",
                    "KillMonsterCnt": "15",
                    "GameType": "5",
                    "MapType": "1",
                    "AcntCamp": "2",
                    "WinCamp": "1"
                }
            ]
        }
    }'''

    page.evaluate(f"""
        document.getElementById('jsonInput').value = JSON.stringify({sample_data});
        handleDataParse();
    """)

    page.wait_for_timeout(1500)

    # 截取完整页面
    page.screenshot(path='screenshot_full.png', full_page=True)
    print("全页截图完成: screenshot_full.png")

    # 截取头部区域（玩家信息+第一条战绩）
    page.screenshot(path='screenshot_preview.png', clip={"x": 0, "y": 0, "width": 1200, "height": 700})
    print("预览截图完成: screenshot_preview.png")

    browser.close()

print("截图任务完成！")
