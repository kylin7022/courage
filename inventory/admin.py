from django.contrib import admin
from .models import Customer, ProductType, IncomingShipment, OutgoingShipment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'phone', 'created_at']
    search_fields = ['name', 'contact', 'phone']
    list_per_page = 20

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_number', 'barcode']
    search_fields = ['name', 'model_number', 'barcode']
    list_filter = ['model_number']
    list_per_page = 20

@admin.register(IncomingShipment)
class IncomingShipmentAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'customer', 'product_type', 'quantity', 'created_at']
    search_fields = ['document_number', 'customer__name', 'product_type__model_number']
    list_filter = ['customer', 'audit_status']
    date_hierarchy = 'created_at'
    list_per_page = 20

@admin.register(OutgoingShipment)
class OutgoingShipmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product_type', 'quantity', 'unit_price', 'total_amount', 'created_at']
    search_fields = ['customer__name', 'product_type']
    list_filter = ['customer', 'audit_status']
    date_hierarchy = 'created_at'
    readonly_fields = ['total_amount']
    list_per_page = 20
