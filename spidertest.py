import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import mysql.connector

# MySQL数据库连接配置
db_config = {
    'host': '你的数据库主机',
    'user': '你的用户名',
    'password': '你的密码',
    'database': '你的数据库名称'
}

# 初始页面URL
base_url = 'https://www.yapingkeji.com/product/'

# 存储所有产品页面的链接
product_links = [base_url]

# 发送请求并获取第一页内容
response = requests.get(base_url)
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
    response = requests.get(next_page_url)
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
for link in product_links:
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 查找所有符合条件的 <div> 标签
    div_tags = soup.find_all('div', class_='item-thumbnail')

    # 遍历每个符合条件的 <div> 标签
    for div_tag in div_tags:
        # 在每个 <posts> 标签中查找 <img> <a>标签
        img_tags = div_tag.find_all('img')
        a_tags = div_tag.find_all('a')
        for a in a_tags:
            href = a.get('href')  
        # 输出每个 <img> 标签的 src\alt 属性值
        for img in img_tags:
            img_src = img.get('data-src')
            img_alt = img.get('alt')
            
            if img_src:
                print(img_alt)
            if href:
                print(href)
            if img_src:
                print(img_src)
