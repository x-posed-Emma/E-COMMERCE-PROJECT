from django.contrib import admin
from .models import Product,VendorProfile,ProductCategory

app_name = 'app1'

@admin.register(Product)
class Productss(admin.ModelAdmin):
    list_display = ('vendor','product_name','product_price','product_image','available_quantity','discount','available')

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'store_name', 'activated']  
    search_fields = ['store_name', 'user__username'] 
    list_filter = ['activated']   


@admin.register(ProductCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    