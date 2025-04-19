from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
from django.contrib import messages
import csv
import datetime
from decimal import Decimal

from .models import (
    Customer, 
    ProductType, 
    Price, 
    OutgoingShipment, 
    IncomingShipment, 
    BatchGroup, 
    Inventory
)
from .forms import (
    CustomerForm, 
    ProductTypeForm, 
    PriceForm, 
    OutgoingShipmentForm, 
    IncomingShipmentForm, 
    BatchGroupForm
)
from django.core.paginator import Paginator

def home(request):
    """
    首页视图函数
    """
    return render(request, 'home.html')

# 客户管理
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'inventory/customer_list.html', {'customers': customers})

@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '客户添加成功！')
            return redirect('inventory:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': '添加客户'})

@login_required
def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, '客户更新成功！')
            return redirect('inventory:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': '编辑客户'})

@login_required
def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, '客户删除成功！')
        return redirect('inventory:customer_list')
    return render(request, 'inventory/confirm_delete.html', {'object': customer, 'title': '删除客户'})

# 入库单据管理
@login_required
def inbound_list(request):
    inbound_shipments = IncomingShipment.objects.all().order_by('-created_at')
    return render(request, 'inventory/inbound_list.html', {'inbound_shipments': inbound_shipments})

@login_required
def inbound_add(request):
    if request.method == 'POST':
        form = IncomingShipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '入库单据添加成功！')
            return redirect('inventory:inbound_list')
    else:
        form = IncomingShipmentForm()
    return render(request, 'inventory/inbound_form.html', {'form': form, 'title': '添加入库单据'})

@login_required
def inbound_detail(request, inbound_id):
    inbound = get_object_or_404(IncomingShipment, id=inbound_id)
    return render(request, 'inventory/inbound_detail.html', {'inbound': inbound})

@login_required
def inbound_edit(request, inbound_id):
    inbound = get_object_or_404(IncomingShipment, id=inbound_id)
    if request.method == 'POST':
        form = IncomingShipmentForm(request.POST, instance=inbound)
        if form.is_valid():
            form.save()
            messages.success(request, '入库单据更新成功！')
            return redirect('inventory:inbound_list')
    else:
        form = IncomingShipmentForm(instance=inbound)
    return render(request, 'inventory/inbound_form.html', {'form': form, 'title': '编辑入库单据'})

@login_required
def inbound_delete(request, inbound_id):
    inbound = get_object_or_404(IncomingShipment, id=inbound_id)
    if request.method == 'POST':
        inbound.delete()
        messages.success(request, '入库单据删除成功！')
        return redirect('inventory:inbound_list')
    return render(request, 'inventory/confirm_delete.html', {'object': inbound, 'title': '删除入库单据'})

# 出库单据管理
@login_required
def outbound_list(request):
    outbound_shipments = OutgoingShipment.objects.all().order_by('-created_at')
    return render(request, 'inventory/outbound_list.html', {'outbound_shipments': outbound_shipments})

@login_required
def outbound_add(request):
    if request.method == 'POST':
        form = OutgoingShipmentForm(request.POST)
        if form.is_valid():
            outbound = form.save(commit=False)
            
            # 如果品名规格未填写，但已选择产品型号，则自动填写
            if not outbound.product_spec and outbound.product_type:
                product_type = outbound.product_type
                outbound.product_spec = f"{product_type.name} - {product_type.description}"
                
            outbound.save()
            messages.success(request, '出库单据添加成功！')
            return redirect('inventory:outbound_list')
    else:
        form = OutgoingShipmentForm()
    return render(request, 'inventory/outbound_form.html', {'form': form, 'title': '添加出库单据'})

@login_required
def outbound_detail(request, outbound_id):
    outbound = get_object_or_404(OutgoingShipment, id=outbound_id)
    return render(request, 'inventory/outbound_detail.html', {'outbound': outbound})

