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
    path('inbound/', views.inbound_list, name='inbound_list'),  # 修改这行
    path('inbound/add/', views.inbound_add, name='inbound_add'),
    path('inbound/<int:inbound_id>/', views.inbound_detail, name='inbound_detail'),
    
    # 出库单据管理
    path('outbound/', views.outbound_list, name='outbound_list'),  # 修改这行
    path('outbound/add/', views.outbound_add, name='outbound_add'),
    path('outbound/<int:outbound_id>/', views.outbound_detail, name='outbound_detail'),
    
    # 产品型号管理
    path('products/', views.product_list, name='product_list'),
    path('product/add/', views.product_add, name='product_add'),  # Added missing comma
    path('product/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # 价格设置
    # path('prices/', views.price_list, name='price_list'),  # 暂时注释该行
    path('price/add/', views.price_add, name='price_add'),
    path('price/<int:price_id>/edit/', views.price_edit, name='price_edit'),
    
    # 导出账单
    path('export-bill/<int:customer_id>/', views.export_customer_bill, name='export_customer_bill'),
    path('batch-groups/', views.batch_group_list, name='batch_group_list'),
    path('batch-groups/add/', views.batch_group_add, name='batch_group_add'),
    path('batch-groups/<int:group_id>/edit/', views.batch_group_edit, name='batch_group_edit'),
    path('customers/<int:customer_id>/export-monthly-bill/<int:year>/<int:month>/', 
         views.export_monthly_bill, name='export_monthly_bill'),
    path('product-types/', views.product_type_list, name='product_type_list'),
    path('product-types/add/', views.product_type_add, name='product_type_add'),
    path('product-types/<int:product_type_id>/edit/', views.product_type_edit, name='product_type_edit'),
]