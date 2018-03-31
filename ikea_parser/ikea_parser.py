# -*- coding: utf-8 -*-
from .models import *
from bs4 import BeautifulSoup

import requests
import os
import pathlib
from django.shortcuts import get_list_or_404
import time
from django.utils.timezone import datetime

#selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

from .create_identificator import create_identificator

import re

from app.settings import MEDIA_ROOT, BASE_DIR


#main url http://www.ikea.com/pl/pl/catalog/allproducts/

# categories_dict = {
#   'category_title': [ [sub_category_title, sub_category_url], [sub_category_title, sub_category_url] ],
#   'category_title': [ [sub_category_title, sub_category_url], [sub_category_title, sub_category_url] ],
# }

DOMAIN = 'http://www.ikea.com'

#парсинг категорий, подкатегорий
def parse_categories_():
    main_page = 'http://www.ikea.com/pl/pl/'
    domain = 'http://www.ikea.com'
    categories_dict = {}

    # categories_dict = {
    #                   'category_title_1': [ ['subcategory_title_1', 'subcategory_url_1'], ['subcategory_title_2', 'subcategory_url_2'] ]
    # }

    print(len(Product.objects.all()))
    # основнов парсер
    html = requests.get(main_page).text
    soup_main_object = BeautifulSoup(html, 'lxml')
    categories = soup_main_object.find('ul', class_='header-nav-sublist').find_all('li',
                                                                                   class_='header-nav-sublist-title')
    for category in categories:
        subcategories_list = []
        category_title = re.sub('\s+', ' ', category.find('a').text.strip())
        # create category if not exist
        try:
            category_created = Category.objects.get(title=category_title)
        except Category.DoesNotExist:
            category_created = Category.objects.create(title=category_title)
        subcategories_containers = category.find_all('div', class_='col-3')
        for subcategories_container in subcategories_containers:
            subcategories = subcategories_container.find_all('li')
            subcategories_list = []
            for subcategory in subcategories:
                subcategory_title = re.sub('\s+', ' ', subcategory.find('a').text.strip())
                subcategory_url = 'http://' + subcategory.find('a').get('href')[2:]
                # создание подкатегории если не найдена
                try:
                    subcategory_created = SubCategory.objects.get(title=subcategory_title, category=category_created)
                except SubCategory.DoesNotExist:
                    subcategory_created = SubCategory.objects.create(title=subcategory_title, url_ikea=subcategory_url,
                                                                     category=category_created, unique_identificator=create_identificator(8))
                #проверка на наличие подподкатегории
                subcategory_request = requests.get(subcategory_url).text
                subcategory_soup = BeautifulSoup(subcategory_request, 'lxml')
                classes_to_find_sub_subcategories = ['row-first row', 'row-second row']
                for class_to_find_sub_subcategory in classes_to_find_sub_subcategories:
                    sub_subcategories_container = subcategory_soup.find('div', class_=class_to_find_sub_subcategory)
                    if sub_subcategories_container == []:
                        sub_subcategories_container = None

                    if sub_subcategories_container is not None:
                        sub_subcategories = sub_subcategories_container.find_all('div', class_='img-slot')
                        if sub_subcategories == []:
                            sub_subcategories = None
                        if sub_subcategories is not None:
                            print(sub_subcategories)
                            print('YES " %s " ' % subcategory_url)
                            subcategory_created.have_sub_subcategory = True
                            subcategory_created.save()
                            for sub_subcategory in sub_subcategories:
                                sub_subcategory_title = re.sub('\s+', ' ', sub_subcategory.find('a').text.strip())
                                sub_subcategory_url = sub_subcategory.find('a').get('href')
                                try:
                                    SubSubCategory.objects.get(title=sub_subcategory_title, subcategory=subcategory_created)
                                except:
                                    SubSubCategory.objects.create(subcategory=subcategory_created, title=sub_subcategory_title,
                                                                  url_ikea=sub_subcategory_url, unique_identificator=create_identificator(8))
                    else:
                        pass
                        #print('$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        #print('Податегория " %s " не имеет под подкатегорий' % subcategory_url)
                        #print('$$$$$$$$$$$$$$$$$$$$$$$$$$')

                one_subcategory_list = [subcategory_title, subcategory_url]
                subcategories_list.append(one_subcategory_list)
        categories_dict[category_title] = subcategories_list
    return categories_dict

