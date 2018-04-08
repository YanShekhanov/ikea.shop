from ikea_parser.models import ProductImage

def json_serializer(queryset):
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
    return objects_list