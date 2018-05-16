from ikea_parser.models import ProductImage

'''def json_serializer(queryset):
    objects_list = []
    for object in queryset:
        one_object_dict = {}
        try:
            image = ProductImage.objects.filter(product=object).first()
            one_object_dict['image'] = image.image.url
        except AttributeError:
            one_object_dict['image'] = ''

        for field in object._meta.get_fields():
            try:
                if field.name == 'subcategory' or field.name == 'sub_subcategory':
                    continue
                one_object_dict[field.name] = getattr(object, field.name)
            except AttributeError:
                pass
        objects_list.append(one_object_dict)
    return objects_list'''

def product_to_json(queryset):
    objects_list = []
    for product in queryset:
        one_product_dict = {}
        try:
            image = ProductImage.objects.filter(product=product, size=250).first()
            one_product_dict['image'] = image.image.url
        except ProductImage.DoesNotExist:
            one_product_dict['image'] = 'Image does not exist'
        one_product_dict['article_number_with_dot'] = product.with_dot()
        one_product_dict['article_number'] = product.article_number
        one_product_dict['title'] = product.title
        one_product_dict['price'] = product.price
        one_product_dict['unique_identificator'] = product.unique_identificator
        one_product_dict['dimensions'] = product.dimensions
        objects_list.append(one_product_dict)
    return objects_list