@login_required
def outbound_edit(request, outbound_id):
    outbound = get_object_or_404(OutgoingShipment, id=outbound_id)
    if request.method == 'POST':
        form = OutgoingShipmentForm(request.POST, instance=outbound)
        if form.is_valid():
            outbound = form.save(commit=False)
            
            # 如果品名规格未填写，但已选择产品型号，则自动填写
            if not outbound.product_spec and outbound.product_type:
                product_type = outbound.product_type
                outbound.product_spec = f"{product_type.name} - {product_type.description}"
                
            outbound.save()
            messages.success(request, '出库单据更新成功！')
            return redirect('inventory:outbound_list')
    else:
        form = OutgoingShipmentForm(instance=outbound)
    return render(request, 'inventory/outbound_form.html', {'form': form, 'title': '编辑出库单据'})

@login_required
def outbound_delete(request, outbound_id):
    outbound = get_object_or_404(OutgoingShipment, id=outbound_id)
    if request.method == 'POST':
        outbound.delete()
        messages.success(request, '出库单据删除成功！')
        return redirect('inventory:outbound_list')
    return render(request, 'inventory/confirm_delete.html', {'object': outbound, 'title': '删除出库单据'})

# 产品型号管理
@login_required
def product_type_list(request):
    product_types = ProductType.objects.all().order_by('-created_at')
    return render(request, 'inventory/product_type_list.html', {'product_types': product_types})

@login_required
def product_type_add(request):
    if request.method == 'POST':
        form = ProductTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '产品型号添加成功！')
            return redirect('inventory:product_type_list')
    else:
        form = ProductTypeForm()
    return render(request, 'inventory/product_type_form.html', {'form': form, 'title': '添加产品型号'})

@login_required
def product_type_edit(request, product_type_id):
    product_type = get_object_or_404(ProductType, id=product_type_id)
    if request.method == 'POST':
        form = ProductTypeForm(request.POST, instance=product_type)
        if form.is_valid():
            form.save()
            messages.success(request, '产品型号更新成功！')
            return redirect('inventory:product_type_list')
    else:
        form = ProductTypeForm(instance=product_type)
    return render(request, 'inventory/product_type_form.html', {'form': form, 'title': '编辑产品型号'})

@login_required
def product_type_delete(request, product_type_id):
    product_type = get_object_or_404(ProductType, id=product_type_id)
    if request.method == 'POST':
        product_type.delete()
        messages.success(request, '产品型号删除成功！')
        return redirect('inventory:product_type_list')
    return render(request, 'inventory/confirm_delete.html', {'object': product_type, 'title': '删除产品型号'})

# 价格设置
@login_required
def price_list(request):
    prices = Price.objects.all().order_by('-effective_date')
    return render(request, 'inventory/price_list.html', {'prices': prices})

@login_required
def price_add(request):
    if request.method == 'POST':
        form = PriceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '价格记录添加成功！')
            return redirect('inventory:price_list')
    else:
        form = PriceForm()
    return render(request, 'inventory/price_form.html', {'form': form, 'title': '添加价格记录'})

@login_required
def price_edit(request, price_id):
    price = get_object_or_404(Price, id=price_id)
    if request.method == 'POST':
        form = PriceForm(request.POST, instance=price)
        if form.is_valid():
            form.save()
            messages.success(request, '价格记录更新成功！')
            return redirect('inventory:price_list')
    else:
        form = PriceForm(instance=price)
    return render(request, 'inventory/price_form.html', {'form': form, 'title': '编辑价格记录'})

@login_required
def price_delete(request, price_id):
    price = get_object_or_404(Price, id=price_id)
    if request.method == 'POST':
        price.delete()
        messages.success(request, '价格记录删除成功！')
        return redirect('inventory:price_list')
    return render(request, 'inventory/confirm_delete.html', {'object': price, 'title': '删除价格记录'})

