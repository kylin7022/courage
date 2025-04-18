from .models import Customer

def customers_processor(request):
    """
    添加客户列表到所有模板的上下文中
    """
    return {
        'customers': Customer.objects.all().order_by('name')
    } 