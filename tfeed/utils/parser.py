import feedparser
from html2text import html2text


def parse(source):
    return feedparser.parse(source)


def get_entries(feed):
    entries = []
    for index in range(len(feed["entries"])):
       entry = dict() 
       entry["title"] = feed["entries"][index]["title"]
       entry["summary"] = html2text(feed["entries"][index]["content"][0]["value"])
       entry["date"] = feed["entries"][index]["published"]
       entries.append(entry)
    return entries


def get_news_source(feed):
    return feed["feed"]["title"]

