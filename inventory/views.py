from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Customer, ProductType, IncomingShipment, OutgoingShipment
from .forms import CustomerForm, ProductTypeForm, IncomingShipmentForm, OutgoingShipmentForm
import xlsxwriter
import io
from django.contrib.auth.decorators import login_required
from .models import Price
from .forms import PriceForm

def customer_list(request):
    search_query = request.GET.get('search', '')
    customers = Customer.objects.all()
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(contact__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    paginator = Paginator(customers, 10)
    page = request.GET.get('page')
    customers = paginator.get_page(page)
    return render(request, 'inventory/customers.html', {'customers': customers, 'search_query': search_query})

def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '客户添加成功！')
                return redirect('inventory:customer_list')
            except Exception as e:
                messages.error(request, f'保存失败：{str(e)}')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': '添加客户'})

def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, '客户信息更新成功！')
            return redirect('inventory:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': '编辑客户'})

def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, '客户删除成功！')
        return redirect('inventory:customer_list')
    return render(request, 'inventory/customer_confirm_delete.html', {'customer': customer})

def product_list(request):
    search_query = request.GET.get('search', '')
    products = ProductType.objects.all().select_related('customer')
    if search_query:
        products = products.filter(
            Q(model_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'inventory/products.html', {'products': products, 'search_query': search_query})
    
    try:
        page_size = int(request.GET.get('page_size', 10))  # 允许自定义每页显示数量
        page_size = min(max(page_size, 1), 100)  # 限制范围在1-100之间
    except ValueError:
        page_size = 10
    
    paginator = Paginator(products, page_size)
    
    try:
        page = int(request.GET.get('page', 1))
        products = paginator.page(page)
    except:
        products = paginator.page(1)
    
    return render(request, 'inventory/products.html', {
        'products': products,
        'search_query': search_query,
        'page_size': page_size
    })

def price_list(request):
    search_query = request.GET.get('search', '')
    prices = Price.objects.all()  # 需要先创建 Price 模型
    if search_query:
        prices = prices.filter(
            Q(product__model_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    paginator = Paginator(prices, 10)
    page = request.GET.get('page')
    prices = paginator.get_page(page)
    return render(request, 'inventory/prices.html', {'prices': prices, 'search_query': search_query})
    
    try:
        page_size = int(request.GET.get('page_size', 10))  # 允许自定义每页显示数量
        page_size = min(max(page_size, 1), 100)  # 限制范围在1-100之间
    except ValueError:
        page_size = 10
    
    paginator = Paginator(products, page_size)
    
    try:
        page = int(request.GET.get('page', 1))
        products = paginator.page(page)
    except:
        products = paginator.page(1)
    
    return render(request, 'inventory/products.html', {
        'products': products,
        'search_query': search_query,
        'page_size': page_size
    })

def price_add(request):
    if request.method == 'POST':
        form = PriceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '价格信息添加成功！')
                return redirect('inventory:price_list')
            except Exception as e:
                messages.error(request, f'保存失败：{str(e)}')
    else:
        form = PriceForm()
    return render(request, 'inventory/price_form.html', {'form': form, 'title': '添加价格'})

def product_add(request):
    if request.method == 'POST':
        form = ProductTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '产品添加成功！')
            return redirect('inventory:product_list')
    else:
        form = ProductTypeForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': '添加产品'})

def product_edit(request, product_id):
    product = get_object_or_404(ProductType, id=product_id)
    if request.method == 'POST':
        form = ProductTypeForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '产品信息更新成功！')
            return redirect('inventory:product_list')
    else:
        form = ProductTypeForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': '编辑产品'})

def product_delete(request, product_id):
    product = get_object_or_404(ProductType, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, '产品删除成功！')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

