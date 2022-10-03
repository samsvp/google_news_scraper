#%%
import get_news

uber_topic = ["Lei do SeAC"] # get all news from this one
topics = ["ANATEL", "Ciência, Tecnologia e Informação",
    "Serviço de Valor Adicionado", "Serviço de Valor Agregado",
    "Comissão de Ciência e Tecnologia", "Conteúdo Audiovisual", 
    "Lei Geral de Telecomunicação", "Serviço de Acesso Condicionado"] # get news which fall under these topics

keywords = ["SVA", "Câmara", "Senado"] # if these words are on the title, get it

all_news = {}

n = 10
for topic in uber_topic + topics:
    print(topic)
    url = get_news.create_url(topic) if topic.lower() not in get_news.topics_url else get_news.topics_url[topic.lower()]
    soup = get_news.get_page(url)
    news = get_news.get_news(soup, n=n, save_history=False)
    get_news.add_summary(news, add_ngrams=True, n=3, top_n=10)

    all_news[topic] = news

# %%
from collections import Counter

final_news = {}
for topic in uber_topic:
    final_news.update(all_news[topic])
    #del all_news[topic]


titles = [title for topic in topics
            for title in all_news[topic].keys()]

# if the title has been repeated, then add it
filtered_titles = [item
    for item, count in Counter(titles).items() 
        if count > 1 or any(keyword in item for keyword in keywords)]

# if the source contains one of the keywords, then add it
filtered_titles += [title for topic in topics
    for title, value in all_news[topic].items()
        if any(keyword.lower() in value["fonte"].lower() for keyword in keywords)]

# update the final news dict
for topic in topics:
    for title, value in all_news[topic].items():
        if title in filtered_titles: final_news.update({title: value})

print(len(final_news))
# %%
