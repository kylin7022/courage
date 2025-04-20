from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
from django.contrib import messages
import csv
import datetime
from decimal import Decimal
from django.urls import reverse
from django.http import HttpResponse
import xlsxwriter
from io import BytesIO
from datetime import datetime

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
import xlwt  # 添加到文件顶部的导入语句中

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
        print("POST data:", request.POST)  # 添加调试信息
        if form.is_valid():
            try:
                print("Form is valid, cleaned data:", form.cleaned_data)  # 添加调试信息
                customer = form.save()
                messages.success(request, '客户添加成功！')
                return redirect('inventory:customer_list')
            except Exception as e:
                print(f"Error saving customer: {str(e)}")  # 添加调试信息
                messages.error(request, f'保存失败：{str(e)}')
        else:
            print("Form errors:", form.errors)  # 添加调试信息
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {
        'form': form, 
        'title': '添加客户',
        'submit_url': reverse('inventory:customer_add')
    })

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
        print("收到的POST数据:", request.POST)  # 调试信息
        form = OutgoingShipmentForm(request.POST)
        if form.is_valid():
            print("表单验证通过，清理后的数据:", form.cleaned_data)  # 调试信息
            outbound = form.save(commit=False)
            
            # 如果品名规格未填写，但已选择产品型号，则自动填写
            if not outbound.product_spec and outbound.product_type:
                product_type = outbound.product_type
                outbound.product_spec = f"{product_type.name} - {product_type.description}"
            
            # 确保批次组名称被正确保存
            batch_group_name = form.cleaned_data.get('batch_group_name')
            print("批次组名称:", batch_group_name)  # 调试信息
            outbound.batch_group_name = batch_group_name
            
            print("保存前的出库单对象:", vars(outbound))  # 调试信息
            outbound.save()
            print("保存后的出库单对象:", vars(outbound))  # 调试信息
            
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
    
    # 添加调试信息，检查所有出货记录
    all_shipments = OutgoingShipment.objects.all()
    print(f"数据库中所有出货记录数量: {all_shipments.count()}")
    for shipment in all_shipments:
        print(f"出货记录: ID={shipment.id}, 客户ID={shipment.customer_id}, 客户名={shipment.customer.name}")
    
    # 获取该客户的所有出货记录
    # 修改查询条件，添加审核状态过滤
    outgoing_shipments = OutgoingShipment.objects.filter(
        customer=customer,
        audit_status='APPROVED'  # 只导出已审核的记录
    ).order_by('-created_at')
    
    print(f"客户 {customer.name} 的出货记录数量: {outgoing_shipments.count()}")
    
    # 添加更详细的调试信息
    print(f"SQL查询: {outgoing_shipments.query}")
    print(f"记录数量: {outgoing_shipments.count()}")
    
    # 检查每条记录
    for shipment in outgoing_shipments:
        print(f"出货记录: ID={shipment.id}, 日期={shipment.shipment_date}, 客户={shipment.customer.name}")
    
    # 创建新的Excel工作簿和工作表
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('出货记录')
    
    # 设置标题样式
    title_style = xlwt.easyxf('font: bold on')
    
    # 写入表头
    headers = ['出货日期', '型号', '品名规格', '批号', '批次组', '针距', '数量', '单价', '总金额', '备注']
    for col, header in enumerate(headers):
        ws.write(0, col, header, title_style)
    
    # 写入数据行（添加空值保护）
    for row, shipment in enumerate(outgoing_shipments, start=1):
        try:
            # 获取关联数据时添加空值判断
            product_type = getattr(shipment, 'product_type', None)
            model_number = product_type.model_number if product_type else ''
            
            ws.write(row, 0, shipment.shipment_date.strftime('%Y-%m-%d') if shipment.shipment_date else '')
            ws.write(row, 1, model_number)  # 型号
            ws.write(row, 2, shipment.product_spec or '')
            ws.write(row, 3, shipment.batch_number or '')
            ws.write(row, 4, shipment.batch_group_name or '')  # 直接使用字符型字段
            ws.write(row, 5, shipment.pin_pitch or '')
            ws.write(row, 6, shipment.quantity or 0)
            ws.write(row, 7, float(shipment.unit_price) if shipment.unit_price else 0.00)
            ws.write(row, 8, float(shipment.total_amount) if shipment.total_amount else 0.00)
            ws.write(row, 9, shipment.notes or '')
        except Exception as e:
            print(f"写入行 {row} 时出错: {str(e)}")
            raise  # 添加异常抛出以便调试

    # 设置列宽
    for col in range(len(headers)):
        ws.col(col).width = 256 * 15  # 15个字符宽度
    
    # 创建响应
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{customer.name}_出货记录.xls"'
    
    # 保存Excel文件
    wb.save(response)
    return response