# 导出账单
@login_required
def export_customer_bill(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 获取该客户的所有出货记录
    outgoing_shipments = OutgoingShipment.objects.filter(customer=customer).order_by('shipping_date')
    
    # 创建Excel响应
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{customer.name}_bill.xls"'
    
    # 添加BOM标记，解决Excel中文显示乱码问题
    response.write(u'\ufeff'.encode('utf-8'))
    
    # 创建CSV写入器
    writer = csv.writer(response, delimiter='\t')
    writer.writerow(['出货日期', '型号', '品名规格', '批号', '批次组', '针距', '数量', '单价', '总金额', '备注'])
    
    for shipment in outgoing_shipments:
        writer.writerow([
            shipment.shipping_date.strftime('%Y-%m-%d'),
            shipment.product_type.model_number,
            shipment.product_spec,
            shipment.batch_number,
            shipment.batch_group,
            shipment.pin_pitch,
            shipment.quantity,
            f"{shipment.unit_price:.2f}",
            f"{shipment.total_amount:.2f}",
            shipment.notes
        ])
    
    return response

@login_required
def export_monthly_bill(request, customer_id, year, month):
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 构造日期范围
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)
    
    # 获取该客户在指定月份的所有出货记录
    outgoing_shipments = OutgoingShipment.objects.filter(
        customer=customer,
        shipping_date__gte=start_date,
        shipping_date__lt=end_date
    ).order_by('shipping_date')
    
    # 创建Excel响应
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{customer.name}_{year}_{month}_monthly_bill.xls"'
    
    # 添加BOM标记，解决Excel中文显示乱码问题
    response.write(u'\ufeff'.encode('utf-8'))
    
    # 创建CSV写入器
    writer = csv.writer(response, delimiter='\t')
    writer.writerow(['出货日期', '型号', '品名规格', '批号', '批次组', '针距', '数量', '单价', '总金额', '备注'])
    
    total_amount = Decimal('0.00')
    
    for shipment in outgoing_shipments:
        writer.writerow([
            shipment.shipping_date.strftime('%Y-%m-%d'),
            shipment.product_type.model_number,
            shipment.product_spec,
            shipment.batch_number,
            shipment.batch_group,
            shipment.pin_pitch,
            shipment.quantity,
            f"{shipment.unit_price:.2f}",
            f"{shipment.total_amount:.2f}",
            shipment.notes
        ])
        total_amount += shipment.total_amount
    
    # 写入总计行
    writer.writerow(['', '', '', '', '', '', '', '总计', f"{total_amount:.2f}", ''])
    
    return response

# 批次组管理
@login_required
def batch_group_list(request):
    batch_group_list = BatchGroup.objects.all().order_by('-created_at')
    paginator = Paginator(batch_group_list, 10)  # 每页显示10条记录
    
    page = request.GET.get('page')
    batch_groups = paginator.get_page(page)
    
    return render(request, 'inventory/batch_group_list.html', {
        'batch_groups': batch_groups,
        'page_obj': batch_groups,  # 添加这行
        'title': '批次管理'
    })

def batch_group_create(request):
    if request.method == 'POST':
        form = BatchGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '批次创建成功')
            return redirect('inventory:batch_group_list')
    else:
        form = BatchGroupForm()
    
    return render(request, 'inventory/batch_group_form.html', {
        'form': form,
        'title': '新增批次'
    })

def batch_group_update(request, pk):
    batch_group = get_object_or_404(BatchGroup, pk=pk)
    if request.method == 'POST':
        form = BatchGroupForm(request.POST, instance=batch_group)
        if form.is_valid():
            form.save()
            messages.success(request, '批次更新成功')
            return redirect('inventory:batch_group_list')
    else:
        form = BatchGroupForm(instance=batch_group)
    
    return render(request, 'inventory/batch_group_form.html', {
        'form': form,
        'title': '编辑批次'
    })

def batch_group_delete(request, pk):
    batch_group = get_object_or_404(BatchGroup, pk=pk)
    batch_group.delete()
    messages.success(request, '批次删除成功')
    return redirect('inventory:batch_group_list')

# API视图
@login_required
def product_type_detail_api(request, product_type_id):
    """
    获取产品型号详细信息的API
    """
    product_type = get_object_or_404(ProductType, id=product_type_id)
    data = {
        'id': product_type.id,
        'name': product_type.name,
        'model_number': product_type.model_number,
        'description': product_type.description,
        'unit_price': float(product_type.unit_price),
        'customer_id': product_type.customer.id,
        'customer_name': product_type.customer.name
    }
    return JsonResponse(data)