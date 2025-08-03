# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

#  Selenium加载新闻列表页
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

url = "https://www.nottingham.edu.cn/cn/press-release/news-listing.aspx"
driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

#  提取所有新闻卡片
cards = soup.find_all("div", class_="news-card__content")

email_body = f"📰 UNNC 新闻简报 📢\n共抓取到 {len(cards)} 条新闻。\n\n"

if len(cards) == 0:
    email_body += "当前未抓取到任何新闻内容，可能页面结构发生变化。\n"

#  逐个抓取详情页
for idx, card in enumerate(cards, 1):
    title_tag = card.find("h3")
    link_tag = title_tag.find("a") if title_tag else None

    list_title = title_tag.get_text(strip=True) if title_tag else "无标题"
    detail_url = (
        "https://www.nottingham.edu.cn" + link_tag["href"]
        if link_tag and link_tag.has_attr("href")
        else None
    )

    email_body += f"列表标题：{list_title}\n"
    if not detail_url:
        email_body += "❌ 无详情页链接\n" + "-"*40 + "\n"
        continue

    #  请求详情页
    try:
        r = requests.get(detail_url, timeout=10)
        r.encoding = "utf-8"
        detail_soup = BeautifulSoup(r.text, "html.parser")

        # 详情标题
        detail_title_tag = detail_soup.find("h1")
        detail_title = detail_title_tag.get_text(strip=True) if detail_title_tag else "无详情标题"

        # 详情正文
        paragraphs = detail_soup.find_all("p")
        detail_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        email_body += f"🔗 链接：{detail_url}\n"
        email_body += f"📄 详情标题：{detail_title}\n"
        email_body += f"📝 正文预览：{detail_text[:300]}...\n"

    except Exception as e:
        email_body += f"抓取详情页失败: {repr(e)}\n"

    email_body += "-"*40 + "\n"

# 构造邮件
sender_email = "地址"
receiver_email = "邮箱地址"
password = "密码"  # 你的Gmail应用专用密码

msg = MIMEMultipart()
msg['From'] = Header(sender_email, 'utf-8')
msg['To'] = Header(receiver_email, 'utf-8')
msg['Subject'] = Header("UNNC 新闻简报 📬", 'utf-8')

msg.attach(MIMEText(email_body, "plain", "utf-8"))

# 6️⃣ 发送邮件
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.send_message(msg)
    print(" 邮件发送成功！")
except Exception as e:
    print("邮件发送失败:", repr(e))
