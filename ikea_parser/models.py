from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import os
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
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, verbose_name='Подкатегория, id')
    sub_subcategory = models.ForeignKey(SubSubCategory, on_delete=models.CASCADE, null=True, verbose_name='Под подкатегория, id')
    article_number = models.CharField(max_length=9, blank=False, default='', null=False, verbose_name='Артикул')
    title = models.CharField(max_length=32, blank=False, null=False, default='', verbose_name='Название')
    description = models.CharField(max_length=64, blank=False, null=False, default='', verbose_name='Короткое описание')
    price = models.FloatField(blank=False, null=False, default=0, verbose_name='Цена')
    url_ikea = models.CharField(max_length=256, null=False, blank=True, default='', verbose_name='Ссылка')
    url = models.CharField(max_length=256, null=False, blank=True, default='', verbose_name='Ссылка')
    available = models.IntegerField(default=0, blank=False, null=False, verbose_name='Наличие')
    key_feautures = models.CharField(max_length=512, blank=True, null=False, default='', verbose_name='Основное описание')
    good_to_know = models.CharField(max_length=512, blank=True, null=False, default='', verbose_name='Полезно знать')
    care_instructions = models.CharField(max_length=512, blank=True, null=False, default='', verbose_name='Инструкция по уходу')
    materials_info = models.CharField(max_length=512, blank=True, null=False, default='', verbose_name='Материал')
    dimensions = models.CharField(max_length=128, blank=True, null=False, default='', verbose_name='Габариты')
    designed_by = models.CharField(max_length=32, blank=True, null=False, default='', verbose_name='Создатель')
    complementary_products = models.CharField(max_length=512, blank=True, default='', null=False, verbose_name='Дополняющие продукты')
    color_options = models.CharField(max_length=512, blank=True, null=True, default='', verbose_name='Другие цвета')
    color = models.CharField(max_length=32, blank=True, default='', null=True, verbose_name='Цвет')
    is_translated = models.BooleanField(default=False, blank=True, null=False, verbose_name='Перевод')
    is_parsed = models.BooleanField(default=False, blank=False, null=False, verbose_name='Скачанно')
    unique_identificator = models.CharField(max_length=8, blank=False, null=False, default='', verbose_name='Идентификатор')

    def __str__(self):
        return self.article_number

#НЕ РАБОТАЕТ
@receiver(post_delete, sender=Product)
def delete_images_for_product(sender, instance, **kwargs):
    existed_images = None
    try:
        existed_images = ProductImage.objects.filter(product=instance)
        for existed_image in existed_images:
            if len(existed_image.product.all()) > 1:
                existed_image.product.remove(instance)
            else:
                existed_image.delete()
                try:
                    os.remove(existed_image.image.url)
                except FileNotFoundError:
                    pass
    except existed_images.DoesNotExist:
        pass



class ProductImage(models.Model):
    product = models.ManyToManyField(Product, verbose_name='Продукт, id')
    image = models.ImageField(upload_to='products/', default='', verbose_name='Изображение')
    title = models.CharField(max_length=16, blank=False, null=False, default='', verbose_name='Название')
    size = models.SmallIntegerField(blank=False, null=False, default=0, verbose_name='Размер, px')




