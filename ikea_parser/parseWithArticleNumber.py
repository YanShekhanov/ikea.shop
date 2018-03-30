import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from .ikea_parser import parseComplementaryProducts
from app.settings import MEDIA_ROOT
from .models import *

from selenium.webdriver.firefox.options import Options

#------------------1. Доделать добавление категории и подкатегории к продукту который будет парситься
#------------------2. Доделать парсинг моделей, габаритов данного артикула
#------------------3. Реализовать скачивание изображений размером 200px
#------------------4. Перенести все на автоматический парсер всех артикулов

#парсинг одного артикула по номеру
#если parse_complementary = False, то не парсим дополняющие продукты, только записываем их артикулы в БД
def parseOneProductInformationWithArticleNumber(article_number, parse_complementary=True):

    #1
    start_parse = time.time()
    created_product = None
    create_product = True
    available = 0
    product_article = article_number

    if create_product:
        # available in Lublin
        product_available_url = 'http://www.ikea.com/pl/pl/iows/catalog/availability/%s/' % (
            product_article)

        product_request = requests.get(product_available_url).text
        product_page = BeautifulSoup(product_request, 'xml')
        available = product_page.find('localStore', buCode='311').find('availableStock').get_text()
        #web driver
        product_url = 'https://www.ikea.com/pl/pl/catalog/products/%s/' % product_article

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(firefox_options=options)
        driver.get(product_url)
        html = driver.page_source
        product_soup = BeautifulSoup(html, 'lxml')

        product_title = product_soup.find('span', id='name').text.strip()# название
        product_description = product_soup.find('span', id='type').text.strip()  # разшифровка
        product_color = product_description.split(',')[1]
        product_price = product_soup.find('span', class_='packagePrice').text.split()[:2]
        if product_price[1] == 'PLN':
            product_price = product_price[0]
        product_price = ''.join(product_price)
        for symbol in product_price:
            if symbol == ' ':
                product_price = ''.join(product_price.split(' '))
        for symbol in product_price:
            if symbol == ',':
                product_price = '.'.join(product_price.split(','))
        product_unit = product_soup.find('span', class_='unit')  # /шт.
        if product_unit is not None:
            product_unit = product_unit.text.strip()
        else:
            product_unit = ''

        # technical information - основная информация
        key_feautures = product_soup.find('div', id='custBenefit').text
        good_to_know = product_soup.find('div', id='goodToKnowPart').find('div', id='goodToKnow').text
        care_instructions = product_soup.find('div', id='careInstructionsPart').find('div',
                                                                                     id='careInst').text

        # габариты
        dimensions_parsed = product_soup.find('div', id='productDimensionsContainer').find('div',
                                                                                           id='metric').contents
        dimensions = []

        ########################## НЕ РАБОТАЮЩИЙ ГОВНОКОД СУКА

        # вариации цвета
        # проверка на наличие блока с цветами
        parse_colors = True
        color_articles_list = []
        existed_colors_on_page = []
        colors = []

        #bs4
        try:
            colors = product_soup.find('div', id='selectionDropDownDiv1').find_all('li')
            print('ЕСТЬ ЦВЕТА')
        except:
            print('НЕТУ ЦВЕТОВ')
            parse_colors = False
        if parse_colors:
            try:
                existed_colors_on_page = [] #уже найденные цвета
                for color in colors:
                    color_identificator = color.get('data-value')
                    if color_identificator not in existed_colors_on_page:
                        existed_colors_on_page.append(color_identificator)

                for color_identificator_for_parse in existed_colors_on_page:
                    button_for_open_colors_options = driver.find_element_by_id('selectionDropDownDiv1')
                    button_for_open_colors_options.click()
                    one_color_button = driver.find_element_by_xpath('//li[@data-value="' + color_identificator_for_parse +  '"]')
                    one_color_button.click()
                    one_color_url = driver.current_url.split('#')[1][1:]
                    color_articles_list.append(one_color_url)
                color_options = '#'.join(color_articles_list)
            except WebDriverException:
                parseOneProductInformationWithArticleNumber(product_article)

        # complamantary products - дополняющие продукты
        driver.find_element_by_id('complementaryProductContainer')
        complementary_products_list = []
        complementary_products_block = product_soup.find('div', id='complementaryProductContainer')
        print(complementary_products_block)
        complementary_products = complementary_products_block.find_all('li')
        for complementary_product in complementary_products:
            complementary_product_article = complementary_product.get('id').split('_')[1]
            # добавляем артикул в БД для дальнейшей загрузки
            complementary_products_list.append(complementary_product_article)
        complementary_products_to_save = '#'.join(complementary_products_list)
        print('Количество дополняющих продуктов %i' % len(complementary_products_list))
        if len(complementary_products_list) != 0:
            product_query = None
            parseComplementaryProducts(product_query, *complementary_products_list)

        # environment materials - материалы
        environment_button = driver.find_element_by_id('envAndMatTab')
        environment_button.click()
        html = driver.page_source
        product_soup = BeautifulSoup(html, 'lxml')
        materials = product_soup.find('div', id='custMaterials').text.strip()

        # saving product
        created_product = Product.objects.create(article_number=product_article,
                                                  title=product_title,
                                                  description=product_description,
                                                  price=product_price,
                                                  url_ikea=product_url,
                                                  available=available,
                                                  key_feautures=key_feautures,
                                                  good_to_know=good_to_know,
                                                  care_instructions=care_instructions,
                                                  materials_info=materials,
                                                  complementary_products=complementary_products_to_save,
                                                  color_options=color_options,
                                                  color=product_color)
        print('Артикул %s был успешно сохранен в БД под id = %i' % (created_product.article_number, created_product.id))

        # images 500*500px
        xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + created_product.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
        xml_request = requests.get(xml_product_url).text
        xml_soup = BeautifulSoup(xml_request, 'xml')
        images_500 = xml_soup.find('large').find_all('image')
        prefix_for_500px = '500px'
        for image in images_500:
            start_download = True
            ikea_image_prefix = image.text.split('_')[2]  # префикс номера изображения в икеа

            #проверка на наличие изображения в базе данных
            existed_images = ProductImage.objects.all()
            for existed_image in existed_images:
                if existed_image.title.split('_')[1] == ikea_image_prefix \
                        and existed_image.title.split('_')[0] == created_product.article_number\
                        and created_product.id == existed_image.product.id:
                    start_download = False
                    print('уже найдено')
            # ---------------------------------------------
            if start_download:
                image_request = requests.get(image.text).content
                image_title = created_product.article_number + '_' + ikea_image_prefix + '_' + prefix_for_500px + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/' + created_product.article_number + '_' + ikea_image_prefix + '_' + prefix_for_500px + '.jpg'
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/' + image_title, title=image_title).product.add(created_product)
        driver.close()
    else:
        return FileExistsError
    end_parse = time.time()
    print(start_parse - end_parse)
    return created_product
