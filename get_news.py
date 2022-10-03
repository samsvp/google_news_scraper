#%%
"""
Google news parser
"""
import json
import requests
import html2text
import summarizer
from bs4 import BeautifulSoup, element
from urllib.parse import urljoin

from typing import *
 

news_url = "https://news.google.com/"

topics_url = {
    "oi": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSkwyMHZNRFV4ZGpGakVnVndkQzFDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR%3Apt-419"
}


history_file = "history.json"
try:
    with open(history_file, "r", encoding='utf-8') as f:
        history = json.load(f)
except FileNotFoundError:
    history = {}

 
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
    resume = el.find("a", {"class" : "RZIKme"}).text
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
    imgs = {get_article_title(fig.parent.parent) : fig.find("img").get("src") for fig in figures}
    return imgs


def sort_news(news: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Returns the news sorted by date
    """
    def _sorted(title: str):
        date = news[title]["data"]
        if "horas" in date: return int(date.split(" ")[0])
        elif "ontem" in date: return 24
        elif "dias" in date: return 24 + int(date.split(" ")[0])
        else: return 1000

    return dict(sorted(news.items(), key=lambda item: _sorted(item[0])))


def get_news(soup: BeautifulSoup, class_id=None, n=10, sort=True, save_history=True) -> Dict[str, Dict[str, str]]:
    """
    Get the first n news from the given webpage with its metadata
    """
    articles = get_articles(soup)[:n]
    imgs = get_images(soup)
    
    h = html2text.HTML2Text()
    h.ignore_links = True

    news = { get_article_title(article) : {
                        "link" : get_link(article), "data" : get_date(article),
                        "descrição" : get_description(article), "fonte" : get_source(article),
                        "img": imgs.get(get_article_title(article), "")} 
                        for article in articles if get_article_title(article) and get_article_title(article) not in history}
    
    if save_history:
        with open(history_file, "w", encoding='utf-8') as f:
            history.update(news)
            json.dump(history, f, ensure_ascii=False, indent=True)

    return sort_news(news) if sort else news


def add_summary(news: Dict[str, str], add_ngrams=True, n=3, top_n=10) -> Dict[str, Dict[str, Any]]:
    """Adds news summary. Modifies the original dict. Can add
    the 'top_n' ngrams count to the news dict. Modifies the original dict"""
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True

    for title in news:
        # gets the text inside an html string. Ignores links urls
        # and script tags
        page = get_page(news[title]["link"])
        articles = get_articles(page)
        articles.sort(key=lambda a : len(a), reverse=True)
        
        if not articles: continue

        article = h.handle(str(articles[0]))
        summary = summarizer.get_summary(article, 7) if article else ""
        news[title]["summary"] = summary
        
        if add_ngrams:
            ngrams_freq = [(k, v) for k, v in
                summarizer.get_ngrams_freq(summary, n).items()]
            ngrams_freq.sort(key=lambda x: x[1], reverse=True)
            print(ngrams_freq, "\n")
            news[title]["ngram"] = ngrams_freq[:top_n]

    return news


def add_ngrams(news: Dict[str, str], n: int, top_n: int) -> Dict[str, Dict[str, Any]]:
    """Adds the 'top_n' ngrams count to the news dict. Modifies the original dict"""
    for title in news:
        summary = news[title]["summary"]
        ngrams_freq = [(k, v) for k, v in
            summarizer.get_ngrams_freq(summary, n).items()]
        print(ngrams_freq)
        # sort based on the freq count
        ngrams_freq.sort(key=lambda x: x[1], reverse=True)

        news[title]["ngram"] = ngrams_freq[:top_n]

    return news


def get_news_summary(link: str) -> List[str]:
    """
    Gets the news summary for the given page
    """
    r = get_page(link)
    if not r: return ""

    articles = get_articles(r)
    
    if not articles: return ""

    articles.sort(key=lambda a : len(a), reverse=True)
    # gets the text inside an html string. Ignores links urls
    # and script tags
    h = html2text.HTML2Text()
    h.ignore_links = True
    article = h.handle(str(articles[0]))
    
    summary = summarizer.get_summary(article, 7) if article else ""
    return summary


def format_news(news: Dict[str,Dict[str,str]], get_summary=False) -> str:
    texts = []
    for title in news:
        text = title + "\n\n"
        text += "\n".join([f"{info}: {news[title][info]}" for info in news[title] if info != "img"])
        if get_summary:
            text += f"\nsumario: {get_news_summary(news[title]['link'])}"
        texts.append(text)
    return "\n\n\n\n".join(texts)

# %%