def export_monthly_bill(request, customer_id):
    # 添加异常处理确保日期参数有效
    try:
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    except (TypeError, ValueError) as e:
        return HttpResponse(f"日期格式错误: {str(e)}", status=400)
    
    # 添加更详细的调试日志
    print(f"转换后的日期参数 - 开始: {start_date}(类型: {type(start_date)}), 结束: {end_date}(类型: {type(end_date)})")
    
    # 获取数据时添加select_related提升性能
    shipments = OutgoingShipment.get_monthly_bill_data(customer_id, start_date, end_date)\
        .select_related('customer', 'product_type')
    
    # 添加调试信息
    print(f"有效出货单数量: {shipments.count()}")
    for shipment in shipments[:3]:  # 打印前3条记录
        print(f"出货单ID: {shipment.id}, 审核状态: {shipment.audit_status}, 日期: {shipment.shipment_date}")
    
    # 获取数据
    shipments = OutgoingShipment.get_monthly_bill_data(customer_id, start_date, end_date)
    customer = Customer.objects.get(id=customer_id)
    
    # 创建Excel文件
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # 设置样式
    title_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 12
    })
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'border': 1
    })
    cell_format = workbook.add_format({
        'align': 'center',
        'border': 1
    })
    
    # 写入标题（修复日期格式）
    worksheet.merge_range('A1:H1', 
                         f'{end_date.year}年{end_date.month:02d}月份对账单',  # 使用datetime属性
                         title_format)
    worksheet.write('A2', f'客户：{customer.name}', workbook.add_format({'bold': True}))
    worksheet.write('E2', 
                   f'起止日期：{start_date.strftime("%Y-%m-%d")}~{end_date.strftime("%Y-%m-%d")}',  # 使用strftime格式化
                   workbook.add_format({'bold': True}))
    
    # 写入表头
    headers = ['日期', '送单号码', '批号', '品名规格', '数量(k)', '脚距(mm)', '单价', '金额']
    for col, header in enumerate(headers):
        worksheet.write(3, col, header, header_format)
    
    # 写入数据
    row = 4
    total_amount = 0
    for shipment in shipments:
        data = shipment.to_bill_dict()  # 添加缩进
        worksheet.write(row, 0, data['date'].strftime('%Y-%m-%d'), cell_format)
        worksheet.write(row, 1, data['document_number'], cell_format)
        worksheet.write(row, 2, data['batch_number'], cell_format)
        worksheet.write(row, 3, data['product_spec'], cell_format)
        worksheet.write(row, 4, data['quantity'], cell_format)
        worksheet.write(row, 5, data['pin_pitch'], cell_format)
        worksheet.write(row, 6, float(data['unit_price']), cell_format)
        worksheet.write(row, 7, float(data['total_amount']), cell_format)
        total_amount += float(data['total_amount'])
        row += 1
    
    # 写入合计
    worksheet.write(row, 6, '合计：', header_format)
    worksheet.write(row, 7, total_amount, header_format)
    
    # 设置列宽
    worksheet.set_column('A:A', 12)  # 日期
    worksheet.set_column('B:B', 15)  # 送单号码
    worksheet.set_column('C:C', 12)  # 批号
    worksheet.set_column('D:D', 20)  # 品名规格
    worksheet.set_column('E:H', 10)  # 其他列
    
    workbook.close()
    
    # 准备响应
    output.seek(0)
    # 修复文件名中的日期格式
    filename = f"{customer.name}_{end_date.year}年{end_date.month:02d}月对账单.xlsx"
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
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