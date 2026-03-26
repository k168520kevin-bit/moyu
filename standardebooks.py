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

                #分析属于哪种网站结构
                #调用不同的爬虫策略，目前发现的目录结构有三种
                #只有chapter-1的模式
                #part-1 chapter-1-1的模式
                #section-1 chapter-1的模式
                #如果这三种模式都不匹配，抛出日志信息，再添加网页结构

                if parts:
                    #part-1 chapter-1-1的模式
                    if soup.select_one('section[epub\:type*="part"]'):
                        get_from_part()

                    #section-1 chapter-1的模式
                    if soup.select_one('section[id^="section-"], section[epub\:type*="division"]'):
                        get_from_section()

                    #只有chapter-1的模式
                    if soup.select_one('section[id^="chapter-"]'): 
                        get_from_chapter()

                    

                    
                    #如果这三种模式都不匹配，抛出日志信息，再添加网页结构
                    
                        
                else:
                    # 场景 B：书没有 Part，直接是章节
                    # 2. 核心：寻找所有的 <section> 标签
                    # Standard Ebooks 的章节通常在 <section> 内，且有 epub:type="chapter"
                    print(f"检测到 没有part ...")   
            
        except Exception as e:
            print(f"抓取第 {page_num} 页时出错: {e}")
            break

    return all_extracted_paths

#只有chapter-1的模式
def get_from_chapter():
    print(f"只有chapter-1的模式")

#part-1 chapter-1-1的模式
def get_from_part():
    print(f"part-1 chapter-1-1的模式")

#section-1 chapter-1的模式
def get_from_section():
    print(f"section-1 chapter-1的模式")

def test(test_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    response = requests.get(test_url, headers=headers)
    response.raise_for_status() # 检查请求是否成功

    soup = BeautifulSoup(response.text, 'html.parser')

    #part-1 chapter-1-1的模式
    if soup.select_one('section[epub\:type*="part"]'):
        get_from_part()

    #section-1 chapter-1的模式
    elif soup.select_one('section[id^="section-"], section[epub\:type*="division"]'):
        get_from_section()

    #只有chapter-1的模式
    elif soup.select_one('section[id^="chapter-"]'): 
        get_from_chapter()

    else:
        print(f"其他模式")


# --- 执行脚本 ---
# 假设你想爬取前 5 页的内容
start = 1
end = 1 
#final_paths = get_all_book_paths(start, end)
test_url = "https://standardebooks.org/ebooks/dorothy-l-sayers_robert-eustace/the-documents-in-the-case/text/single-page"
final_paths = test(test_url)

print(f"\n任务完成！总共抓取到 {len(final_paths)} 条书籍路径。")