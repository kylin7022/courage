from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # 客户管理
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    
    # 入库单据管理
    path('inbound/', views.inbound_list, name='inbound_list'),
    path('inbound/add/', views.inbound_add, name='inbound_add'),
    path('inbound/<int:inbound_id>/', views.inbound_detail, name='inbound_detail'),
    path('inbound/<int:inbound_id>/edit/', views.inbound_edit, name='inbound_edit'),
    path('inbound/<int:inbound_id>/delete/', views.inbound_delete, name='inbound_delete'),
    
    # 出库单据管理
    path('outbound/', views.outbound_list, name='outbound_list'),
    path('outbound/add/', views.outbound_add, name='outbound_add'),
    path('outbound/<int:outbound_id>/', views.outbound_detail, name='outbound_detail'),
    path('outbound/<int:outbound_id>/edit/', views.outbound_edit, name='outbound_edit'),
    path('outbound/<int:outbound_id>/delete/', views.outbound_delete, name='outbound_delete'),
    
    # 产品型号管理
    path('product-types/', views.product_type_list, name='product_type_list'),
    path('product-types/add/', views.product_type_add, name='product_type_add'),
    path('product-types/<int:product_type_id>/edit/', views.product_type_edit, name='product_type_edit'),
    path('product-types/<int:product_type_id>/delete/', views.product_type_delete, name='product_type_delete'),
    
    # 价格设置
    path('price/', views.price_list, name='price_list'),
    path('price/add/', views.price_add, name='price_add'),
    path('price/<int:price_id>/edit/', views.price_edit, name='price_edit'),
    path('price/<int:price_id>/delete/', views.price_delete, name='price_delete'),
    
    # 导出账单
    path('export-bill/<int:customer_id>/', views.export_customer_bill, name='export_customer_bill'),
    
    # 批次组管理
    path('batch-groups/', views.batch_group_list, name='batch_group_list'),
    path('batch-groups/add/', views.batch_group_create, name='batch_group_create'),
    path('batch-groups/<int:pk>/update/', views.batch_group_update, name='batch_group_update'),
    path('batch-groups/<int:pk>/delete/', views.batch_group_delete, name='batch_group_delete'),
    path('customers/<int:customer_id>/export-monthly-bill/<int:year>/<int:month>/', 
         views.export_monthly_bill, name='export_monthly_bill'),
         
    # API接口
    path('api/product-type/<int:product_type_id>/', views.product_type_detail_api, name='product_type_detail_api'),
]