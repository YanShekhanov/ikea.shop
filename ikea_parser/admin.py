from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)

admin.site.register(Room)
admin.site.register(RoomPlace)
admin.site.register(RoomExample)
admin.site.register(ExampleImage)