#парсинг артикулов (+артикул, ссылка, название, короткое описание, цена, наличие в Люблине)
#return products_dict = {
#                       'subcategory_title1': [product_article1, product_article2, ...],
#                       'subcategory_title2': [product_article3, product_article4, ...]
#                        }

def get_sub_and_sub_subcategories():
    # parse products
    try:
        subcategories = SubCategory.objects.all()
    except SubCategory.DoesNotExist:
        return FileExistsError

    for subcategory in subcategories:
        url_for_parse = ''
        if subcategory.have_sub_subcategory:
            sub_subcategories = SubSubCategory.objects.filter(subcategory=subcategory)
            for sub_subcategory in sub_subcategories:
                sub_subcategory_url = sub_subcategory.url_ikea
                sub_subcategory_title = sub_subcategory.title
                url_for_parse = sub_subcategory_url
                subcategory_status = False
                sub_subcategory_status = True
                parse_products_articles_(sub_subcategory, subcategory_status, sub_subcategory_status)
        else:
            subcategory_url = subcategory.url_ikea
            subcategory_title = subcategory.title
            url_for_parse = subcategory_url
            subcategory_status = True
            sub_subcategory_status = False
            parse_products_articles_(subcategory, subcategory_status, sub_subcategory_status)

#парсинг артикулов и основной информации к ним (название, краткое описание, цена)
def parse_products_articles_(query, subcategory_status, sub_subcategory_status):
    created_products_list = []
    iter_category_products_number = 0
    foreign_key_query = query
    create_product = True


    parsed_url = requests.get(foreign_key_query.url_ikea).text
    soup_subcategory = BeautifulSoup(parsed_url, 'lxml')
    products = soup_subcategory.find_all('div', class_='product')
    for product in products:
        create_product = True
        product_article = product.get('id').split('_')[1]

        #проверка на наличие в БД запрашуемого артикула
        if subcategory_status:
            try:
                Product.objects.get(subcategory=query, article_number=product_article)
                create_product = False
                print('Артикула под номером %s был найден в БД и не будет перезаписываться' % product_article)
            except Product.DoesNotExist:
                pass
        if sub_subcategory_status:
            try:
                Product.objects.get(sub_subcategory=query, article_number=product_article)
                created_product = False
                print('Артикула под номером %s был найден в БД и не будет перезаписываться' % product_article)
            except Product.DoesNotExist:
                pass

        if create_product:
            # available in Lublin
            product_available_url = 'http://www.ikea.com/pl/pl/iows/catalog/availability/%s/' % (
                product_article)

            product_request = requests.get(product_available_url).text
            product_page = BeautifulSoup(product_request, 'xml')
            try:
                available = product_page.find('localStore', buCode='311').find('availableStock').get_text()
            except AttributeError:
                available = 0
            product_detail = product.find('div', class_='productDetails')
            product_url = DOMAIN + product_detail.find('a').get('href')
            product_title = product_detail.find('span', class_='productTitle').text.strip()  # название
            product_description = product_detail.find('span',
                                                      class_='productDesp').text.strip()  # разшифровка
            product_price = product_detail.find('span', class_='regularPrice').text.split()[:2]
            if product_price[1] == 'PLN':
                product_price = product_price[0]
            product_price = ''.join(product_price)
            for symbol in product_price:
                if symbol == ' ':
                    product_price = ''.join(product_price.split(' '))
            for symbol in product_price:
                if symbol == ',':
                    product_price = '.'.join(product_price.split(','))
            product_unit = product_detail.find('span', class_='unit')  # /шт.
            if product_unit is not None:
                product_unit = product_unit.text.strip()
            else:
                product_unit = ''

            # create Product
            #если продукт находится в подкатегории
            if subcategory_status:
                created_product = Product.objects.create(article_number=product_article, title=product_title,
                                       description=product_description, price=float(product_price),
                                       subcategory=foreign_key_query, url_ikea=product_url, available=available,
                                       unique_identificator=create_identificator(8))
                iter_category_products_number+=1
            #если продукт находится в под подкатегории
            elif sub_subcategory_status:
                subcategory = foreign_key_query.subcategory
                created_product = Product.objects.create(article_number=product_article, title=product_title,
                                       description=product_description, price=float(product_price),
                                       subcategory=subcategory, sub_subcategory=foreign_key_query,
                                       url_ikea=product_url, available=available, unique_identificator=create_identificator(8))
                iter_category_products_number += 1
            created_products_list.append(created_product)

    print('В подкатегории/под подкатегории "%s"найдено и загруженно %i уртикулов' % (foreign_key_query.title, iter_category_products_number))
    return created_products_list

