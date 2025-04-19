from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField('供应商名称', max_length=100)
    contact = models.CharField('联系人', max_length=50, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    address = models.TextField('地址', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = '供应商'

class Customer(models.Model):
    name = models.CharField('客户名称', max_length=100)
    contact = models.CharField('联系人', max_length=50, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    address = models.TextField('地址', blank=True)
    batch_number = models.CharField('批号', max_length=50, blank=True)
    model_spec = models.CharField('型号规格', max_length=100, blank=True)
    pin_pitch = models.CharField('针距', max_length=50, blank=True)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'

class ProductType(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    name = models.CharField('型号名称', max_length=100)
    model_number = models.CharField('型号', max_length=100)
    barcode = models.CharField('条形码', max_length=50, blank=True)
    description = models.TextField('描述', blank=True)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.customer.name} - {self.model_number}'

    class Meta:
        verbose_name = '产品型号'
        verbose_name_plural = '产品型号'

class Inventory(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    batch_number = models.CharField('批号', max_length=50)
    quantity = models.IntegerField('数量')
    location = models.CharField('存储位置', max_length=100, blank=True)
    created_at = models.DateTimeField('入库时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f'{self.product_type} - {self.batch_number}'

    class Meta:
        verbose_name = '库存'
        verbose_name_plural = '库存'
        unique_together = ['product_type', 'batch_number']

class InventoryRecord(models.Model):
    INVENTORY_TYPE_CHOICES = [
        ('IN', '入库'),
        ('OUT', '出库'),
    ]

    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    batch_number = models.CharField('批号', max_length=50)
    change_type = models.CharField('变动类型', max_length=3, choices=INVENTORY_TYPE_CHOICES)
    quantity = models.IntegerField('变动数量')
    document_number = models.CharField('单据编号', max_length=50, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('变动时间', auto_now_add=True)

    def __str__(self):
        return f"{self.product_type.model_number} - {self.batch_number} - {self.change_type} - {self.quantity}"

    class Meta:
        verbose_name = '库存变动记录'
        verbose_name_plural = '库存变动记录'

class IncomingShipment(models.Model):
    document_number = models.CharField('单据编号', max_length=50)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='供应商')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    batch_number = models.CharField('批号', max_length=50)
    quantity = models.IntegerField('数量')
    shipment_date = models.DateField('来料日期', default=timezone.now)
    notes = models.TextField('备注', blank=True)
    AUDIT_STATUS_CHOICES = [
        ('PENDING', '待审核'),
        ('APPROVED', '已审核'),
        ('REJECTED', '已驳回'),
    ]
    audit_status = models.CharField('审核状态', max_length=10, choices=AUDIT_STATUS_CHOICES, default='PENDING')
    auditor = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审核人')
    audit_time = models.DateTimeField('审核时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.document_number} - {self.customer.name}'

    class Meta:
        verbose_name = '来料单据'
        verbose_name_plural = '来料单据'

class Price(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    effective_date = models.DateField('生效日期', default=timezone.now)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.product_type} - {self.unit_price}'

    class Meta:
        verbose_name = '价格记录'
        verbose_name_plural = '价格记录'

class BatchGroup(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    batch_number = models.CharField('批号', max_length=50)
    model_number = models.CharField('型号', max_length=100)
    pin_pitch = models.CharField('针距', max_length=50, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.customer.name} - {self.batch_number}'

    class Meta:
        verbose_name = '批次组'
        verbose_name_plural = '批次组'

class OutgoingShipment(models.Model):
    document_number = models.CharField('单据编号', max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name='产品型号')
    batch_number = models.CharField('批号', max_length=50)
    shipment_date = models.DateField('出货日期', default=timezone.now)
    order_number = models.CharField('选单号码', max_length=50, blank=True)  # 添加选单号码字段
    quantity = models.IntegerField('数量')
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2)
    pin_pitch = models.CharField('脚距', max_length=50, blank=True)
    unit_weight = models.DecimalField('单重(g)', max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    batch_group = models.ForeignKey(BatchGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='批次组')
    # 保持原有字段
    AUDIT_STATUS_CHOICES = [
        ('PENDING', '待审核'),
        ('APPROVED', '已审核'),
        ('REJECTED', '已驳回'),
    ]
    audit_status = models.CharField('审核状态', max_length=10, choices=AUDIT_STATUS_CHOICES, default='PENDING')
    auditor = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审核人')
    audit_time = models.DateTimeField('审核时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def save(self, *args, **kwargs):
        # 自动计算总金额
        if self.unit_price and self.quantity:
            self.total_amount = self.quantity * self.unit_price
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer.name} - {self.product_type}'

    class Meta:
        verbose_name = '出货单据'
        verbose_name_plural = '出货单据'

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=IncomingShipment)
def update_inventory_on_incoming(sender, instance, created, **kwargs):
    if created:
        # 创建库存记录或更新库存数量
        inventory, created = Inventory.objects.get_or_create(
            product_type=instance.product_type,
            batch_number=instance.batch_number,
            defaults={'quantity': 0}  # 初始化数量为0
        )
        inventory.quantity += instance.quantity
        inventory.save()

        # 创建库存变动记录
        InventoryRecord.objects.create(
            product_type=instance.product_type,
            batch_number=instance.batch_number,
            change_type='IN',
            quantity=instance.quantity,
            document_number=instance.document_number,
            notes=f"来料单据 {instance.document_number}"
        )

@receiver(post_save, sender=OutgoingShipment)
def update_inventory_on_outgoing(sender, instance, created, **kwargs):
    if created:
        try:
            # 根据批号和产品规格查找相关库存
            inventory_items = Inventory.objects.filter(
                batch_number=instance.batch_number,
                product_type__model_number=instance.product_type.model_number
            )
            
            if inventory_items.exists():
                inventory = inventory_items.first()
                inventory.quantity -= instance.quantity
                inventory.save()

                # 创建库存变动记录
                InventoryRecord.objects.create(
                    product_type=instance.product_type,
                    batch_number=instance.batch_number,
                    change_type='OUT',
                    quantity=instance.quantity,
                    document_number=instance.document_number,
                    notes=f"出货单据 - {instance.customer.name} - {instance.document_number}"
                )
        except Exception as e:
            print(f"Error updating inventory: {str(e)}")

class OperationLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name='操作用户')
    model_name = models.CharField('模型名称', max_length=100)
    object_id = models.IntegerField('对象ID')
    action = models.CharField('操作类型', max_length=50)  # 例如: 'CREATE', 'UPDATE', 'DELETE'
    changes = models.JSONField('变更内容', blank=True, null=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name} - {self.object_id}"

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']