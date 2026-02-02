from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock')
    search_fields = ('title',)
    list_filter = ('price', 'stock')