#парсинг изображений, основной информации к артикулу
def parse_one_product_information_(product_query, browser_driver):

    time_start = time.time()
    product_to_save = Product.objects.get(id=product_query.id)
    product_url = product_query.url_ikea

    driver = browser_driver
    driver.get(product_url)
    html = driver.page_source
    product_soup = BeautifulSoup(html, 'lxml')

    # -----------------------------------------------------#
    # technical information - основная информация
    key_feautures = product_soup.find('div', id='custBenefit').text
    good_to_know = product_soup.find('div', id='goodToKnowPart').find('div', id='goodToKnow').text
    care_instructions = product_soup.find('div', id='careInstructionsPart').find('div', id='careInst').text

    # -----------------------------------------------------#
    # габариты
    dimension_to_save = ''
    try:
        dimensions_parsed = product_soup.find('div', id='productDimensionsContainer').find('div', id='metric').contents
        dimensions_list = []
        for string in dimensions_parsed:
            if isinstance(string, str):
                dimensions_list.append(string)
        dimension_to_save = '.'.join(dimensions_list)
    except TypeError or AttributeError:
        pass

    # -----------------------------------------------------#
    # вариации цвета
    # проверка на наличие блока с цветами
    parse_colors = True
    color_articles_list = []
    existed_colors_on_page = []
    colors = []
    color_options = ''

    # bs4
    try:
        colors = product_soup.find('div', id='selectionDropDownDiv1').find_all('li')
    except:
        parse_colors = False
    if parse_colors:
        existed_colors_on_page = []  # уже найденные цвета
        for color in colors:
            color_identificator = color.get('data-value')
            if color_identificator not in existed_colors_on_page:
                existed_colors_on_page.append(color_identificator)

        for color_identificator_for_parse in existed_colors_on_page:
            button_for_open_colors_options = driver.find_element_by_id('selectionDropDownDiv1')
            button_for_open_colors_options.click()
            one_color_button = driver.find_element_by_xpath(
                '//li[@data-value="' + color_identificator_for_parse + '"]')
            one_color_button.click()
            one_color_url = driver.current_url.split('#')[1][1:]
            color_articles_list.append(one_color_url)
        color_options = '#'.join(color_articles_list)

    # -----------------------------------------------------#
    # more models - модели
    parse_models = True
    models_articles_list = []
    models_to_save = ''
    models = None
    try:
        models = product_soup.find('div', id='selectMoremodelsWrapper').find_all('li')
    except:
        parse_models = False

    if parse_models:
        for model in models:
            models_article = model.get('data-url').strip().split('/')[-1]
            models_articles_list.append(models_article)
        if len(models_articles_list) != 0:
            models_to_save = '#'.join(models_articles_list)
            parseComplementaryProducts(product_query, *models_articles_list)

    # -----------------------------------------------------#
    # complamantary products - дополняющие продукты
    complementary_products_list = []
    complementary_product_to_save = ''
    complementary_products_block = product_soup.find('div', id='complementaryProductContainer')
    complementary_products = complementary_products_block.find_all('li')
    for complementary_product in complementary_products:
        complementary_product_article = complementary_product.get('id').split('_')[1]
        complementary_products_list.append(complementary_product_article)
    print('Количество дополняющих продуктов %i' % len(complementary_products_list))
    if len(complementary_products_list) != 0:
        complementary_product_to_save = '#'.join(complementary_products_list)
        parseComplementaryProducts(product_query, *complementary_products_list)

    # -----------------------------------------------------#
    # environment materials - материалы
    environment_button = driver.find_element_by_id('envAndMatTab')
    environment_button.click()
    html = driver.page_source
    product_soup = BeautifulSoup(html, 'lxml')
    materials = product_soup.find('div', id='custMaterials').text.strip()

    # -----------------------------------------------------#
    #saving product
    product_to_save.key_feautures = key_feautures
    product_to_save.good_to_know = good_to_know
    product_to_save.care_instructions = care_instructions
    product_to_save.materials_info = materials
    product_to_save.complementary_products = complementary_product_to_save
    product_to_save.color_options = color_options
    product_to_save.additional_models = models_to_save
    product_to_save.dimensions = dimension_to_save
    product_to_save.is_parsed = True
    product_to_save.save()

    # -----------------------------------------------------#
    # images 500*500px
    xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + product_query.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
    xml_request = requests.get(xml_product_url).text
    xml_soup = BeautifulSoup(xml_request, 'xml')
    images_500 = xml_soup.find('large').find_all('image')
    prefix_for_500px = '500px'
    added_images_prefixes = []
    for image in images_500:
        start_download = True
        ikea_image_prefix = image.text.split('_')[2]  # префикс номера изображения в икеа
        if ikea_image_prefix not in added_images_prefixes:
            # проверка на наличие изображения в базе данных
            existed_images = ProductImage.objects.all()
            for existed_image in existed_images:
                if existed_image.title.split('_')[1] == ikea_image_prefix \
                        and existed_image.title.split('_')[0] == product_to_save.article_number \
                        and product_to_save == existed_image.product:
                    existed_image.product.add(product_to_save)
                    start_download = False
                    print('Изображение с названием %s к артикулу номер %s уже найдено. БЫЛА ДОБАВЛЕННА СВЯЗЬ!' % (
                    existed_image.title, product_to_save.article_number))

            if start_download:
                image_request = requests.get(image.text).content
                image_title = product_to_save.article_number + '_' + ikea_image_prefix + '_' + prefix_for_500px + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/500px/' + image_title
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/500px/' + image_title, title=image_title,
                                                size=500).product.add(product_to_save)
                    added_images_prefixes.append(
                        ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                    # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений

    # -----------------------------------------------------#
    # images 250*250px
    xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + product_query.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
    xml_request = requests.get(xml_product_url).text
    xml_soup = BeautifulSoup(xml_request, 'xml')
    images_250 = xml_soup.find('normal').find_all('image')
    prefix_for_250px = '250px'
    added_images_prefixes = []
    for image in images_250:
        start_download = True
        ikea_image_prefix = image.text.split('/')[-1].split('_')[0]  # префикс номера изображения в икеа
        if ikea_image_prefix not in added_images_prefixes:
            # проверка на наличие изображения в базе данных
            existed_images = ProductImage.objects.all()
            for existed_image in existed_images:
                if existed_image.title.split('_')[1] == ikea_image_prefix \
                        and existed_image.title.split('_')[0] == product_to_save.article_number \
                        and product_to_save == existed_image.product:
                    existed_image.product.add(product_to_save)
                    start_download = False
                    print('Изображение с названием %s к артикулу номер %s уже найдено. БЫЛА ДОБАВЛЕННА СВЯЗЬ!' % (
                        existed_image.title, product_to_save.article_number))

            if start_download:
                image_request = requests.get(image.text).content
                image_title = product_to_save.article_number + '_' + ikea_image_prefix + '_' + prefix_for_250px + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/250px/' + image_title
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/250px/' + image_title, title=image_title,
                                                size=250).product.add(product_to_save)
                added_images_prefixes.append(
                    ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений

    time_end = time.time()
    delta = time_end - time_start

    product_dict = {
        'article_number':product_to_save.article_number,
        'unique_identificator':product_to_save.unique_identificator,
        'subcategory':product_to_save.subcategory,
        'sub_subcategory':product_to_save.sub_subcategory,
        'url_ikea':product_to_save.url_ikea,
        'complementary_products':product_to_save.complementary_products,
        'additional_models':product_to_save.additional_models,
        'color_options':product_to_save.color_options,
        'is_parsed':product_to_save.is_parsed,
        'parse_later':product_to_save.parse_later,
        'parsed_time':delta,
    }

    print(product_dict)
    return product_to_save


#парсинг дополняющих артикулов - парсит всю информацию, НО НЕ ПАРСИТ ИНОФРМАЦИЮ ОБ ДОПОЛНЯЮЩИХ АРТИКУЛАХ К ЗАДАННЫМ АРТИКУЛАМ
#статус дополняющего артикула остается is_parsed=False для того, чтоб артикул в дальнейшем смог парсится в случае не достающей информации

def parseComplementaryProducts(parent_product, *complementary_products_list):
    print('---------ПАРСИНГ ДОПОЛНЯЮЩИХ АРТИКУЛОВ К %s НАЧАЛСЯ---------' % parent_product.article_number)
    # 1
    start_parse = time.time()
    created_product = None
    create_product = True
    available = 0

    #удаляем из списка эллементы которые уже существуют в БД
    complementary_products_articles_not_existed = []
    for complementary_product in complementary_products_list:
        try:
            Product.objects.get(article_number=complementary_product, is_parsed=True)
        except Product.DoesNotExist:
            try:
                Product.objects.get(article_number=complementary_product, is_parsed=False, parse_later=False)
            except Product.DoesNotExist:
                try:
                    Product.objects.get(article_number=complementary_product, is_parsed=False, parse_later=True)
                except Product.DoesNotExist:
                    complementary_products_articles_not_existed.append(complementary_product)

    print('СПИСОК ДОПОЛНЯЮЩИХ ПРОДУКТОВ К ПАРСИНГУ ', complementary_products_articles_not_existed)
    if len(complementary_products_articles_not_existed) != 0:

        from selenium.webdriver.chrome.options import Options
        from selenium import webdriver
        #обязательные настройки для запуска хрома без экрана
        options = Options()
        options.add_argument("--headless")
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(chrome_options=options)

        for complementary_product in complementary_products_articles_not_existed:
            product_article = complementary_product

            # available in Lublin - наличие в Люблине
            product_available_url = 'http://www.ikea.com/pl/pl/iows/catalog/availability/%s/' % (
                product_article)
            product_request = requests.get(product_available_url).text
            product_page = BeautifulSoup(product_request, 'xml')
            available = product_page.find('localStore', buCode='311').find('availableStock').get_text()
            # web driver
            product_url = 'https://www.ikea.com/pl/pl/catalog/products/%s/' % product_article
            driver.get(product_url)
            html = driver.page_source
            product_soup = BeautifulSoup(html, 'lxml')

            product_title = product_soup.find('span', id='name').text.strip()  # название
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

            #-----------------------------------------------------#
            # technical information - основная информация
            key_feautures = product_soup.find('div', id='custBenefit').text
            good_to_know = product_soup.find('div', id='goodToKnowPart').find('div', id='goodToKnow').text
            care_instructions = product_soup.find('div', id='careInstructionsPart').find('div',
                                                                                         id='careInst').text
            #-----------------------------------------------------#
            # габариты
            dimensions_parsed = product_soup.find('div', id='productDimensionsContainer').find('div',
                                                                                               id='metric').contents
            dimensions = []

            # -----------------------------------------------------#
            # вариации цвета
            # проверка на наличие блока с цветами
            parse_colors = True
            color_articles_list = []
            existed_colors_on_page = []
            colors = []
            color_options_to_save = ''

            # bs4
            try:
                colors = product_soup.find('div', id='selectionDropDownDiv1').find_all('li')
                print('ЕСТЬ ЦВЕТА')
            except:
                print('НЕТУ ЦВЕТОВ')
                parse_colors = False
            if parse_colors:
                existed_colors_on_page = []  # уже найденные цвета
                for color in colors:
                    color_identificator = color.get('data-value')
                    if color_identificator not in existed_colors_on_page:
                        existed_colors_on_page.append(color_identificator)

                for color_identificator_for_parse in existed_colors_on_page:
                    button_for_open_colors_options = driver.find_element_by_id('selectionDropDownDiv1')
                    button_for_open_colors_options.click()
                    one_color_button = driver.find_element_by_xpath(
                        '//li[@data-value="' + color_identificator_for_parse + '"]')
                    one_color_button.click()
                    one_color_url = driver.current_url.split('#')[1][1:]
                    color_articles_list.append(one_color_url)
                color_options_to_save = '#'.join(color_articles_list)

            # -----------------------------------------------------#
            # complamantary products - дополняющие продукты
            complementary_products_list = []
            complementary_products_block = product_soup.find('div', id='complementaryProductContainer')
            complementary_products = complementary_products_block.find_all('li')
            for complementary_product in complementary_products:
                complementary_product_article = complementary_product.get('id').split('_')[1]
                complementary_products_list.append(complementary_product_article)
            complementary_products_to_save = '#'.join(complementary_products_list)

            # -----------------------------------------------------#
            # more models - модели
            parse_models = True
            models_articles_list = []
            models = None
            models_to_save = ''
            try:
                models = product_soup.find('div', id='selectMoremodelsWrapper').find_all('li')
                print('ЕСТЬ МОДЕЛИ')
            except:
                parse_models = False
                print('НЕТУ МОДЕЛЕЙ')

            if parse_models:
                for model in models:
                    models_article = model.get('data-url').strip().split('/')[-1]
                    models_articles_list.append(models_article)
                if len(models_articles_list) != 0:
                    models_to_save = '#'.join(models_articles_list)

            # -----------------------------------------------------#
            # environment materials - материалы
            environment_button = driver.find_element_by_id('envAndMatTab')
            environment_button.click()
            html = driver.page_source
            product_soup = BeautifulSoup(html, 'lxml')
            materials = product_soup.find('div', id='custMaterials').text.strip()

            # -----------------------------------------------------#
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
                                                     color=product_color,
                                                     color_options=color_options_to_save,
                                                     additional_models=models_to_save,
                                                     is_parsed=False,
                                                     parse_later=True)
            print('Артикул %s был успешно сохранен в БД под id = %i' % (
            created_product.article_number, created_product.id))

            # -----------------------------------------------------#
            # images 500*500px
            xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + created_product.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
            xml_request = requests.get(xml_product_url).text
            xml_soup = BeautifulSoup(xml_request, 'xml')
            images_500 = xml_soup.find('large').find_all('image')
            prefix_for_500px = '500px'
            for image in images_500:
                start_download = True
                ikea_image_prefix = image.text.split('_')[2]  # префикс номера изображения в икеа

                # проверка на наличие изображения в базе данных
                existed_images = ProductImage.objects.all()
                for existed_image in existed_images:
                    if existed_image.title.split('_')[1] == ikea_image_prefix \
                            and existed_image.title.split('_')[0] == created_product.article_number \
                            and created_product.id == existed_image.product.id:
                        existed_image.product.add(created_product)
                        start_download = False
                        print(
                            'Изображение с названием %s к артикулу номер %s уже найдено. БЫЛА ДОБАВЛЕННА СВЯЗЬ!' % (
                            existed_image.title, created_product.article_number))
                # ---------------------------------------------
                if start_download:
                    image_request = requests.get(image.text).content
                    image_title = created_product.article_number + '_' + ikea_image_prefix + '_' + prefix_for_500px + '.jpg'
                    image_url_to_save = MEDIA_ROOT + 'products/500px/' + created_product.article_number + '_' + ikea_image_prefix + '_' + prefix_for_500px + '.jpg'
                    with open(image_url_to_save, 'wb') as image_file:
                        image_file.write(image_request)
                        image_file.close()
                        ProductImage.objects.create(image='products/500px/' + image_title, title=image_title).product.add(created_product)

                # -----------------------------------------------------#
                # images 250*250px
                xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + created_product.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
                xml_request = requests.get(xml_product_url).text
                xml_soup = BeautifulSoup(xml_request, 'xml')
                images_250 = xml_soup.find('normal').find_all('image')
                prefix_for_250px = '250px'
                added_images_prefixes = []
                for image in images_250:
                    start_download = True
                    ikea_image_prefix = image.text.split('/')[-1].split('_')[
                        0]  # префикс номера изображения в икеа
                    if ikea_image_prefix not in added_images_prefixes:
                        # проверка на наличие изображения в базе данных
                        existed_images = ProductImage.objects.all()
                        for existed_image in existed_images:
                            if existed_image.title.split('_')[1] == ikea_image_prefix \
                                    and existed_image.title.split('_')[0] == created_product.article_number \
                                    and created_product == existed_image.product:
                                existed_image.product.add(created_product)
                                start_download = False
                                print(
                                    'Изображение с названием %s к артикулу номер %s уже найдено. БЫЛА ДОБАВЛЕННА СВЯЗЬ!' % (
                                        existed_image.title, created_product.article_number))

                        if start_download:
                            image_request = requests.get(image.text).content
                            image_title = created_product.article_number + '_' + ikea_image_prefix + '_' + prefix_for_250px + '.jpg'
                            image_url_to_save = MEDIA_ROOT + 'products/250px/' + image_title
                            with open(image_url_to_save, 'wb') as image_file:
                                image_file.write(image_request)
                                image_file.close()
                                ProductImage.objects.create(image='products/250px/' + image_title,
                                                            title=image_title,
                                                            size=250).product.add(created_product)
                            added_images_prefixes.append(
                                ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                            # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений

            #закрываем старую вкладку и открываем новую
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'T', Keys.CONTROL + Keys.TAB, Keys.CONTROL + 'W')
        print('-----------ПАРСИНГ ДОПОЛНЯЮЩИХ АРТИКУЛОВ ЗАВЕРШЕН')
        driver.close()

    end_parse = time.time()
    print(start_parse - end_parse)
    return created_product


def translate(category=None, subcategory=None, product=None):
    parsed_domain = 'https://ikea-club.com.ua/ua/'
    try:
        products = Product.objects.filter(is_translated=False)
    except Product.DoesNotExist:
        return FileExistsError

    for product in products:
        request = requests.get(parsed_domain + product.article_number).text
        product_soup = BeautifulSoup(request, 'lxml')













