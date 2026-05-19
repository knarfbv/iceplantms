from django import forms
from .models import IceProduct, Inventory, Customer, Order, OrderItem

class IceProductForm(forms.ModelForm):
    class Meta:
        model = IceProduct
        fields = ['name', 'size', 'price']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'quantity']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'phone']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']