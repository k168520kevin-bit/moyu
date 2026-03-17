import os
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from supabase import create_client

# 初始化 Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_specific_stories():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("🔍 正在检索特定审计卷宗...")
        # 建议加上 networkidle，确保 JavaScript 渲染出的故事块全部加载完成
        page.goto("https://www.libraryofshortstories.com/stories", wait_until="networkidle")

        # 模拟 2 次下滑以扩充数据量
        for _ in range(2):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        soup = BeautifulSoup(page.content(), 'html.parser')
        
        # --- 精准选择器逻辑 ---
        # 寻找 class 为 story_tile_cluster 的 div 内部
        # class 同时包含 story_tile 和 true_link 的 a 标签
        target_links = soup.select('div.story_tile_cluster a.story_tile.true_link')
        
        results = []
        base_url = "https://www.libraryofshortstories.com"

        for link in target_links:
            print(f"开始打印---------------{link}")
            href = link.get('href')
            if not href: continue
            
            full_url = base_url + href if href.startswith('/') else href
            # 提取文本内容作为标题
            title = link.get_text(strip=True)

            results.append({
                "item_number": f"REG-{hash(full_url) % 1000000}",
                "title": f"Internal Review: {title}",
                "content": f"Full protocol access via: {full_url}",
                "raw_source": full_url
            })

        '''
        # 存入 Supabase
        if results:
            # 这里的 upsert 会根据 item_number (或你在表里设定的唯一约束) 自动处理重复
            supabase.table("disguised_archives").upsert(results).execute()
            print(results)
        else:
            print("⚠️ 未找到匹配的 a.story_tile.true_link，请检查页面是否已完全加载。")
        '''

        browser.close()

if __name__ == "__main__":
    scrape_specific_stories()