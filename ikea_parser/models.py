from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import os
from app.settings import BASE_DIR
from django.utils.timezone import now
# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False, default='', verbose_name='Название категории')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_translated = models.BooleanField(default=False, blank=True, null=False, verbose_name='Перевод')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория, id', editable=False)
    title = models.CharField(max_length=128, blank=False, null=False, default='', verbose_name='Название подкатегории')
    url = models.CharField(max_length=256, blank=True, null=False, default='', verbose_name='Ссылка')
    url_ikea = models.CharField(max_length=256, blank=True, null=False, default='', verbose_name='Ссылка')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_translated = models.BooleanField(default=False, blank=True, null=False, verbose_name='Перевод')
    have_sub_subcategory = models.BooleanField(default=False, blank=False, null=False, verbose_name='Под под категория')
    unique_identificator = models.CharField(max_length=8, blank=False, null=False, verbose_name='Идентификатор')
    priority = models.BooleanField(default=False, blank=True, null=False, verbose_name='Приоритет')


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

class SubSubCategory(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, verbose_name='Подкатегория, id')
    title = models.CharField(max_length=128, blank=False, null=False, default='', verbose_name='Название подкатегории')
    url = models.CharField(max_length=256, blank=True, null=False, default='', verbose_name='Ссылка')
    url_ikea = models.CharField(max_length=256, blank=True, null=False, default='', verbose_name='Ссылка')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_translated = models.BooleanField(default=False, blank=True, null=False, verbose_name='Перевод')
    unique_identificator = models.CharField(max_length=8, blank=False, null=False, verbose_name='Идентификатор')
    priority = models.BooleanField(default=False, blank=True, null=False, verbose_name='Приоритет')



    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

class Product(models.Model):
    subcategory = models.ManyToManyField(SubCategory, verbose_name='Подкатегория, id')
    sub_subcategory = models.ManyToManyField(SubSubCategory, verbose_name='Под подкатегория, id')
    article_number = models.CharField(max_length=9, blank=False, default='', null=False, verbose_name='Артикул')
    title = models.CharField(max_length=64, blank=False, null=False, default='', verbose_name='Название')
    description = models.CharField(max_length=128, blank=False, null=True, default='', verbose_name='Короткое описание')
    price = models.FloatField(blank=False, null=False, default=0, verbose_name='Цена')
    url_ikea = models.CharField(max_length=256, null=False, blank=False, default='', verbose_name='Ссылка')
    url = models.CharField(max_length=256, null=True, blank=True, default='', verbose_name='Ссылка')
    available = models.IntegerField(default=0, blank=False, null=False, verbose_name='Наличие')
    key_feautures = models.CharField(max_length=1536, blank=True, null=True, default='', verbose_name='Основное описание')
    good_to_know = models.CharField(max_length=1536, blank=True, null=True, default='', verbose_name='Полезно знать')
    care_instructions = models.CharField(max_length=1536, blank=True, null=True, default='', verbose_name='Инструкция по уходу')
    materials_info = models.CharField(max_length=1536, blank=True, null=True, default='', verbose_name='Материал')
    dimensions = models.CharField(max_length=256, blank=True, null=True, default='', verbose_name='Габариты')
    designed_by = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name='Создатель')
    complementary_products = models.CharField(max_length=512, blank=True, default='', null=True, verbose_name='Дополняющие продукты')
    additional_models = models.CharField(max_length=512, blank=True, null=True, default='', verbose_name='Модели')
    color_options = models.CharField(max_length=512, blank=True, null=True, default='', verbose_name='Другие цвета')
    size_options = models.CharField(max_length=512, blank=True, null=True, default=None, verbose_name='Другие размеры' )
    color = models.CharField(max_length=32, blank=True, default='', null=True, verbose_name='Цвет')
    is_translated = models.BooleanField(default=False, blank=True, null=False, verbose_name='Перевод')
    is_parsed = models.BooleanField(default=False, blank=False, null=False, verbose_name='Скачанно')
    unique_identificator = models.CharField(max_length=8, blank=False, null=False, default='', verbose_name='Идентификатор')
    parse_later = models.BooleanField(blank=True, null=False, default=False, verbose_name='Парсить позже')
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return self.article_number

#при удалении записи продукта ищем связанные с ним изображения и удаляем. Если у изображения 2 или больше связанных продуктов,
#то удаляем из reletedField только удаляемый продукт
@receiver(post_delete, sender=Product)
def delete_images_for_product(sender, instance, **kwargs):
    existed_images = ProductImage.objects.filter(product=instance)
    for image in existed_images:
        releted_nmb = len(image.product.all())
        if releted_nmb == 1:
            image.delele()
        if releted_nmb > 1:
            for releted_product in image.product.all():
                if releted_product == instance:
                    image.product.remove(releted_product)


class ProductImage(models.Model):
    product = models.ManyToManyField(Product, verbose_name='Продукт, id')
    image = models.ImageField(upload_to='products/', default='', verbose_name='Изображение')
    title = models.CharField(max_length=32, blank=False, null=False, default='', verbose_name='Название')
    size = models.SmallIntegerField(blank=False, null=False, default=0, verbose_name='Размер, px')
    is_icon = models.BooleanField(blank=True, default=False, verbose_name='Иконка')

@receiver(post_delete, sender=ProductImage)
def delete_images(sender, instance, **kwargs):
    try:
        os.remove(BASE_DIR + instance.image.url)
    except FileNotFoundError:
        pass

class Room(models.Model):
    title = models.CharField(max_length=32, null=True, default=None, blank=True, verbose_name='Название комнаты')
    ikea_url = models.CharField(max_length=256, null=True, default=None, blank=False, verbose_name='ссылка')
    image = models.ImageField(upload_to='rooms/', default='', verbose_name='Изображение')
    unique_identificator = models.CharField(max_length=4, default=None, null=True, blank=True, verbose_name='identificator')

    def __str__(self):
        return self.title

class RoomPlace(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='комната')
    title = models.CharField(max_length=32, null=True, default=None, blank=True, verbose_name='Название части')
    ikea_url = models.CharField(max_length=256, null=True, default=None, blank=False, verbose_name='ссылка')
    image = models.ImageField(upload_to='room_places/', default=None, null=True, blank=True)
    unique_identificator = models.CharField(max_length=8, default=None, null=True, blank=True, verbose_name='identificator')

    def __str__(self):
        return ('%s, %s' %(self.room.title, self.title))

class RoomExample(models.Model):
    room_place = models.ForeignKey(RoomPlace, on_delete=models.CASCADE, verbose_name='часть комнаты')
    title = models.CharField(max_length=512, null=True, default=None, blank=False, verbose_name='название')
    products = models.CharField(max_length=1024, null=True, default=None, blank=True, verbose_name='продукты')

class ExampleImage(models.Model):
    example = models.ForeignKey(RoomExample, on_delete=models.CASCADE, verbose_name='комната')
    image = models.ImageField(upload_to='rooms_examples/', default='', verbose_name='Изображение')
    title = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name='название')
    is_presentation = models.BooleanField(blank=True, default=False, verbose_name='маленькое изображение')








