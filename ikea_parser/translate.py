from googletrans import Translator
import re

def translate(query):
    print(query.values_list())

    not_editable = ['id', 'category', 'subcategory', 'sub_subcategory', 'updated', 'created', 'is_translated', 'is_parsed',
                    'url', 'url_ikea', 'have_sub_subcategory', 'unique_identificator', 'priority', 'article_number',
                    'price', 'color_options', 'product', 'image', 'size']

    translator = Translator()
    translated_text = re.sub(r'\s+', ' ', string=translator.translate(query.title, src='pl', dest='ru').text)
    corrected_text = translated_text[0].upper() + translated_text[1:]
    #query.title = corrected_text
    #query.save()
