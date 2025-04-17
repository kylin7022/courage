from django.contrib import admin
from .models import Customer, ProductType, IncomingShipment, OutgoingShipment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'phone', 'created_at']
    search_fields = ['name', 'contact', 'phone']
    list_per_page = 20

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['customer', 'model_number', 'unit_price', 'created_at']
    search_fields = ['customer__name', 'model_number']
    list_filter = ['customer']
    list_per_page = 20

@admin.register(IncomingShipment)
class IncomingShipmentAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'customer', 'product_type', 'quantity', 'shipment_date']
    search_fields = ['document_number', 'customer__name', 'product_type__model_number']
    list_filter = ['customer', 'shipment_date']
    date_hierarchy = 'shipment_date'
    list_per_page = 20

@admin.register(OutgoingShipment)
class OutgoingShipmentAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'customer', 'product_type', 'quantity', 'unit_price', 'total_amount', 'shipment_date']
    search_fields = ['document_number', 'customer__name', 'product_type__model_number']
    list_filter = ['customer', 'shipment_date']
    date_hierarchy = 'shipment_date'
    readonly_fields = ['unit_price', 'total_amount']
    list_per_page = 20
