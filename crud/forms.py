from django import forms
from .models import Inventory, Customer, Order, OrderItem

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'size', 'price']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'phone']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer']

class OrderItemForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']