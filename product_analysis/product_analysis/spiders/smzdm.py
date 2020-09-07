# -*- coding: utf-8 -*-
import scrapy
from ..items import ProductAnalysisItem
class SmzdmSpider(scrapy.Spider):
    name = 'smzdm'
    allowed_domains = ['smzdm.com']
    start_urls = ['https://www.smzdm.com/fenlei/qipaoshui/']

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_ten)

    def parse_ten(self, response):
        products = response.xpath(
            '//*[@class="feed-row-wide"]'
        )[:10]
        for product in products:
            item = ProductAnalysisItem()
            product_name = product.xpath(
                './/h5[@class="feed-block-title"]/a/text()'
            ).extract_first()
            self.logger.debug(f"current product name is: {product_name}")
            item['product_name'] = product_name.strip()
            url = product.xpath(
                './/h5[@class="feed-block-title"]/a/@href'
            ).extract_first()
            self.logger.info(f"first ten product url: {url}")
            yield scrapy.Request(url, meta={'item': item}, callback=self.parse_details)
    def parse_details(self, response):
        item = response.meta['item']
        comments = response.xpath(
            '//*[@id="commentTabBlockNew"]/ul[@class="comment_listBox"]/li[@class="comment_list"]'
        )
        self.logger.info(f"{len(comments)} comments on current page")
        for comment in comments:
            user_name = comment.xpath(
                './div[@class="comment_conBox"]/div[@class="comment_avatar_time "]/a/span/text()'
            ).extract_first()
            user_comment = "".join(comment.xpath(
                './div[@class="comment_conBox"]/div[@class="comment_conWrap"]/div/p/span/text()'
            ).extract())
            self.logger.debug(f"-----------------{user_name} said: {user_comment}-----------------")
            item['user_name'] = user_name.strip()
            item['user_comment'] = user_comment.strip()
            yield item
        next_page = response.xpath(
            '//*[@id="commentTabBlockNew"]/ul[@class="pagination"]/li[@class="pagedown"]/a/@href'
        ).extract_first()
        if next_page:
            self.logger.info(f"next page url is: {next_page}")
            yield scrapy.Request(next_page, meta={'item': item}, callback=self.parse_details)
