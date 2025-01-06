from tfeed.ui import RssReader
from tfeed.utils import parse, get_entries, get_news_source
import sys


def main(**kwargs):
    newsfeed = parse(kwargs.get("url"))
    entries = get_entries(newsfeed)
    app = RssReader(
        css_path="../ui/styles.css",
        title=get_news_source(newsfeed) or "tfeed",
        help_file="ui/help.md",
        entries=entries
    )
    app.run()


if __name__ == "__main__":
    try:
        url = sys.argv[1]
    except IndexError:
        sys.exit("Please provide a valid RSS feed URL as an argument.")
    main(url=url)