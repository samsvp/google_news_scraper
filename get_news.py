#%%
"""
Google news parser
"""
import requests
import summarizer
from bs4 import BeautifulSoup, element
from urllib.parse import urljoin
from typing import List, Dict
 

# oi topic url
oi_url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSkwyMHZNRFV4ZGpGakVnVndkQzFDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR%3Apt-419"
oi_class = "VDXfz"

news_url = "https://news.google.com/"

def create_url(q: str) -> str:
    """
    Creates a vali url for a given query
    """
    query = q.replace(" ", "%20")
    url = f"https://news.google.com/search?q={query}&hl=pt-BR&gl=BR&ceid=BR%3Apt-419"
    return url

def get_page(url: str) -> BeautifulSoup:
    """
    Gets html from the given url
    """
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
    except Exception as e:
        print(e)
        soup = None
    return soup

def get_article_title(el: element.Tag) -> str:
    """
    Get the article title in the element "el"
    """
    try:
        title = el.find("h3").text # google news titles are inside the h3 tag
    except:
        title = ""
    return title

def get_articles_title(el: element.Tag) -> List[str]:
    """
    Get all article titles in the element "el"
    """
    titles = [h3.text for h3 in el.find_all("h3")] # google news titles are inside the h3 tag
    return titles

def get_articles(el: element.Tag, class_id=None) -> element.ResultSet:
    """
    Get all articles in the element "el"
    """
    try:
        articles = el.find_all("article") if class_id is None else el.find_all("article", {"class" : class_id})
    except:
        articles = ""
    return articles

def get_link(el: element.Tag, class_id=None) -> str:
    """
    Get the first link in the element "el"
    """
    relative_link = el.find("a").get("href") if class_id is None else el.find("a", {"class" : class_id})
    link = urljoin(news_url, relative_link)
    return link

def get_links(el: element.Tag, class_id=None) -> List[str]:
    """
    Get all links in the element "el"
    """
    a_tags = el.find_all("a") if class_id is None else el.find_all("a", {"class" : class_id})
    links = [urljoin(news_url, link.get("href")) for link in a_tags]
    return links

def get_date(el: element.Tag) -> str:
    """
    Get the day which the article was published
    """
    post_time = el.find("time")
    return post_time.text if post_time is not None else "Sem data"

def get_description(el: element.Tag) -> str:
    """
    Gets the news description
    """
    resume = el.find("span", {"class" : "xBbh9"}).text
    return resume

def get_source(el: element.Tag) -> str:
    """
    Get the news source
    """
    a_tags = el.find_all("a")
    source = a_tags[-1].text
    return source

def get_images(soup: BeautifulSoup) -> List[str]:
    """
    Get the news image
    """
    figures = soup.find_all("figure")
    imgs = [fig.find("img").get("src") for fig in figures] 
    return imgs

def get_news(soup: BeautifulSoup, class_id=None, n=10) -> Dict[str, str]:
    """
    Get all news from the given webpage with its metadata
    """
    articles = get_articles(soup)[:n]
    imgs = get_images(soup)[:n]
    news = { get_article_title(article) : {
                        "link" : get_link(article), "data" : get_date(article),
                        "descrição" : get_description(article), "fonte" : get_source(article),
                        "img": imgs[i] } 
                        for i,article in enumerate(articles) if get_article_title(article)}
    return news

def get_news_summary(link: str) -> List[str]:
    """
    Gets the news summary for the given page
    """
    r = get_page(link)
    if not r: return ""

    articles = get_articles(r)
    articles.sort(key=lambda a : len(a), reverse=True)
    summary = summarizer.get_summary(articles[0].text, 7) if articles else ""
    return summary

def format_news(news: Dict[str,Dict[str,str]]) -> str:
    texts = []
    for title in news:
        text = title + "\n\n"
        text += "\n".join([f"{info}: {news[title][info]}" for info in news[title]])
        text += f"\nsumario: {get_news_summary(news[title]['link'])}"
        texts.append(text)
    return "\n\n\n\n".join(texts)
