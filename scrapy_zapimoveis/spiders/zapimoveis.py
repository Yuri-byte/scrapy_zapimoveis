import scrapy
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class ZapimoveisSpider(scrapy.Spider):
    name = "zapimoveis"
    allowed_domains = ["www.zapimoveis.com.br"]
    start_urls = ["https://www.zapimoveis.com.br/venda/imoveis/sp+ribeirao-preto/?transacao=venda&onde=,S%C3%A3o%20Paulo,Ribeir%C3%A3o%20Preto,,,,,city,BR%3ESao%20Paulo%3ENULL%3ERibeirao%20Preto,-18.912775,-48.275523,&pagina=1"]

    def star_requests(self):
        url = "https://www.zapimoveis.com.br/venda/imoveis/sp+ribeirao-preto/?transacao=venda&onde=,S%C3%A3o%20Paulo,Ribeir%C3%A3o%20Preto,,,,,city,BR%3ESao%20Paulo%3ENULL%3ERibeirao%20Preto,-18.912775,-48.275523,&pagina=1"
        yield scrapy.Request(url, self.parse)

    async def parse(self, response):
        # command to save return in csv file scrapy crawl zapimoveis -O zapimoveis.csv
        # Initialize a Selenium WebDriver
        driver = webdriver.Chrome()
        driver.get(response.url)

        # Scroll down to load more content
        current_scroll_position = driver.execute_script("return window.scrollY")
        current_page_height = driver.execute_script("return document.body.scrollHeight")
        i = 1
        while current_scroll_position + driver.execute_script("return window.innerHeight") <  current_page_height:
            scroll_distance = i * 500
            scroll_down(driver, scroll_distance)
            current_scroll_position = driver.execute_script("return window.scrollY")
            current_page_height = driver.execute_script("return document.body.scrollHeight")
            i += 1

        # Now, extract data using Scrapy selectors       
        list_of_cards = driver.find_element(By.XPATH, '//div[@class="listing-wrapper__content"]')
        cards = list_of_cards.find_elements(By.XPATH, './/div[@class="l-card__content"]')
        for card_content in cards:
            count_elements = 1
            area = ''
            try:
                element = card_content.find_element(By.XPATH, './/section/p[@itemprop="floorSize"]')
                area = element.text
                count_elements += 1
            except NoSuchElementException:
                pass
            rooms = ''
            try:
                element = card_content.find_element(By.XPATH, './/section/p[@itemprop="numberOfRooms"]')
                rooms = element.text
                count_elements += 1
            except NoSuchElementException:
                pass
            bathrooms = ''
            try:
                element = card_content.find_element(By.XPATH, './/section/p[@itemprop="numberOfBathroomsTotal"]')
                bathrooms = element.text
                count_elements += 1
            except NoSuchElementException:
                pass
            parking_spaces = ''
            try:
                element = card_content.find_element(By.XPATH, f'.//section/p[{count_elements}]')
                parking_spaces = element.text
            except NoSuchElementException:
                pass
            neighbourhood_city = ''
            try:
                element = card_content.find_element(By.XPATH, './/div[1]/section/div/h2')
                neighbourhood_city = element.text
            except NoSuchElementException:
                pass
            street = ''
            try:
                element = card_content.find_element(By.XPATH, './/div[1]/section/p')
                street = element.text
            except NoSuchElementException:
                pass
            title = ''
            try:
                element = card_content.find_element(By.XPATH, './/div[2]/p')
                title = element.text
            except NoSuchElementException:
                pass
            sell_value = ''
            try:
                element = card_content.find_element(By.XPATH, './/div[@class="result-card__wrapper"]/div[1]/p[1]')
                sell_value = element.text
            except NoSuchElementException:
                pass
            yield {
                'area': area,
                'rooms': rooms,
                'bathrooms': bathrooms,
                'parking_spaces': parking_spaces,
                'title': title,
                'neighbourhood_city': neighbourhood_city,
                'street': street,
                'sell_value': sell_value,
            }

        # Close the browser
        driver.quit()

        # add 1 to the parameter "pagina" at the end of url to search for next page.
        if response.request.url == 'https://www.zapimoveis.com.br/venda/imoveis/sp+ribeirao-preto/?transacao=venda&onde=,S%C3%A3o%20Paulo,Ribeir%C3%A3o%20Preto,,,,,city,BR%3ESao%20Paulo%3ENULL%3ERibeirao%20Preto,-18.912775,-48.275523,&pagina=1':
            current_page = 1
        else:
            current_page = re.findall(r'\d+', response.request.url)[-1]
        next_page = int(current_page) + 1
        if next_page <= 100 and response.status != 404:
            next_page_url = f'https://www.zapimoveis.com.br/venda/imoveis/sp+ribeirao-preto/?transacao=venda&onde=,S%C3%A3o%20Paulo,Ribeir%C3%A3o%20Preto,,,,,city,BR%3ESao%20Paulo%3ENULL%3ERibeirao%20Preto,-18.912775,-48.275523,&pagina={next_page}'
            yield scrapy.Request(url=next_page_url, callback=self.parse)

        pass

def scroll_down(driver, scroll_distance):
    driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
    time.sleep(0.5)