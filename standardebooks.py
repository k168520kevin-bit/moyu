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

            # 2. 开始循环：遍历你在网页中找到的所有 <a> 标签 (links)
            for link in links:
                
                # 3. 尝试获取这个标签里的 'href' 属性（也就是 /ebooks/xxx 那个路径）
                path = link.get('href')
                print(f"链接: {path}")
                
                # 4. 判断一下：如果这个路径不是空的（即存在这个属性）
                if path:
                    
                    # 5. 把这个干净的路径存进我们的列表里
                    page_paths.append(path)

            
            print(f"本页抓取到 {len(page_paths)} 本书")
            all_extracted_paths.extend(page_paths)
            
            # 💡 关键：礼貌爬虫，每页爬完歇 1-2 秒，防止被封 IP
            time.sleep(2)
            
        except Exception as e:
            print(f"抓取第 {page_num} 页时出错: {e}")
            break

    return all_extracted_paths

# --- 执行脚本 ---
# 假设你想爬取前 5 页的内容
start = 1
end = 5 
final_paths = get_all_book_paths(start, end)

print(f"\n任务完成！总共抓取到 {len(final_paths)} 条书籍路径。")