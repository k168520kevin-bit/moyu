import requests
from bs4 import BeautifulSoup
import time
import re

def get_all_book_paths(start_page, end_page):
    base_url = "https://standardebooks.org/ebooks"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    all_extracted_paths = []

    # 分页循环：从 start_page 到 end_page
    for page_num in range(start_page, end_page + 1):
        print(f"--- 正在处理第 {page_num} 页 ---")
        
        # 拼接带参数的 URL
        params = {'page': page_num}
        
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status() # 检查请求是否成功
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 使用 CSS 选择器精准定位缩略图容器中的链接
            links = soup.select('div.thumbnail-container a[property="schema:url"]')
            
            
            # 1. 先准备一个空列表，用来装抓到的路径
            page_paths = []

            base_url = "https://standardebooks.org"

            # 2. 开始循环：遍历你在网页中找到的所有 <a> 标签 (links)
            for link in links:
                # 3. 尝试获取这个标签里的 'href' 属性（也就是 /ebooks/xxx 那个路径）
                path = link.get('href')
                print(f"链接: {path}")
                book_url = base_url + path + "/text/single-page"
                print(f"链接: {book_url}")
                response = requests.get(book_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 1. 获取书名（作为这一批章节的父级标识）
                book_title = soup.find('h1').get_text(strip=True)
                print(f"链接: {book_title}")

                # 2. 寻找所有的 Part（部）
                # 注意：在 CSS 选择器中，属性名里的冒号 ":" 需要用反斜杠 "\" 转义
                # [epub\:type*="part"] 意思是：寻找 epub:type 属性中包含 "part" 字样的标签
                parts = soup.select('section[epub\:type*="part"]')
                print(f"链接: {parts}")

                chapter_global_index = 1 # 全局章节计数器，用于排序

                if parts:
                    # 场景 A：书有 Part 结构
                    for p_idx, part in enumerate(parts, start=1):
                        print(f"检测到有part ...")
                        # 获取 Part 的标题（例如 "Part I"）
                        part_title_tag = part.find(['h2', 'h3'])
                        # 2. 核心：寻找所有的 <section> 标签
                        # Standard Ebooks 的章节通常在 <section> 内，且有 epub:type="chapter"
                        part_name = part_title_tag.get_text(strip=True) if part_title_tag else f"Part {p_idx}"
                        print(f"检测到 {part_name} ...")
                        
                        # 在这个 Part 内部寻找所有章节
                        # 在这个 Part 内部寻找 Chapter
                        # 同样使用包含匹配，因为 chapter 后面也跟着 bodymatter 等字样
                        chapters = part.select('section[epub\:type*="chapter"]')
                        for chapter in chapters:
                            save_chapter(chapter, book_title, part_name, chapter_global_index)
                            chapter_global_index += 1

                            time.sleep(2)
                else:
                    # 场景 B：书没有 Part，直接是章节
                    # 2. 核心：寻找所有的 <section> 标签
                    # Standard Ebooks 的章节通常在 <section> 内，且有 epub:type="chapter"
                    print(f"检测到 没有part ...")
                    chapters = part.select('section[epub\:type*="chapter"]')
                    for chapter in chapters:
                        save_chapter(chapter, book_title, None, chapter_global_index)
                        chapter_global_index += 1
                        time.sleep(2)           
            
        except Exception as e:
            print(f"抓取第 {page_num} 页时出错: {e}")
            break

    return all_extracted_paths


def save_chapter(chapter_node, book_title, part_name, index):
    print(f"链接: {book_title}")


# --- 执行脚本 ---
# 假设你想爬取前 5 页的内容
start = 1
end = 1 
final_paths = get_all_book_paths(start, end)

print(f"\n任务完成！总共抓取到 {len(final_paths)} 条书籍路径。")