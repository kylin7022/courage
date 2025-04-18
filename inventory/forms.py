from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Customer, 
    Supplier, 
    ProductType, 
    IncomingShipment, 
    OutgoingShipment, 
    Price,
    BatchGroup,
    Inventory
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact', 'phone', 'address', 'batch_number', 'model_spec', 'pin_pitch', 'unit_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'model_spec': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_pitch': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['customer', 'name', 'model_number', 'barcode', 'description', 'unit_price']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }

class IncomingShipmentForm(forms.ModelForm):
    class Meta:
        model = IncomingShipment
        fields = ['document_number', 'supplier', 'customer', 'product_type', 'batch_number', 'quantity', 'shipment_date', 'notes']
        widgets = {
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'shipment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError('数量必须大于0')
        return quantity

class OutgoingShipmentForm(forms.ModelForm):
    class Meta:
        model = OutgoingShipment
        fields = ['document_number', 'customer', 'product_type', 'batch_number', 'quantity', 'unit_price']
        widgets = {
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError('数量必须大于0')
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        product_type = cleaned_data.get('product_type')
        batch_number = cleaned_data.get('batch_number')
        quantity = cleaned_data.get('quantity')

        if product_type and batch_number and quantity:
            try:
                inventory = Inventory.objects.get(
                    product_type=product_type,
                    batch_number=batch_number
                )
                if inventory.quantity < quantity:
                    raise ValidationError({
                        'quantity': f'库存不足。当前库存: {inventory.quantity}'
                    })
            except Inventory.DoesNotExist:
                raise ValidationError({
                    'batch_number': f'找不到批号为 {batch_number} 的库存记录'
                })

        return cleaned_data

class BatchGroupForm(forms.ModelForm):
    class Meta:
        model = BatchGroup
        fields = ['customer', 'batch_number', 'model_number', 'pin_pitch']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_pitch': forms.TextInput(attrs={'class': 'form-control'})
        }

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['product_type', 'unit_price', 'effective_date', 'notes']
        widgets = {
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }   