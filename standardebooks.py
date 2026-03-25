import requests
from bs4 import BeautifulSoup
import time

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
                book_url = base_url + path
                response = requests.get(book_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                

                # 1. 获取书名（作为这一批章节的父级标识）
                book_title = soup.find('h1').get_text(strip=True)
                book_id = book_url.split('/')[-1] # 得到 'chance'

                # 2. 核心：寻找所有的 <section> 标签
                # Standard Ebooks 的章节通常在 <section> 内，且有 epub:type="chapter"
                chapters = soup.find_all('section', attrs={"epub:type": "chapter"})
                
                # 如果没找到特定的 chapter 属性，就找普通的 section
                if not chapters:
                    chapters = soup.find_all('section')

                print(f"检测到 {len(chapters)} 个章节，准备分段存入数据库...")
                print(f"检测到 {chapters} 个...")

                for index, chapter in enumerate(chapters, start=1):
                    # 提取当前章节标题
                    # 通常章节内第一个 h2 或 h3 是标题
                    title_tag = chapter.find(['h2', 'h3', 'h4'])
                    chapter_title = title_tag.get_text(strip=True) if title_tag else f"Chapter {index}"

                    # 准备数据
                    chapter_data = {
                        "title": f"{book_title} - {chapter_title}", # 方便你在列表页搜索
                        "content": str(chapter),                    # 只存这一章的 HTML
                        "summary": chapter.get_text()[:150] + "...",
                        "from_url": f"{book_url}#chapter-{index}",
                        # 额外字段建议：
                        # "book_group": book_id,
                        # "order_index": index
                    }
                    print(f"检测到 {chapter_data} ...")
                    time.sleep(2)
                

            
            print(f"本页抓取到 {len(page_paths)} 本书")
            all_extracted_paths.extend(page_paths)
            
            
        except Exception as e:
            print(f"抓取第 {page_num} 页时出错: {e}")
            break

    return all_extracted_paths

# --- 执行脚本 ---
# 假设你想爬取前 5 页的内容
start = 1
end = 1 
final_paths = get_all_book_paths(start, end)

print(f"\n任务完成！总共抓取到 {len(final_paths)} 条书籍路径。")