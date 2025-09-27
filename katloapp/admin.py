from django.contrib import admin
from .models import Business, Product

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name','user','whatsapp_number','slug','public','created_at')
    search_fields = ('name','user__username','whatsapp_number','slug')
    list_filter = ('public','city')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','business','price','active','created_at')
    search_fields = ('name','business__name','sku')
    list_filter = ('active',)
