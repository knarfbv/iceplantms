from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import IceProduct, Inventory, Customer, Order, OrderItem
from .forms import IceProductForm, InventoryForm, CustomerForm, OrderForm, OrderItemForm

# Create your views here.

def product_list(request):
    products = IceProduct.objects.all()
    return render(request, 'products/list.html', {'products': products})

def product_add(request):
    form = IceProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'products/form.html', {'form': form})

def product_edit(request, pk):
    product = get_object_or_404(IceProduct, pk=pk)
    form = IceProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'products/form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(IceProduct, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/delete.html', {'product': product})


def inventory_list(request):
    inventory = Inventory.objects.select_related('product').all()
    return render(request, 'inventory/list.html', {'inventory': inventory})

def inventory_add(request):
    form = InventoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('inventory_list')
    return render(request, 'inventory/form.html', {'form': form})

def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    form = InventoryForm(request.POST or None, instance=inventory)
    if form.is_valid():
        form.save()
        return redirect('inventory_list')
    return render(request, 'inventory/form.html', {'form': form})


def customer_list(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query)
        )
    else:
        customers = Customer.objects.all()
    return render(request, 'customers/list.html', {'customers': customers, 'query': query})

def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'customers/form.html', {'form': form})

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'customers/form.html', {'form': form})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'customers/delete.html', {'customer': customer})


def order_list(request):
    query = request.GET.get('q', '')
    orders = Order.objects.select_related('customer')
    if query:
        orders = orders.filter(
            Q(id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(status__icontains=query)
        )
    orders = orders.all()
    return render(request, 'orders/list.html', {'orders': orders, 'query': query})

def order_add(request):
    form = OrderForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('order_detail', pk=form.instance.pk)
    return render(request, 'orders/form.html', {'form': form})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product').all()
    return render(request, 'orders/detail.html', {'order': order, 'items': items})

def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            return redirect('order_detail', pk=pk)
    return redirect('order_detail', pk=pk)

def order_item_add(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    form = OrderItemForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.order = order
        item.save()
        inventory = get_object_or_404(Inventory, product=item.product)
        inventory.quantity -= item.quantity
        inventory.save()
        return redirect('order_detail', pk=order_pk)
    return render(request, 'orders/item_form.html', {'form': form, 'order': order})

def order_item_edit(request, order_pk, pk):
    order = get_object_or_404(Order, pk=order_pk)
    item = get_object_or_404(OrderItem, pk=pk, order=order)
    form = OrderItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('order_detail', pk=order_pk)
    return render(request, 'orders/item_form.html', {'form': form, 'order': order, 'item': item})

def order_item_delete(request, order_pk, pk):
    order = get_object_or_404(Order, pk=order_pk)
    item = get_object_or_404(OrderItem, pk=pk, order=order)
    if request.method == 'POST':
        item.delete()
        return redirect('order_detail', pk=order_pk)
    return redirect('order_detail', pk=order_pk)