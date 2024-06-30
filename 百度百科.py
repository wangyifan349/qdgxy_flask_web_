import requests
from bs4 import BeautifulSoup
import re
import random
from fake_useragent import UserAgent

# 设置要爬取的网页 URL
url = "https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E7%88%AC%E8%99%AB"

# 设置代理服务器
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

# 设置浏览器头，使用随机的 User-Agent
ua = UserAgent()
headers = {
    'User-Agent': ua.random
}

# 向网页发送 GET 请求
response = requests.get(url, headers=headers, proxies=proxies)

# 使用 BeautifulSoup 解析 HTML 内容
soup = BeautifulSoup(response.content, 'html.parser')

# 提取网页标题
title = soup.find('h1').text.strip()
print(f"标题: {title}")

# 提取网页内容
content = soup.find('div', {'class': 'lemma-summary'}).text.strip()
print(f"内容: {content}")

# 找到网页上的所有链接
links = soup.find_all('a', href=re.compile(r'^https?://'))

# 创建一个集合来存储唯一的链接
unique_links = set()

# 遍历链接，提取 href 属性
for link in links:
    href = link.get('href')
    if href:
        unique_links.add(href)

# 打印唯一的链接
print(f"唯一链接: {len(unique_links)}")
for link in unique_links:
    print(link)

# 尝试自动找到网页上的新链接
new_links = set()
for link in unique_links:
    try:
        response = requests.get(link, headers=headers, proxies=proxies)
        soup = BeautifulSoup(response.content, 'html.parser')
        new_links.update({a.get('href') for a in soup.find_all('a', href=re.compile(r'^https?://'))})
    except Exception as e:
        print(f"错误: {e}")

# 打印新链接
print(f"新链接: {len(new_links)}")
for link in new_links:
    print(link)
