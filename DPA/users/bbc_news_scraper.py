# bbc_news_scraper.py
import feedparser

def get_bbc_ukrainian_news(rss_url):
    feed = feedparser.parse(rss_url)

    if feed.status != 200:
        print("Помилка: Неможливо отримати дані з RSS-каналу")
        return []

    news_list = []

    for entry in feed.entries:
        news_item = {
            'title': entry.title,
            'link': entry.link
        }

        news_list.append(news_item)

    return news_list
