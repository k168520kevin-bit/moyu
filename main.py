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
        for _ in range(1):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        soup = BeautifulSoup(page.content(), 'html.parser')
        
        # --- 精准选择器逻辑 ---
        # 寻找 class 为 story_tile_cluster 的 div 内部
        # class 同时包含 story_tile 和 true_link 的 a 标签
        target_links = soup.select('div.story_tile_cluster a.story_tile.true_link')
        
        base_url = "https://www.libraryofshortstories.com"

        # 1. 检查数据库中是否已存在该 URL
        existing_data = supabase.table("articles") \
            .select("from_url") \
            .eq("from_url", full_url) \
            .execute()

        for link in target_links:
            print(f"开始打印---------------")
            path = link.get('href')
            # 顺便获取一下里面的标题，方便确认
            title_element = link.select_one('.story_tile_title')

            title = title_element.get_text(strip=True) if title_element else "未知标题"
            
            print(f"标题: {title.ljust(20)} | 路径: {path}")

            full_url = base_url + path
            print(f"\n📖 正在深入抓取: {full_url}")

            # 2. 判断是否存在
            if existing_data.data:
                print(f"⏭️  跳过已存在审计项: {full_url}")
                continue  # 存在就直接跳到下一个循环，不执行下面的 page.goto

            # 2. 访问详情页
            page.goto(full_url, wait_until="networkidle")
            detail_soup = BeautifulSoup(page.content(), 'html.parser')

            # 3. 定位详情页内容
            # 找到阅读区域
            reading_section = detail_soup.find('div', id='reading_section')

            if reading_section:
                # 获取标题 (h1)
                title = reading_section.find('h1').get_text(strip=True) if reading_section.find('h1') else "无标题"
                
                # 获取正文内容 (story_text 里的所有 p)
                story_text_div = reading_section.find('div', id='story_text')
                if story_text_div:
                    # 提取所有 p 标签的文本，并用换行符连接
                    paragraphs = [str(p) for p in story_text_div.find_all('p')]
                    full_text = "\n\n".join(paragraphs)
                    
                    print(f"✅ 成功抓取文章：[{title}]")
                    print(f"📝 内容预览 (前 100 字): {full_text}")
                    
                    # --- 这里可以执行你的 Supabase 写入逻辑 ---
                    supabase.table("articles").upsert({
                        "title": title,
                        "content": full_text,
                        "from_url": full_url
                    }).execute()
                else:
                    print("❌ 未找到正文内容 (story_text)")
            else:
                print("❌ 未找到阅读区域 (reading_section)")

            # 适当休眠，保护对方服务器
            time.sleep(2)


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