def inbound_list(request):
    search_query = request.GET.get('search', '')
    inbounds = IncomingShipment.objects.all()
    if search_query:
        inbounds = inbounds.filter(
            Q(document_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    paginator = Paginator(inbounds, 10)
    page = request.GET.get('page')
    inbounds = paginator.get_page(page)
    return render(request, 'inventory/inbound_list.html', {'inbounds': inbounds, 'search_query': search_query})

def inbound_add(request):
    if request.method == 'POST':
        form = IncomingShipmentForm(request.POST)
        if form.is_valid():
            try:
                shipment = form.save(commit=False)
                if shipment.quantity <= 0:
                    messages.error(request, '入库数量必须大于0')
                    return render(request, 'inventory/inbound_form.html', {'form': form, 'title': '添加入库单'})
                shipment.save()
                messages.success(request, '入库单添加成功！')
                return redirect('inventory:inbound_list')
            except Exception as e:
                messages.error(request, f'保存失败：{str(e)}')
    else:
        form = IncomingShipmentForm()
    return render(request, 'inventory/inbound_form.html', {'form': form, 'title': '添加入库单'})

def inbound_detail(request, inbound_id):
    inbound = get_object_or_404(IncomingShipment, id=inbound_id)
    return render(request, 'inventory/inbound_detail.html', {'inbound': inbound})

def outbound_list(request):
    search_query = request.GET.get('search', '')
    outbounds = OutgoingShipment.objects.all()
    if search_query:
        outbounds = outbounds.filter(
            Q(document_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    paginator = Paginator(outbounds, 10)
    page = request.GET.get('page')
    outbounds = paginator.get_page(page)
    return render(request, 'inventory/outbound_list.html', {'outbounds': outbounds, 'search_query': search_query})

def outbound_add(request):
    if request.method == 'POST':
        form = OutgoingShipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '出库单添加成功！')
            return redirect('inventory:outbound_list')
    else:
        form = OutgoingShipmentForm()
    return render(request, 'inventory/outbound_form.html', {'form': form, 'title': '添加出库单'})

def outbound_detail(request, outbound_id):
    outbound = get_object_or_404(OutgoingShipment, id=outbound_id)
    return render(request, 'inventory/outbound_detail.html', {'outbound': outbound})

def export_customer_bill(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    outbounds = OutgoingShipment.objects.filter(customer=customer)
    
    # 创建Excel文件
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # 设置表头
    headers = ['单据编号', '产品型号', '数量', '单价', '总金额', '出库日期']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # 写入数据
    for row, outbound in enumerate(outbounds, 1):
        worksheet.write(row, 0, outbound.document_number)
        worksheet.write(row, 1, outbound.product_type.model_number)
        worksheet.write(row, 2, outbound.quantity)
        worksheet.write(row, 3, float(outbound.unit_price))
        worksheet.write(row, 4, float(outbound.total_amount))
        worksheet.write(row, 5, outbound.shipment_date.strftime('%Y-%m-%d'))
    
    workbook.close()
    output.seek(0)
    
    # 设置响应
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="bill_{customer_id}.xlsx"'
    return response


@login_required
def price_edit(request, price_id):
    price = get_object_or_404(Price, pk=price_id)
    if request.method == 'POST':
        form = PriceForm(request.POST, instance=price)
        if form.is_valid():
            form.save()
            return redirect('price_list')
    else:
        form = PriceForm(instance=price)
    return render(request, 'inventory/price_form.html', {
        'form': form,
        'title': '编辑价格记录'
    })

def batch_group_list(request):
    search_query = request.GET.get('search', '')
    batch_groups = BatchGroup.objects.all().select_related('customer')
    if search_query:
        batch_groups = batch_groups.filter(
            Q(batch_number__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    paginator = Paginator(batch_groups, 10)
    page = request.GET.get('page')
    batch_groups = paginator.get_page(page)
    return render(request, 'inventory/batch_groups.html', {
        'batch_groups': batch_groups, 
        'search_query': search_query
    })

def batch_group_add(request):
    if request.method == 'POST':
        form = BatchGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '批次组添加成功！')
            return redirect('inventory:batch_group_list')
    else:
        form = BatchGroupForm()
    return render(request, 'inventory/batch_group_form.html', {
        'form': form, 
        'title': '添加批次组'
    })

def batch_group_edit(request, group_id):
    batch_group = get_object_or_404(BatchGroup, id=group_id)
    if request.method == 'POST':
        form = BatchGroupForm(request.POST, instance=batch_group)
        if form.is_valid():
            form.save()
            messages.success(request, '批次组更新成功！')
            return redirect('inventory:batch_group_list')
    else:
        form = BatchGroupForm(instance=batch_group)
    return render(request, 'inventory/batch_group_form.html', {
        'form': form, 
        'title': '编辑批次组'
    })

def export_monthly_bill(request, customer_id, year, month):
    customer = get_object_or_404(Customer, id=customer_id)
    start_date = datetime.date(year, month, 1)
    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    
    outbounds = OutgoingShipment.objects.filter(
        customer=customer,
        shipment_date__range=[start_date, end_date]
    ).order_by('shipment_date')
    
    # 创建Excel文件
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # 设置表头样式
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # 设置单元格样式
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # 写入标题
    worksheet.merge_range('A1:G1', f'{year}年{month}月份对账单', header_format)
    worksheet.write('A2', f'客户：{customer.name}', cell_format)
    worksheet.write('D2', f'起止日期：{start_date.strftime("%Y/%m/%d")}-{end_date.strftime("%Y/%m/%d")}', cell_format)
    worksheet.write('F2', '月结方式：当月结', cell_format)
    worksheet.write('G2', '币别：人民币', cell_format)
    
    # 设置表头
    headers = ['日期', '送单号码', '批号', '品名规格', '数量(K)', '脚距(mm)', '单价', '金额']
    for col, header in enumerate(headers):
        worksheet.write(3, col, header, header_format)
    
    # 写入数据
    row = 4
    total_amount = 0
    for outbound in outbounds:
        worksheet.write(row, 0, outbound.shipment_date.strftime('%Y/%m/%d'), cell_format)
        worksheet.write(row, 1, outbound.document_number, cell_format)
        worksheet.write(row, 2, outbound.batch_group.batch_number if hasattr(outbound, 'batch_group') else '', cell_format)
        worksheet.write(row, 3, outbound.product_type.model_number, cell_format)
        worksheet.write(row, 4, outbound.quantity, cell_format)
        worksheet.write(row, 5, outbound.batch_group.pin_pitch if hasattr(outbound, 'batch_group') else '', cell_format)
        worksheet.write(row, 6, float(outbound.unit_price), cell_format)
        worksheet.write(row, 7, float(outbound.total_amount), cell_format)
        total_amount += float(outbound.total_amount)
        row += 1
    
    # 写入合计
    worksheet.write(row, 6, '合计：', header_format)
    worksheet.write(row, 7, total_amount, header_format)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{customer.name}_{year}{month}月账单.xlsx"'
    return response