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
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, NoSuchElementException
from .create_identificator import create_identificator
import re
from app.settings import MEDIA_ROOT, BASE_DIR


#main url http://www.ikea.com/pl/pl/catalog/allproducts/

# categories_dict = {
#   'category_title': [ [sub_category_title, sub_category_url], [sub_category_title, sub_category_url] ],
#   'category_title': [ [sub_category_title, sub_category_url], [sub_category_title, sub_category_url] ],
# }

DOMAIN = 'http://www.ikea.com'

import json
#парсинг категорий, подкатегорий
def parse_categories_():
    main_page = 'http://www.ikea.com/pl/pl/'
    domain = 'http://www.ikea.com'
    categories_dict = {}

    # categories_dict = {
    #                   'category_title_1': [ ['subcategory_title_1', 'subcategory_url_1'], ['subcategory_title_2', 'subcategory_url_2'] ]
    # }

    # основнов парсер
    html = requests.get(main_page).text
    soup_main_object = BeautifulSoup(html, 'lxml')
    categories = soup_main_object.find('ul', class_='header-nav-sublist').find_all('li', class_='header-nav-sublist-title')
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
                print(subcategory_url)
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

                #проверка на наличие подкатегорий в другом блоке
                sub_subcategories_containers = subcategory_soup.find_all('div', class_='visualNavContainer')
                if sub_subcategories_containers == []:
                    sub_subcategories_containers = None
                if sub_subcategories_containers is not None:
                    for sub_subcategory_container in sub_subcategories_containers:
                        sub_subcategory_block = sub_subcategory_container.find('a', class_='categoryName')
                        if sub_subcategory_block == []:
                            sub_subcategory_block = None
                        if sub_subcategory_block is not None:
                            subcategory_created.have_sub_subcategory = True
                            subcategory_created.save()
                            sub_subcategory_url = DOMAIN + sub_subcategory_block.get('href')
                            sub_subcategory_title = re.sub('\s+', ' ', sub_subcategory_block.text.strip())
                            try:
                                SubSubCategory.objects.get(subcategory=subcategory_created, title=sub_subcategory_title)
                            except SubSubCategory.DoesNotExist:
                                SubSubCategory.objects.create(subcategory=subcategory_created, title=sub_subcategory_title,
                                                               url_ikea=sub_subcategory_url, unique_identificator=create_identificator(8))


                one_subcategory_list = [subcategory_title, subcategory_url]
                subcategories_list.append(one_subcategory_list)
        categories_dict[category_title] = subcategories_list
    return categories_dict


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

from googletrans import Translator
from shop.models import Coef
#парсинг артикулов и основной информации к ним (название, краткое описание, цена)
def parse_products_articles_(query, subcategory_status, sub_subcategory_status):
    translator = Translator()
    created_products_list = []
    iter_category_products_number = 0
    foreign_key_query = query
    create_product = True
    existed_product = None
    with open('data/first_products.json', 'w') as data_file:
        print(foreign_key_query.url_ikea)
        parsed_url = requests.get(foreign_key_query.url_ikea).text
        soup_subcategory = BeautifulSoup(parsed_url, 'lxml')
        products = soup_subcategory.find_all('div', class_='product')
        for product in products:
            one_product_dict = {}
            create_product = True
            product_article = product.get('id').split('_')[1]

            #проверка на наличие в БД запрашуемого артикула
            if subcategory_status:
                try:
                    existed_product = Product.objects.get(article_number=product_article)
                    existed_product.subcategory.add(foreign_key_query)
                    create_product = False
                    #print('Артикула под номером %s был найден в БД и не будет перезаписываться' % product_article)
                except Product.DoesNotExist:
                    pass
            if sub_subcategory_status:
                try:
                    existed_product = Product.objects.get(article_number=product_article)
                    existed_product.subcategory.add(foreign_key_query.subcategory)
                    existed_product.sub_subcategory.add(foreign_key_query)
                    create_product = False
                    #print('Артикула под номером %s был найден в БД и не будет перезаписываться' % product_article)
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
                product_description = translator.translate(product_detail.find('span', class_='productDesp').text.strip(), dest='uk').text  # разшифровка
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
                product_price = int(round(float(product_price) * Coef.objects.all().first().coef))

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
                                           url_ikea=product_url, available=available,
                                           unique_identificator=create_identificator(8))
                    created_product.subcategory.add(foreign_key_query)
                    iter_category_products_number+=1
                #если продукт находится в под подкатегории
                elif sub_subcategory_status:
                    subcategory = foreign_key_query.subcategory
                    created_product = Product.objects.create(article_number=product_article, title=product_title,
                                           description=product_description, price=float(product_price),
                                           url_ikea=product_url, available=available,
                                           unique_identificator=create_identificator(8))
                    created_product.subcategory.add(subcategory)
                    created_product.sub_subcategory.add(foreign_key_query)
                    iter_category_products_number += 1

                #создание словаря одного продукта
                one_product_dict = {
                    'title':str(product_title.encode('utf-8')),
                    'article_number':product_article,
                    'product_availability': available,
                    'product_price':product_price,
                    'product_description':str(product_description.encode('utf-8')),
                    'product_url':product_url,
                    'subcategory':subcategory_status,
                    'sub_subcategory':sub_subcategory_status,
                    'subcategory_title':str(foreign_key_query.title.encode('utf-8')),
                    'subcategory_url':foreign_key_query.url_ikea,
                }
                json.dumps(one_product_dict, data_file, ensure_ascii=False) #запись в файл словаря одного продукта
                created_products_list.append(one_product_dict)
        data_file.close()

    #print('В подкатегории/под подкатегории "%s"найдено и загруженно %i уртикулов' % (foreign_key_query.title, iter_category_products_number))
    return created_products_list

