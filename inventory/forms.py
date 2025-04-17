from django import forms
from .models import (
    Customer, 
    ProductType, 
    IncomingShipment, 
    OutgoingShipment, 
    Price,
    BatchGroup
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'})
        }

class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['customer', 'model_number', 'unit_price']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'})
        }

class IncomingShipmentForm(forms.ModelForm):
    class Meta:
        model = IncomingShipment
        fields = ['document_number', 'customer', 'product_type', 'quantity', 'shipment_date']
        widgets = {
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

class OutgoingShipmentForm(forms.ModelForm):
    class Meta:
        model = OutgoingShipment
        fields = ['document_number', 'customer', 'product_type', 'quantity', 'shipment_date']
        widgets = {
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

class BatchGroupForm(forms.ModelForm):
    class Meta:
        model = BatchGroup
        fields = ['batch_number', 'customer', 'model_number', 'pin_pitch', 'description']
        widgets = {
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_pitch': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

from .models import Price

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['product_type', 'price', 'effective_date']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }