from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from io import BytesIO
from datetime import datetime
from .models import (
    Customer, 
    ProductType,
    IncomingShipment,
    OutgoingShipment,
    Inventory,
    Price
)
from .forms import (
    CustomerForm,
    ProductTypeForm,
    IncomingShipmentForm,
    OutgoingShipmentForm,
    PriceForm
)
import xlsxwriter

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'inventory/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '客户创建成功！')
            return redirect('inventory:customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'inventory/customer_form.html', {
        'form': form,
        'title': '添加客户'
    })

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, '客户信息更新成功！')
            return redirect('inventory:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'inventory/customer_form.html', {
        'form': form,
        'title': '编辑客户'
    })

@login_required
def customer_delete(request, pk):  # Changed parameter name to match URL pattern
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, '客户删除成功！')
        return redirect('inventory:customer_list')
    return render(request, 'inventory/confirm_delete.html', {'object': customer, 'title': '删除客户'})

# 入库单据管理
@login_required
def inbound_list(request):
    inbound_list = IncomingShipment.objects.all().order_by('-created_at')
    paginator = Paginator(inbound_list, 10)  # 每页显示10条记录
    
    page = request.GET.get('page')
    inbound_shipments = paginator.get_page(page)
    
    return render(request, 'inventory/inbound_list.html', {
        'inbound_shipments': inbound_shipments
    })

@login_required
def inbound_add(request):
    if request.method == 'POST':
        form = IncomingShipmentForm(request.POST)
        print("POST data:", request.POST)  # Debug info
        if form.is_valid():
            try:
                print("Form is valid, cleaned data:", form.cleaned_data)  # Debug cleaned data
                inbound = form.save(commit=False)
                print("Inbound object before save:", vars(inbound))  # Debug object state
                inbound.save()
                print("Inbound saved successfully")  # Confirm save
                
                # Create inventory record
                inventory, created = Inventory.objects.get_or_create(
                    product_type=inbound.product_type,
                    batch_number=inbound.batch_number,
                    defaults={'quantity': 0}
                )
                inventory.quantity += inbound.quantity
                inventory.save()
                print("Inventory updated successfully")  # Confirm inventory update
                
                messages.success(request, '入库单据添加成功！')
                return redirect('inventory:inbound_list')
            except Exception as e:
                print(f"Error saving inbound: {str(e)}")  # Debug error
                messages.error(request, f'保存失败：{str(e)}')
        else:
            print("Form errors:", form.errors)  # Debug form errors
            messages.error(request, '表单验证失败，请检查输入！')
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
    # 添加排序并确保获取所有相关字段
    outbound_shipments = OutgoingShipment.objects.all().select_related(
        'customer', 
        'product_type'
    ).order_by('-created_at')
    
    # 添加调试信息
    print("查询到的出库单数量:", outbound_shipments.count())
    for shipment in outbound_shipments:
        print(f"出库单ID: {shipment.id}, 单号: {shipment.document_number}")
    
    return render(request, 'inventory/outbound_list.html', {
        'outbound_shipments': outbound_shipments
    })

@login_required
def outbound_add(request):
    if request.method == 'POST':
        form = OutgoingShipmentForm(request.POST)
        if form.is_valid():
            outbound = form.save(commit=False)
            # 自动计算总金额
            outbound.total_amount = outbound.quantity * outbound.unit_price
            # 设置默认审核状态
            outbound.audit_status = 'PENDING'  
            outbound.save()
            messages.success(request, '出库单据添加成功！')
            return redirect('inventory:outbound_list')
        else:
            print("表单验证错误:", form.errors)  # 调试信息
            messages.error(request, '表单验证失败，请检查输入！')
    else:
        form = OutgoingShipmentForm()
    
    return render(request, 'inventory/outbound_form.html', {
        'form': form,
        'title': '添加出库单据'
    })

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
        product_type.soft_delete()  # 使用软删除方法
        messages.success(request, '产品型号已删除')
        return redirect('inventory:product_type_list')
    return render(request, 'inventory/confirm_delete.html', 
                 {'object': product_type, 'title': '删除产品型号'})

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


def get_customers_for_export(request):
    """获取客户列表用于导出功能"""
    customers = Customer.objects.all().order_by('name')
    return JsonResponse({
        'customers': list(customers.values('id', 'name'))
    })


@login_required
def export_monthly_bill(request, customer_id):
    """导出客户对账单"""
    customer = get_object_or_404(Customer, id=customer_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        # 添加更严格的日期校验
        if not all([start_date, end_date]):
            return HttpResponse("必须同时提供开始日期和结束日期", status=400)
            
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # 添加调试日志
        print(f"导出条件检查 - 客户: {customer.name}")
        print(f"日期范围: {start_date} 至 {end_date}")
        
        # 修正查询条件（使用实际数据库中的状态值）
        records = OutgoingShipment.objects.filter(
            customer=customer,
            shipment_date__range=[start_date, end_date],
            audit_status='PENDING'  # 改为实际存在的状态值
        ).order_by('shipment_date')
        
        print(f"实际查询条件: customer={customer.id} status=PENDING date_range={start_date}-{end_date}")
        print(f"找到 {records.count()} 条记录")
        
        if not records.exists():
            return HttpResponse("没有找到符合条件的出库记录", status=404)

        # 创建Excel文件（添加字段存在性校验）
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # 设置标题格式
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'border': 1
        })
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'border': 1
        })
        
        # 添加标题行（动态填充客户和日期）
        worksheet.merge_range(1, 0, 1, 1, f'客户：{customer.name}', header_format)  # A2-B2合并带客户名称
        worksheet.merge_range(1, 2, 1, 4, f'起止日期：{start_date} - {end_date}', header_format)  # C2-E2合并带日期
        worksheet.merge_range(1, 5, 1, 6, '月结方式：', header_format)  # F2-G2合并
        worksheet.write(1, 7, '币别：', header_format)  # H2

        # 写入表头（从第2行开始保持不变）
        headers = ['日期', '送单号码', '批号', '品名规格', '数量(K)', '脚距(mm)', '单价', '金额']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)  # 第三行

        # 调整数据写入起始行（原1改为3）
        for row, record in enumerate(records, start=3):  # 数据从第4行开始
            # 添加字段调试信息
            print(f"记录 {row} 批号: {record.batch_number} 数量: {record.quantity}")
            
            worksheet.write(row, 0, record.shipment_date.strftime('%Y-%m-%d') if record.shipment_date else '')
            worksheet.write(row, 1, record.order_number or '未录入')
            worksheet.write(row, 2, record.batch_number or 'N/A')
            worksheet.write(row, 3, record.product_spec or (record.product_type.name if record.product_type else '未知型号'))
            worksheet.write_number(row, 4, float(record.quantity) if record.quantity and record.quantity > 0 else 0.0)
            worksheet.write(row, 5, str(record.pin_pitch) if record.pin_pitch else '')
            worksheet.write_number(row, 6, float(record.unit_price) if record.unit_price else 0.0)
            worksheet.write_number(row, 7, float(record.total_amount) if record.total_amount else 0.0)
        
        workbook.close()
        
        # 设置响应头
        output.seek(0)
        filename = f"{customer.name}_对账单_{start_date}至{end_date}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return HttpResponse(f"导出失败: {str(e)}", status=500)


@login_required
def export_delivery_note(request, customer_id):
    """导出客户出货单"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 修改查询条件（添加更多状态支持）
    records = OutgoingShipment.objects.filter(
        customer=customer,
        audit_status__in=['APPROVED', 'PENDING'],
        quantity__gt=0
    ).order_by('-shipment_date').select_related('product_type')[:50]
    
    print(f"导出记录数: {records.count()}")
    if records:
        print(f"示例记录批号: {records[0].batch_number}")

    # 创建Excel文件
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # 设置标题格式
    title_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 14,
        'border': 1
    })
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'border': 1
    })
    
    # 添加标题行
    worksheet.merge_range(0, 1, 0, 2, '出货明细', title_format)  # B1-C1合并
    worksheet.write(0, 3, '送货单号：')  # D1
    worksheet.write(1, 0, f'客户名称：{customer.name}')  # A2
    worksheet.write(1, 3, f'出货日期：{datetime.now().strftime("%Y-%m-%d")}')  # D2
    
    # 写入表头（从第2行开始）
    headers = ['批号', '品名规格', '数量', '单重', '备注']
    for col, header in enumerate(headers):
        worksheet.write(2, col, header, header_format)  # 第三行
    
    # 调整数据写入起始行（原1改为3）
    for row, record in enumerate(records, start=3):  # 数据从第4行开始
        # 字段验证调试
        print(f"记录 {row} 字段验证:")
        print(f"unit_weight 存在: {hasattr(record, 'unit_weight')}")
        print(f"unit_price 存在: {hasattr(record, 'unit_price')}")
        
        # 处理品名规格
        product_spec = record.product_spec or f"{record.product_type.name} {record.product_type.description or ''}".strip()
        
        # 写入数据（添加空值处理）
        worksheet.write(row, 0, record.batch_number or 'N/A')
        worksheet.write(row, 1, product_spec or '未指定规格')
        worksheet.write_number(row, 2, float(record.quantity) if record.quantity else 0.0)
        worksheet.write_number(row, 3, float(record.unit_price) if record.unit_price else 0.0)
        worksheet.write(row, 4, record.notes or '')
    
    # 添加底部签名（在所有数据行之后）
    last_row = 3 + len(records)  # 计算最后一行号
    worksheet.write(last_row + 1, 0, '制单')   # 批号列底部
    worksheet.write(last_row + 1, 3, '签收')   # 单重列底部
    
    workbook.close()
    
    # 处理空数据情况
    if records.count() == 0:
        return HttpResponse("当前没有可导出的出货记录", status=404)
    
    output.seek(0)
    filename = f"{customer.name}_出货单_{datetime.now().strftime('%Y%m%d')}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_management(request):
    """导出管理页面视图"""
    return render(request, 'inventory/export_management.html', {
        'title': '导出管理'
    })


# Add this at the beginning of the file, with other imports
def home(request):
    """
    首页视图函数
    """
    return render(request, 'home.html')