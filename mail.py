#%%
import os
import sys
import json
import smtplib
import platform
import requests
from email.mime.text import MIMEText
from email.message import EmailMessage

import get_news

def f(non_f_str: str):
    """
    f string implementation for the json variables
    """
    return eval(f'f"""{non_f_str}"""')

def get_file_path(filename):
    path = os.path.realpath(__file__) + "/"
    if platform.system() == "Windows": path.replace("\\", "/")
    return os.path.join(path, filename)

def check_login(address, password):
    """
    Verifies if the user put a valid email
    """
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(address, password)
        result = True
    except:
        result = False
    return result

def create_body(topic, n=10):
    print(f"processing topic: {topic}")
    url = get_news.create_url(topic) if topic.lower() not in get_news.topics_url else get_news.topics_url[topic.lower()]
    soup = get_news.get_page(url)
    news = get_news.get_news(soup, n=n)
    body = get_news.format_news(news)
    print(f"topic {topic} processed\n")
    return body

def create_html_body(title: str, link: str, date: str, description: str, source: str, img: str) -> str:
    template = f"""
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .card-horizontal {{
            display: flex;
            flex: 1 1 auto;
        }}
        </style>
        </head>
        <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-12 mt-3">
                    <div class="card">
                        <div class="card-horizontal">
                            <div class="card-body">
                                <img class="" src="{img}" alt="Card image cap" style="float: left;border: 10px solid rgba(255,255,255,0);">                            
                                <a href="{link}" style="float: center;border: 1px solid rgba(255,255,255,0);">
                                    <h4 class="card-title">{title}</h4>
                                </a>
                                <p class="card-text">{description}</p>
                                <p style="color:grey;">{source} - {date}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        </body>
        </html>
    """
    return template

def create_htmls(topic, n=10):
    print(f"processing topic: {topic}")
    url = get_news.create_url(topic) if topic.lower() not in get_news.topics_url else get_news.topics_url[topic.lower()]
    soup = get_news.get_page(url)
    news = get_news.get_news(soup, n=n)
    htmls = [create_html_body(title, news[title]["link"], news[title]["data"],
             news[title]["descrição"], news[title]["fonte"], news[title]["img"])
             for title in news]
    return "\n\n\n".join(htmls)

def _send_email(address, to_email, subject, body, smtp):
    """
    Sends the email to the patient and doctors informing the test results
    """
    try:
        with open("mail_list.txt", "r") as _emails:
            emails = _emails.read()
        # transform ",", new lines and ";" into whitespace
        emails_list = emails.replace("\n"," ").replace(","," ").replace(";"," ").split(" ")
        cc = list(filter(lambda x: x!= "", emails_list)) # clean up the list
    except FileNotFoundError:
        cc = [""]

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = address
    msg['To'] = to_email
    msg['CC'] = cc
    msg.set_content(body)

    smtp.send_message(msg)

def send_mail(address, password, to_emails, subject, raw_body, is_html=False):
    if type(to_emails) == str: to_emails = [to_emails]
    
    body = MIMEText(raw_body, 'html') if is_html else raw_body
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(address, password)
        for to_email in to_emails:
            _send_email(address, to_email, subject, body, smtp)
# %%
