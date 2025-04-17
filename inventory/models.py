from django.db import models

class Customer(models.Model):
    name = models.CharField('客户名称', max_length=100)
    contact = models.CharField('联系人', max_length=50, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    address = models.TextField('地址', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'

class ProductType(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    model_number = models.CharField('型号', max_length=100)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f'{self.customer.name} - {self.model_number}'

    class Meta:
        verbose_name = '产品型号'
        verbose_name_plural = '产品型号'
        unique_together = ['customer', 'model_number']

class IncomingShipment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    quantity = models.IntegerField('数量')
    shipment_date = models.DateField('来料日期')
    document_number = models.CharField('单据编号', max_length=50)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f'{self.document_number} - {self.customer.name}'

    class Meta:
        verbose_name = '来料单据'
        verbose_name_plural = '来料单据'

class OutgoingShipment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    quantity = models.IntegerField('数量')
    shipment_date = models.DateField('出货日期')
    document_number = models.CharField('单据编号', max_length=50)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def save(self, *args, **kwargs):
        self.unit_price = self.product_type.unit_price
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.document_number} - {self.customer.name}'

    class Meta:
        verbose_name = '出货单据'
        verbose_name_plural = '出货单据'


# inventory/models.py
class Price(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    effective_date = models.DateField('生效日期')

    def __str__(self):
        return f"{self.product_type.model_number} - {self.price}"

    class Meta:
        verbose_name = '价格记录'
        verbose_name_plural = '价格记录'


class BatchGroup(models.Model):
    batch_number = models.CharField('批号', max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    model_number = models.CharField('型号', max_length=100)
    pin_pitch = models.CharField('脚距', max_length=50)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.customer.name} - {self.batch_number} - {self.model_number}'

    class Meta:
        verbose_name = '批次组'
        verbose_name_plural = '批次组'
        unique_together = ['customer', 'batch_number', 'model_number']
