import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import mysql.connector
import random
from db import db_host, db_user, db_password, db_database

# MySQL数据库连接配置
db_config = {
    'host': 'db_host',
    'user': 'db_user',
    'password': 'db_password',
    'database': 'db_database'
}

# 初始页面URL
base_url = 'https://www.yapingkeji.com/product/'

# 存储所有产品页面的链接
product_links = [base_url]

# 自定义User-Agent
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.67 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.67 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.67 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
]
# 从 user_agents 列表中随机选择一个 User-Agent
headers = {
    'User-Agent': random.choice(user_agents)
}
# Socks代理配置
proxies = {
    'http': 'socks5h://127.0.0.1:7890',
    'https': 'socks5h://127.0.0.1:7890'
}

# 发送请求并获取第一页内容
response = requests.get(base_url, headers=headers, proxies=proxies)

soup = BeautifulSoup(response.content, 'html.parser')

# 定位所有的链接元素
all_links = soup.find_all('a', href=True)

# 动态生成要检查的关键字列表
start_page = 2
end_page = 15
keywords = ['p' + str(i) for i in range(start_page, end_page + 1)]  # 生成 ['p2', 'p3', 'p4', ..., 'p15']

# 遍历所有链接，找到包含指定关键字的链接
for link in all_links:
    href = link['href']
    for keyword in keywords:
        if keyword in href:
            absolute_url = urljoin(base_url, href)
            if absolute_url not in product_links:
                product_links.append(absolute_url)
            break  # 找到匹配的关键字后退出内循环

# 查找下一页链接并获取更多页面内容
next_page_link = soup.find('a', string='下一页', href=True)
while next_page_link:
    next_page_url = urljoin(base_url, next_page_link['href'])
    response = requests.get(next_page_url,headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 继续查找页面上的链接
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        href = link['href']
        for keyword in keywords:
            if keyword in href:
                absolute_url = urljoin(base_url, href)
                if absolute_url not in product_links:
                    product_links.append(absolute_url)
                break  # 找到匹配的关键字后退出内循环
    
    # 查找下一页链接
    next_page_link = soup.find('a', string='下一页', href=True)

# # 打印所有找到的产品页面链接
# for link in product_links:
#     print(link)
# 连接到MySQL数据库
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    for link in product_links:
        response = requests.get(link,headers=headers, proxies=proxies)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找所有符合条件的 <div> 标签
        div_tags = soup.find_all('div', class_='item-thumbnail')

        # 遍历每个符合条件的 <div> 标签
        for div_tag in div_tags:
            # 在每个 <div> 标签中查找 <img> <a>标签
            img_tags = div_tag.find_all('img')
            a_tags = div_tag.find_all('a')
            for a in a_tags:
                href = a.get('href')
                response2 = requests.get(href,headers=headers, proxies=proxies)
                response2.raise_for_status() # 检查请求是否成功
                html_content = response2.text # 获取返回的网页内容
                soup2 = BeautifulSoup(html_content, 'html.parser')
                page = soup2.find_all('div', class_='theme-box wp-posts-content')# 查找特定的元素
                page_str = str(page)
                remove_str = """[<div class="theme-box wp-posts-content" data-nav="posts">"""
                remove_str2 = '</div>]'
                page_delete = page_str.replace(remove_str, '').replace(remove_str2, '')  
            # 输出每个 <img> 标签的 src\alt 属性值
            for img in img_tags:
                img_src = img.get('data-src')
                img_alt = img.get('alt')
                
            # 插入数据到数据库
                if img_src:
                    insert_query = "INSERT INTO product_information (title, image, link, page) VALUES (%s, %s, %s, %s)"
                    data = (img_alt, img_src, href, page_delete)
                    cursor.execute(insert_query, data)
                    conn.commit()  # 提交事务，将数据插入到数据库中
    print("数据插入成功！")
except mysql.connector.Error as err:
    print(f"数据库错误：{err}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("数据库连接已关闭。")