#парсинг изображений, основной информации к артикулу
def parse_one_product_information_(product_query, browser_driver):

    translator = Translator()

    time_start = time.time()
    product_to_save = Product.objects.get(id=product_query.id)
    product_url = product_query.url_ikea

    driver = browser_driver
    driver.get(product_url)
    html = driver.page_source
    product_soup = BeautifulSoup(html, 'lxml')

    # -----------------------------------------------------#
    # technical information - основная информация
    key_feautures = None
    try:
        key_feautures = translator.translate(product_soup.find('div', id='custBenefit').text, dest='uk').text
    except AttributeError:
        key_feautures = None

    good_to_know = None
    try:
        good_to_know = translator.translate(product_soup.find('div', id='goodToKnowPart').find('div', id='goodToKnow').text, dest='uk').text
    except AttributeError:
        good_to_know = None

    care_instruction_to_save = None
    try:
        care_instructions = product_soup.find('div', id='careInstructionsPart').find('div', id='careInst').contents
        care_instructions_list = []
        for instruction in care_instructions:
            if isinstance(instruction, str):
                care_instructions_list.append(instruction)
        care_instruction_to_save = translator.translate('.'.join(care_instructions_list), dest='uk').text
    except AttributeError:
        pass

    # -----------------------------------------------------#
    # габариты
    dimension_to_save = None
    try:
        dimensions_parsed = product_soup.find('div', id='productDimensionsContainer').find('div', id='metric').contents
        dimensions_list = []
        for string in dimensions_parsed:
            if isinstance(string, str):
                dimensions_list.append(string)
        dimension_to_save = translator.translate('.'.join(dimensions_list), dest='uk').text
    except AttributeError:
        pass

    #------------------------------------------------------#
    #доп. цвета, доп. размеры
    blocks = ['selectionDropDownDiv1', 'selectionDropDownDiv2', 'selectionDropDownDiv3']
    color_options = None
    size_options = None
    for block in blocks:
        parse_colors = False
        parse_sizes = False
        try:
            options = product_soup.find('div', id=block).find_all('li')
            block_label = re.sub(':', '', product_soup.find('div', id=block).find('span', class_='categoryNameLbl').text.strip())
            #print('ЕСТЬ "%s", блок "%s"' % (block_label, block))
            button_for_open_options = driver.find_element_by_id(block) # кнопка для открытия select с цветами
            if block_label == 'kolor': # если блок называется 'kolor'
                parse_colors = True
                if len(options) <= 1:
                    parse_colors = False

            if block_label == 'rozmiar': # если блок называется 'rozmiar'
                parse_sizes = True
                if len(options) <= 1:
                    parse_sizes = False

            if parse_colors or parse_sizes:
                options_articles_list = []
                existed_options_on_page = []  # уже найденные опции
                for option in options:
                    option_identificator = option.get('data-value')
                    if option_identificator not in existed_options_on_page:
                        existed_options_on_page.append(option_identificator)

                for option_identificator_for_parse in existed_options_on_page:
                    button_for_open_options.click()
                    try:
                        one_option_button = driver.find_element_by_xpath(
                            '//li[@data-value="' + option_identificator_for_parse + '"]')
                        one_option_button.click()
                        try:
                            one_option_article_number = driver.current_url.split('#')[1][1:]
                            if one_option_article_number not in options_articles_list:
                                options_articles_list.append(one_option_article_number)
                        except IndexError:  # если ссылка не меняется, тогда берем номер артикула с страницы продукта
                            new_product_soup = driver.page_source
                            one_option_article_number = ''.join(new_product_soup.find('div', id='itemNumber').text.split('.'))
                            if one_option_article_number not in options_articles_list:
                                options_articles_list.append(one_option_article_number)
                    except WebDriverException:
                        pass
                if len(options_articles_list) != 0:
                    if parse_colors:
                        color_options = '#'.join(options_articles_list)
                        #print('Количество цветов артикула %i' % len(options_articles_list))
                    if parse_sizes:
                        size_options = '#'.join(options_articles_list)
                        #print('Количество размеров артикула %i' % len(options_articles_list))
                    parseComplementaryProducts(product_to_save, *options_articles_list)
        except:
            pass

    # -----------------------------------------------------#
    # more models - модели
    parse_models = True
    models_articles_list = []
    models_ = None
    models_to_save = None
    try:
        models_ = product_soup.find('div', id='selectMoremodelsWrapper').find_all('li')
        #print('ЕСТЬ МОДЕЛИ')
    except:
        parse_models = False
        #print('НЕТУ МОДЕЛЕЙ')

    if parse_models:
        for model in models_:
            models_article = model.get('data-url').split('/')[-2]
            if models_article not in models_articles_list:
                models_articles_list.append(models_article)
        if len(models_articles_list) != 0:
            models_to_save = '#'.join(models_articles_list)
            #print('Количество моделей продукта %i' % len(models_articles_list))
            parseComplementaryProducts(product_query, *models_articles_list)

    # -----------------------------------------------------#
    # complamantary products - дополняющие продукты
    complementary_products_list = []
    complementary_product_to_save = None
    try:
        complementary_products_block = product_soup.find('div', id='complementaryProductContainer')
        complementary_products = complementary_products_block.find_all('li')
        for complementary_product in complementary_products:
            try:
                complementary_product_article = complementary_product.get('id').split('_')[1]
                if complementary_product_article not in complementary_products_list:
                    complementary_products_list.append(complementary_product_article)
            except IndexError:
                pass
        #print('Количество дополняющих продуктов %i' % len(complementary_products_list))
        if len(complementary_products_list) != 0:
            complementary_product_to_save = '#'.join(complementary_products_list)
            parseComplementaryProducts(product_query, *complementary_products_list)
    except AttributeError:
        complementary_product_to_save = None

    # -----------------------------------------------------#
    # environment materials - материалы
    materials_to_save = None
    try:
        environment_button = driver.find_element_by_id('envAndMatTab')
        environment_button.click()
        html = driver.page_source
        product_soup = BeautifulSoup(html, 'lxml')
        materials = product_soup.find('div', id='custMaterials').contents
        materials_list = []
        for material in materials:
            if isinstance(material, str):
                materials_list.append(material)
        materials_to_save = translator.translate('. '.join(materials_list), dest='uk').text
    except NoSuchElementException:
        pass

    # -----------------------------------------------------#
    # images 500*500px
    xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + product_query.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
    xml_request = requests.get(xml_product_url).text
    xml_soup = BeautifulSoup(xml_request, 'xml')
    try:
        images_500 = xml_soup.find('large').find_all('image')
        prefix_for_500px = '500px'
        added_images_prefixes = []
        for image in images_500:
            start_download = True
            ikea_image_prefix = image.text.split('_')[2]  # префикс номера изображения в икеа
            try:
                existed_images = ProductImage.objects.filter(product=product_to_save, size=500)
                for existed_image in existed_images:
                    if existed_image.title.split('_')[1] == ikea_image_prefix:
                        start_download = False
            except ProductImage.DoesNotExist:
                pass
            if start_download:
                image_request = requests.get(image.text).content
                image_title = product_to_save.article_number + '_' + ikea_image_prefix + '_' + prefix_for_500px + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/500px/' + image_title
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/500px/' + image_title, title=image_title, size=500).product.add(product_to_save)
                    added_images_prefixes.append(ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                    # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений
    except AttributeError:
        #print('Ошибка загрузки изображения 500px')
        pass

    # -----------------------------------------------------#
    # images 250*250px
    xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + product_query.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
    xml_request = requests.get(xml_product_url).text
    xml_soup = BeautifulSoup(xml_request, 'xml')
    try:
        images_250 = xml_soup.find('normal').find_all('image')
        prefix_for_250px = '250px'
        added_images_prefixes = []
        for image in images_250:
            start_download = True
            ikea_image_prefix = image.text.split('/')[-1].split('_')[0]  # префикс номера изображения в икеа
            try:
                existed_images = ProductImage.objects.filter(product=product_to_save, size=250)
                for existed_image in existed_images:
                    if existed_image.title.split('_')[1] == ikea_image_prefix:
                        start_download = False
            except ProductImage.DoesNotExist:
                pass
            if start_download:
                image_request = requests.get(image.text).content
                image_title = product_to_save.article_number + '_' + ikea_image_prefix + '_' + prefix_for_250px + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/250px/' + image_title
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/250px/' + image_title, title=image_title, size=250).product.add(product_to_save)
                added_images_prefixes.append(ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений
    except AttributeError:
        #print('Ошибка загрузки изображения 250px')
        pass

    # -----------------------------------------------------#
    # images 2000*2000px
    xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + product_query.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
    xml_request = requests.get(xml_product_url).text
    xml_soup = BeautifulSoup(xml_request, 'xml')
    try:
        images_2000 = xml_soup.find('zoom').find_all('image')
        prefix_for_2000px = '2000px'
        added_images_prefixes = [] #изображения в xml могут повторятся и таким образом отслеживаем какие уже добавлены
        for image in images_2000:
            start_download = True
            ikea_image_prefix = image.text.split('/')[-1].split('_')[0]  # префикс номера изображения в икеа
            try:
                existed_images = ProductImage.objects.filter(product=product_to_save, size=2000)
                for existed_image in existed_images:
                    if existed_image.title.split('_')[1] == ikea_image_prefix:
                        start_download = False
            except ProductImage.DoesNotExist:
                pass
            if start_download:
                image_request = requests.get(image.text).content
                image_title = product_to_save.article_number + '_' + ikea_image_prefix + '_' + prefix_for_2000px + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/2000px/' + image_title
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/2000px/' + image_title, title=image_title, size=2000).product.add(product_to_save)
                    added_images_prefixes.append(ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                    # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений
    except AttributeError:
        #print('Ошибка загрузки изображения 2000px')
        pass

    # -----------------------------------------------------#
    # icon
    xml_product_url = 'http://www.ikea.com/pl/pl/catalog/products/' + product_query.article_number + '?type=xml&dataset=normal%2Cprices%2Callimages%2CparentCategories%2Cattributes'
    xml_request = requests.get(xml_product_url).text
    xml_soup = BeautifulSoup(xml_request, 'xml')
    try:
        images_icon = xml_soup.find('small').find_all('image')
        prefix_for_icon = 'icon'
        added_images_prefixes = []
        for image in images_icon:
            start_download = True
            ikea_image_prefix = image.text.split('/')[-1].split('_')[0]  # префикс номера изображения в икеа
            try:
                existed_images = ProductImage.objects.filter(product=product_to_save, is_icon=True)
                for existed_image in existed_images:
                    if existed_image.title.split('_')[1] == ikea_image_prefix:
                        start_download = False
            except ProductImage.DoesNotExist:
                pass
            if start_download:
                image_request = requests.get(image.text).content
                image_title = product_to_save.article_number + '_' + ikea_image_prefix + '_' + prefix_for_icon + '.jpg'
                image_url_to_save = MEDIA_ROOT + 'products/icons/' + image_title
                with open(image_url_to_save, 'wb') as image_file:
                    image_file.write(image_request)
                    image_file.close()
                    ProductImage.objects.create(image='products/icons/' + image_title, title=image_title, size=40, is_icon=True).product.add(product_to_save)
                    added_images_prefixes.append(ikea_image_prefix)  # в ИКЕА изображения повторяются, по єтому при каждой иттерации в список
                    # добавленного добавлям уникальный префикс с изображения икеа дабы избежать повторного сохранения изображений
    except AttributeError:
        #print('Ошибка загрузки иконки')
        pass

    # -----------------------------------------------------#
    # saving product
    product_to_save.key_feautures = key_feautures
    product_to_save.good_to_know = good_to_know
    product_to_save.care_instructions = care_instruction_to_save
    product_to_save.materials_info = materials_to_save
    product_to_save.complementary_products = complementary_product_to_save
    product_to_save.color_options = color_options
    product_to_save.size_options = size_options
    product_to_save.additional_models = models_to_save
    product_to_save.dimensions = dimension_to_save
    product_to_save.is_parsed = True
    product_to_save.save()

    time_end = time.time()
    delta = time_end - time_start

    '''product_dict = {
        'article_number':product_to_save.article_number,
        'unique_identificator':product_to_save.unique_identificator,
        'subcategory':product_to_save.subcategory.url_ikea,
        'sub_subcategory':product_to_save.sub_subcategory.url_ikea,
        'url_ikea':product_to_save.url_ikea,
        'complementary_products':product_to_save.complementary_products,
        'additional_models':product_to_save.additional_models,
        'color_options':product_to_save.color_options,
        'size_options':product_to_save.size_options,
        'is_parsed':product_to_save.is_parsed,
        'parse_later':product_to_save.parse_later,
        'parsed_time':delta,
    }

    file_to_write = open(os.path.join(BASE_DIR, 'data/products.json'), 'a+')
    json.dumps(product_dict, file_to_write, ensure_ascii=False)

    print(product_dict)'''
    print('%s, seconds: %s' % (product_to_save.article_number, delta))
    return product_to_save


#парсинг дополняющих артикулов - парсит всю информацию, НО НЕ ПАРСИТ ИНОФРМАЦИЮ ОБ ДОПОЛНЯЮЩИХ АРТИКУЛАХ К ЗАДАННЫМ АРТИКУЛАМ
#статус дополняющего артикула остается is_parsed=False для того, чтоб артикул в дальнейшем смог парсится в случае не достающей информации

def parseComplementaryProducts(parent_product, *complementary_products_list):
    translator = Translator()
    start_parse = time.time()
    created_product = None
    available = 0

    #удаляем из списка эллементы которые уже существуют в БД
    complementary_products_articles_not_existed = []
    for complementary_product in complementary_products_list:
        if complementary_product != '':
            try:
                Product.objects.get(article_number=complementary_product)
            except Product.DoesNotExist:
                complementary_products_articles_not_existed.append(complementary_product)

    if len(complementary_products_articles_not_existed) != 0:
        #print('СПИСОК ДОПОЛНЯЮЩИХ ПРОДУКТОВ К ПАРСИНГУ ', complementary_products_articles_not_existed)

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

            # web driver
            product_url = 'https://www.ikea.com/pl/pl/catalog/products/%s/' % product_article
            driver.get(product_url)
            html = driver.page_source
            product_soup = BeautifulSoup(html, 'lxml')

            product_title = product_soup.find('span', id='name').text.strip()  # название
            product_description = translator.translate(product_soup.find('span', id='type').text.strip(), dest='uk').text  # разшифровка
            product_color = None
            try:
                product_color = translator.translate(product_description.split(',')[1], dest='uk').text
            except IndexError:
                pass
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
            product_price = int(round(float(product_price) * Coef.objects.all().first().coef))
            product_unit = product_soup.find('span', class_='unit')  # /шт.
            if product_unit is not None:
                product_unit = product_unit.text.strip()
            else:
                product_unit = ''

            # -----------------------------------------------------#
            # saving product
            created_product = Product.objects.create(article_number=product_article,
                                                     title=product_title,
                                                     description=product_description,
                                                     price=product_price,
                                                     url_ikea=product_url,
                                                     color=product_color,
                                                     is_parsed=False,
                                                     parse_later=True,
                                                     unique_identificator=create_identificator(8))
            #print('Артикул %s был успешно сохранен в БД под id = %i' % (created_product.article_number, created_product.id))

            #закрываем старую вкладку и открываем новую
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'T', Keys.CONTROL + Keys.TAB, Keys.CONTROL + 'W')
        #print('-----------ПАРСИНГ ДОПОЛНЯЮЩИХ АРТИКУЛОВ ЗАВЕРШЕН')
        driver.close()

    end_parse = time.time()
    print(complementary_products_articles_not_existed, end_parse - start_parse)
    return created_product

#парсинг комнаты и изображений к ним
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
def parse_rooms():
    pathlib.Path(os.path.join(MEDIA_ROOT, 'rooms/')).mkdir(parents=True, exist_ok=True)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1024,768")
    options.add_argument("--no-sandbox")

    browser = webdriver.Chrome(chrome_options=options)
    url = 'https://www.ikea.com/pl/pl/'
    browser.get(url)
    html = browser.page_source
    page = BeautifulSoup(html, 'lxml')
    rooms = page.find('li', class_='menu-rooms').find_all('li')
    for room in rooms:
        one_room_dict = {}

        room_url = 'https:' + room.find('a').get('href')
        image_url = 'https:' + room.find('img').get('src')
        room_title = re.sub('"', '', room.find('a').text.strip())
        try:
            Room.objects.get(title=room_title)
        except Room.DoesNotExist:
            image_title = create_identificator(4) + '.jpg'
            Room.objects.create(image='rooms/' + image_title, title=room_title, ikea_url=room_url)
            image_page = requests.get(image_url).content
            image_file = open(MEDIA_ROOT + 'rooms/' + image_title, 'wb')
            image_file.write(image_page)
            image_file.close()

#парсинг идей комнат и изображений к ним
def parse_examples(query):
    url = query.ikea_url
    html = BeautifulSoup(requests.get(url).text, 'lxml')
    examples = html.find_all('div', class_='roomblock')
    print('___________________' + query.ikea_url)
    for example in examples:
        start_load = True
        example_url = DOMAIN + example.find('a').get('href')
        example_title = example.find('a').get('title').strip()
        example_small_image = DOMAIN + example.find('img').get('src')  # маленькое изображение
        small_image_title = example_small_image.strip().split('_')[-1].split('.')[0] + '_small.jpg'
        print(example_url)

        #парсинг артикулов одной комнаты
        example_detail_page = BeautifulSoup(requests.get(example_url).text, 'lxml')
        try:
            example_big_image = DOMAIN + example_detail_page.find('div', class_='component-main-image').find('img').get('src') #большое изображение
        except AttributeError:
            start_load = False
        if start_load:
            big_image_title = example_big_image.strip().split('_')[-1].split('.')[0] + '_big.jpg'
            print('big: ', example_big_image, big_image_title)
            print('small: ', example_small_image, small_image_title)

            products = example_detail_page.find_all('div', class_='product')
            products_list_to_save = []
            products_in_example_to_save = None
            for product in products:
                product_article_number = product.get('id').strip().split('_')[1]
                if product not in products_list_to_save:
                    products_list_to_save.append(product_article_number)
                products_in_example_to_save = '#'.join(products_list_to_save)
            continue_ = True
            try:
                created_room = RoomExample.objects.get(title=example_title, room_place=query)
                continue_ = False
            except RoomExample.DoesNotExist:
                created_room = RoomExample.objects.create(room_place=query, title=example_title, products=products_in_example_to_save, unique_identificator=create_identificator(8))
            if continue_:
                #small image
                try:
                    ExampleImage.objects.get(title=small_image_title, example=created_room, is_presentation=True)
                except ExampleImage.DoesNotExist:
                    image_page = requests.get(example_small_image).content
                    image_file = open(os.path.join(MEDIA_ROOT, 'rooms_examples/' + small_image_title), 'wb')
                    image_file.write(image_page)
                    image_file.close()
                    ExampleImage.objects.create(image='rooms_examples/' + small_image_title, title=small_image_title, example=created_room, is_presentation=True)
                #big image
                try:
                    ExampleImage.objects.get(title=big_image_title, example=created_room, is_presentation=False)
                except ExampleImage.DoesNotExist:
                    image_page = requests.get(example_big_image).content
                    image_file = open(os.path.join(MEDIA_ROOT, 'rooms_examples/' + big_image_title), 'wb')
                    image_file.write(image_page)
                    image_file.close()
                    ExampleImage.objects.create(image='rooms_examples/' + big_image_title,title=big_image_title, example=created_room)
        else:
            print('----------------------------------')
            print('load error on page %s' % example_url)
            print('----------------------------------')














