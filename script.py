#%%
import get_news


uber_topic = ["Lei do SeAC"] # get all news from this one
topics = ["ANATEL", "Ciência, Tecnologia e Informação", "Ciência, Tecnologia e Informação",
    "Ciência, Tecnologia e Informação", "Serviço de Valor Adicionado", "Serviço de Valor Agregado",
    "Comissão de Ciência e Tecnologia", "Conteúdo Audiovisual", "Lei Geral de Telecomunicação",
    "Serviço de Acesso Condicionado"] # get news which fall under these topics

keywords = ["SVA", "Câmara", "Senado"] # if these words are on the title, get it

topic = "Lei do SeAC"
n = 10

url = get_news.create_url(topic) if topic.lower() not in get_news.topics_url else get_news.topics_url[topic.lower()]
soup = get_news.get_page(url)
news = get_news.get_news(soup, n=n, save_history=False)
get_news.add_summary(news, add_ngrams=True, n=3, top_n=10)
# %%
