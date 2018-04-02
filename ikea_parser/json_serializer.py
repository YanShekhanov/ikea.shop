def json_serializer(queryset):
    objects_list = []
    for object in queryset:
        one_object_dict = {}
        for field in object._meta.get_fields():
            try:
                if field.many_to_many:
                    one_object_dict[field.name] = json_serializer(getattr(object, field.name).all())
                one_object_dict[field.name] = getattr(object, field.name)
            except AttributeError:
                pass
        objects_list.append(one_object_dict)
    return objects_list