import feedparser
import requests


def fetch_rss_feed(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def parse_rss_feed(rss_data):
    feed = feedparser.parse(rss_data)
    news_items = []

    for entry in feed.entries:
        news_item = {
            'title': entry.title,
            'link': entry.link,
            'pubDate': entry.published,
            'description': entry.description,
            'category': entry.get('category', 'No category'),
            'author': entry.get('author', 'No author'),
            'guid': entry.guid,
            'anons': entry.get('rbc_news_anons', 'No anons'),
            'news_id': entry.get('rbc_news_news_id', 'No news ID'),
            'newsDate_timestamp': entry.get('rbc_news_newsDate_timestamp', 'No newsDate timestamp'),
            'newsModifDate': entry.get('rbc_news_newsModifDate', 'No newsModifDate'),
            'newsline': entry.get('rbc_news_newsline', 'No newsline'),
            'tags': [tag for tag in entry.get('rbc_news_tag', [])],
            'full_text': entry.get('rbc_news_full_text', 'No full text')
        }
        news_items.append(news_item)

    return news_items


def print_news_items(news_items):
    for item in news_items:
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Published Date: {item['pubDate']}")
        print(f"Description: {item['description']}")
        print(f"Category: {item['category']}")
        print(f"Author: {item['author']}")
        print(f"GUID: {item['guid']}")
        print(f"Anons: {item['anons']}")
        print(f"News ID: {item['news_id']}")
        print(f"News Date Timestamp: {item['newsDate_timestamp']}")
        print(f"News Modification Date: {item['newsModifDate']}")
        print(f"Newsline: {item['newsline']}")
        print(f"Tags: {', '.join(item['tags'])}")
        print(f"Full Text: {item['full_text']}")
        print("-" * 80)


if __name__ == "__main__":
    rss_url = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    rss_data = fetch_rss_feed(rss_url)
    news_items = parse_rss_feed(rss_data)
    print_news_items(news_items)

