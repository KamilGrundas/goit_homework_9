from scrapy import signals, Spider
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
import json


class QuotesSpider(Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    
    def __init__(self):
        self.quotes = []
        self.authors = []
        self.authors_visited = set()

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            author = quote.xpath("span/small/text()").get()
            tags = quote.xpath("div[@class='tags']/a/text()").extract()
            quote_ = quote.xpath("span[@class='text']/text()").get()

            self.quotes.append(
                {
                    "tags": tags,
                    "author": author,
                    "quote": quote_
                }
            )
            
            about_link = quote.xpath("span/a/@href").get()
            if about_link and author not in self.authors_visited:
                self.authors_visited.add(author)
                yield response.follow(about_link, self.parse_author)

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield response.follow(next_link, self.parse)

    def parse_author(self, response):
        name = response.xpath("//h3[@class='author-title']/text()").get()
        birth_date = response.xpath("//span[@class='author-born-date']/text()").get()
        birth_location = response.xpath("//span[@class='author-born-location']/text()").get()
        description = (response.xpath("//div[@class='author-description']//text()").get().strip())

        self.authors.append(
            {
                "fullname": name,
                "born_date": birth_date,
                "born_location": birth_location,
                "description": description,
            }
        )


def save_json(file_name, content):
    with open(file_name, "w") as f:
        json.dump(content, f, indent=4)


def spider_closed(spider):
    save_json("quotes.json", spider.quotes)
    save_json("authors.json", spider.authors)


def main():
    process = CrawlerProcess()
    dispatcher.connect(spider_closed, signal=signals.spider_closed) #Wait for signal from spider to finish work, then execute function spider_closed
    process.crawl(QuotesSpider)
    process.start()


if __name__ == "__main__":
    main()
