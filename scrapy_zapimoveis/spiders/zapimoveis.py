import scrapy
import re


class ZapimoveisSpider(scrapy.Spider):
    name = "zapimoveis"
    allowed_domains = ["www.vivareal.com.br"]
    start_urls = ["https://www.vivareal.com.br/venda/sp/ribeirao-preto/"]

    def parse(self, response):
        # command to save return in csv file scrapy crawl zapimoveis -O zapimoveis.csv
        cards = response.xpath('//a[@class="property-card__content-link js-card-title"]')
        for card_content in cards:
            yield {
                'area': card_content.xpath('.//div/ul[1]/li[1]/span[1]//text()').get()[1:-1],
                'rooms': card_content.xpath('.//div/ul[1]/li[2]/span[1]//text()').get()[1:-1],
                'bathrooms': card_content.xpath('.//div/ul[1]/li[3]/span[1]//text()').get()[1:-1],
                'parking_spaces': card_content.xpath('.//div/ul[1]/li[4]/span[1]//text()').get()[1:-1],
                'title': card_content.xpath('.//div/h2[1]/span[1]//text()').get()[1:-1],
                'address': card_content.xpath('.//div/h2[1]/span[2]/span[1]//text()').get(),
                'sell_value': card_content.xpath('.//div/section/div/p//text()').get(),
                'amenities': card_content.xpath('.//div/ul[2]/li//text()').extract()
            }

        # add 1 to the parameter "pagina" at the end of url to search for next page.
        if(response.request.to_dict()['url'] == 'https://www.vivareal.com.br/venda/sp/ribeirao-preto/'):
            current_page = 0
        else:
            current_page = re.findall(r'\d+', response.request.to_dict()['url'])[0]
        next_page = int(current_page) + 1
        if(next_page <= 100 & response.status != 404):
            next_page_url = 'https://www.vivareal.com.br/venda/sp/ribeirao-preto/?pagina=' + next_page + '#onde=Brasil,S%C3%A3o%20Paulo,Ribeir%C3%A3o%20Preto,,,,,,BR%3ESao%20Paulo%3ENULL%3ERibeirao%20Preto,,,'
            yield scrapy.Request(url=next_page_url, callback=self.parse)

        pass
