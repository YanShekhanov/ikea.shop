from django.db import models
from django.db.models.signals import post_delete, post_save
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
    not_display = models.BooleanField(default=False, blank=True, null=False, verbose_name='Не отображать')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

@receiver(post_save, sender=Category)
def not_display_releted_sub(sender, instance, **kwargs):
    if instance.not_display:
        releted_subcategories = SubCategory.objects.filter(category=instance)
        for releted_subcategory in releted_subcategories:
            releted_subcategory.not_display = True
            releted_subcategory.save()

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
    not_display = models.BooleanField(default=False, blank=True, null=False, verbose_name='Не отображать')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

@receiver(post_save, sender=SubCategory)
def not_display_releted_subsub(sender, instance, **kwargs):
    if instance.not_display:
        releted_sub_subcategories = SubSubCategory.objects.filter(subcategory=instance)
        for releted_sub_subcategory in releted_sub_subcategories:
            releted_sub_subcategory.not_display = True
            releted_sub_subcategory.save()


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
    not_display = models.BooleanField(default=False, blank=True, null=False, verbose_name='Не отображать')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

class Product(models.Model):
    subcategory = models.ManyToManyField(SubCategory, verbose_name='Подкатегория, id')
    sub_subcategory = models.ManyToManyField(SubSubCategory, verbose_name='Под подкатегория, id', blank=True, null=True)
    article_number = models.CharField(max_length=9, blank=False, default='', null=False, verbose_name='Артикул')
    title = models.CharField(max_length=64, blank=False, null=False, default='', verbose_name='Название')
    description = models.TextField(blank=False, null=True, default='', verbose_name='Короткое описание')
    price = models.IntegerField(blank=False, null=False, default=0, verbose_name='Цена')
    url_ikea = models.CharField(max_length=256, null=False, blank=False, default='', verbose_name='Ссылка')
    url = models.CharField(max_length=256, null=True, blank=True, default='', verbose_name='Ссылка')
    available = models.IntegerField(default=0, blank=True, null=True, verbose_name='Наличие')
    key_feautures = models.TextField(blank=True, null=True, default='', verbose_name='Основное описание')
    good_to_know = models.TextField(blank=True, null=True, default='', verbose_name='Полезно знать')
    care_instructions = models.TextField(blank=True, null=True, default='', verbose_name='Инструкция по уходу')
    materials_info = models.TextField(blank=True, null=True, default='', verbose_name='Материал')
    dimensions = models.TextField(blank=True, null=True, default='', verbose_name='Габариты')
    designed_by = models.CharField(max_length=128, blank=True, null=True, default='', verbose_name='Создатель')
    complementary_products = models.TextField(blank=True, default='', null=True, verbose_name='Дополняющие продукты')
    additional_models = models.TextField(blank=True, null=True, default='', verbose_name='Модели')
    color_options = models.TextField(blank=True, null=True, default='', verbose_name='Другие цвета')
    size_options = models.TextField(blank=True, null=True, default=None, verbose_name='Другие размеры' )
    color = models.CharField(max_length=256, blank=True, default='', null=True, verbose_name='Цвет')
    is_translated = models.BooleanField(default=False, blank=True, null=False, verbose_name='Перевод')
    is_parsed = models.BooleanField(default=False, blank=False, null=False, verbose_name='Скачанно')
    unique_identificator = models.CharField(max_length=8, blank=False, null=False, default='', verbose_name='Идентификатор')
    parse_later = models.BooleanField(blank=True, null=False, default=False, verbose_name='Парсить позже')
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name='Обновлено')

    change_price_process = models.BooleanField(blank=True, default=False, verbose_name='Процесс изменения цены')
    price_coef = models.FloatField(blank=True, null=False, default=0.0, verbose_name='Коефициент цены')

    def __str__(self):
        return self.article_number

    def with_dot(self):
        without_litt = []
        for sym in self.article_number:
            if sym == 'S' or sym == 's':
                pass
            else:
                without_litt.append(sym)
        return ''.join(without_litt[0:3]) + '.' + ''.join(without_litt[3:6]) + '.' + ''.join(without_litt[6:])


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
    not_display = models.BooleanField(default=False, blank=True, null=False, verbose_name='Не отображать')

    def __str__(self):
        return self.title

@receiver(post_save, sender=Room)
def releted_room_place(sender, instance, **kwargs):
    if instance.not_display:
        releted_room_places = RoomPlace.objecta.filter(room=instance)
        for room_place in releted_room_places:
            room_place.not_display = True
            room_place.save()

class RoomPlace(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='комната')
    title = models.CharField(max_length=32, null=True, default=None, blank=True, verbose_name='Название части')
    ikea_url = models.CharField(max_length=256, null=True, default=None, blank=False, verbose_name='ссылка')
    image = models.ImageField(upload_to='room_places/', default=None, null=True, blank=True)
    unique_identificator = models.CharField(max_length=8, default=None, null=True, blank=True, verbose_name='identificator')
    not_display = models.BooleanField(default=False, blank=True, null=False, verbose_name='Не отображать')

    def __str__(self):
        return ('%s, %s' %(self.room.title, self.title))

@receiver(post_save, sender=RoomPlace)
def releted_room_place(sender, instance, **kwargs):
    if instance.not_display:
        releted_room_examples = RoomExample.objecta.filter(room_place=instance)
        for room_example in releted_room_examples:
            room_example.not_display = True
            room_example.save()

class RoomExample(models.Model):
    room_place = models.ForeignKey(RoomPlace, on_delete=models.CASCADE, verbose_name='часть комнаты')
    title = models.CharField(max_length=512, null=True, default=None, blank=False, verbose_name='название')
    products = models.CharField(max_length=1024, null=True, default=None, blank=True, verbose_name='продукты')
    unique_identificator = models.CharField(max_length=8, null=True, default=None, blank=True, verbose_name='идентификатор')
    not_display = models.BooleanField(default=False, blank=True, null=False, verbose_name='Не отображать')

class ExampleImage(models.Model):
    example = models.ForeignKey(RoomExample, on_delete=models.CASCADE, verbose_name='комната')
    image = models.ImageField(upload_to='rooms_examples/', default='', verbose_name='Изображение')
    title = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name='название')
    is_presentation = models.BooleanField(blank=True, default=False, verbose_name='маленькое изображение')








