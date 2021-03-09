import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import KlimItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class KlimSpider(scrapy.Spider):
	name = 'klim'
	start_urls = ['https://www.klimsparekasse.dk/gaa-til-nyhedsarkiv/?page=1']

	def parse(self, response):
		articles = response.xpath('//div[@class="col-md-9"]')
		for article in articles:
			title = article.xpath('.//h4/text()').get()
			post_links = article.xpath('.//a[@class="link link1"]/@href').getall()
			yield from response.follow_all(post_links, self.parse_post,cb_kwargs=dict(title=title))

		next_page = response.xpath('//a[@title="Next page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,title):
		date = response.xpath('//p[@class="news-date"]/text()').get()
		content = response.xpath('//div[@class="col-md-4 column"]//text() | //div[@class="kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q"]//text()[not (ancestor::h1)] | //div[@class="col-md-12 column"]//p//text() ').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=KlimItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
