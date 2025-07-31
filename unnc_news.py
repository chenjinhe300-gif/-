from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# 设置无头浏览器
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# 打开新闻页面
url = "https://www.nottingham.edu.cn/en/humanities-and-social-sciences/schools-and-department/international-studies/news.aspx"
driver.get(url)
time.sleep(5)  # 等待 JS 加载

# 解析 HTML
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# 找到所有 article 区块
articles = soup.find_all("article", class_="col-md-8 offset-md-1 article-body userContent")

print(f"找到新闻条数：{len(articles)}")
print("-" * 40)

for article in articles:
    title_tag = article.find("caption", class_="Blue-five")
    title = title_tag.get_text(strip=True) if title_tag else "无标题"

    # 提取正文中的段落（table > tbody > tr > td > p）
    content_paras = article.find_all("p")
    content = "\n".join(p.get_text(strip=True) for p in content_paras if p.get_text(strip=True))

    print(f"📰 标题：{title}")
    print(f"📄 正文预览：{content[:100]}...")
    print("-" * 40)
