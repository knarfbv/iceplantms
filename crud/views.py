from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Inventory, Customer, Order, OrderItem
from .forms import InventoryForm, CustomerForm, OrderForm, OrderItemForm

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('order_list')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('order_list')
        return render(request, 'auth/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def inventory_list(request):
    items = Inventory.objects.all()
    return render(request, 'inventory/list.html', {'items': items})

def inventory_add(request):
    form = InventoryForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.quantity = 0
        item.save()
        return redirect('inventory_list')
    return render(request, 'inventory/form.html', {'form': form})

@login_required(login_url='login')
def inventory_edit(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    form = InventoryForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('inventory_list')
    return render(request, 'inventory/form.html', {'form': form})

@login_required(login_url='login')
def inventory_delete(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory_list')
    return render(request, 'inventory/delete.html', {'item': item})

@login_required(login_url='login')
def inventory_update_stock(request, pk):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item = get_object_or_404(Inventory, pk=pk)
        quantity = int(data.get('quantity') or 0)
        if quantity >= 0:
            item.quantity = quantity
            item.save()
            return JsonResponse({'success': True, 'quantity': item.quantity})
        return JsonResponse({'success': False, 'error': 'Invalid quantity'})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required(login_url='login')
def customer_list(request):
    query = request.GET.get('q', '')
    if query:
        customers_list = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query)
        )
    else:
        customers_list = Customer.objects.all()

    paginator = Paginator(customers_list, 10)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)

    return render(request, 'customers/list.html', {'customers': customers, 'query': query})

@login_required(login_url='login')
def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'customers/form.html', {'form': form})

@login_required(login_url='login')
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'customers/form.html', {'form': form})

@login_required(login_url='login')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'customers/delete.html', {'customer': customer})


@login_required(login_url='login')
def order_list(request):
    query = request.GET.get('q', '')
    orders_list = Order.objects.select_related('customer')
    if query:
        orders_list = orders_list.filter(
            Q(id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(status__icontains=query)
        )

    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    return render(request, 'orders/list.html', {'orders': orders, 'query': query})

@login_required(login_url='login')
def order_add(request):
    form = OrderForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('order_detail', pk=form.instance.pk)
    return render(request, 'orders/form.html', {'form': form})

@login_required(login_url='login')
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('item').all()
    return render(request, 'orders/detail.html', {'order': order, 'items': items})

@login_required(login_url='login')
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status not in ['pending', 'cancelled']:
        return redirect('order_detail', pk=pk)
    if request.method == 'POST':
        if order.status == 'pending':
            for order_item in order.items.select_related('item').all():
                order_item.item.quantity += order_item.quantity
                order_item.item.save()
        order.delete()
        return redirect('order_list')
    return render(request, 'orders/delete.html', {'order': order})

@login_required(login_url='login')
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            if status == 'cancelled' and order.status != 'cancelled':
                for order_item in order.items.select_related('item').all():
                    order_item.item.quantity += order_item.quantity
                    order_item.item.save()
            elif order.status == 'cancelled' and status != 'cancelled':
                for order_item in order.items.select_related('item').all():
                    order_item.item.quantity -= order_item.quantity
                    order_item.item.save()
            order.status = status
            order.save()
            return redirect('order_detail', pk=pk)
    return redirect('order_detail', pk=pk)

@login_required(login_url='login')
def order_item_add(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    form = OrderItemForm(request.POST or None)
    if form.is_valid():
        order_item = form.save(commit=False)
        order_item.order = order
        inventory_item = order_item.item
        if inventory_item.quantity < order_item.quantity:
            form.add_error('quantity', 'Not enough stock available.')
        else:
            order_item.item_name = inventory_item.name
            order_item.item_price = inventory_item.price
            order_item.save()
            inventory_item.quantity -= order_item.quantity
            inventory_item.save()
            return redirect('order_detail', pk=order_pk)
    return render(request, 'orders/item_form.html', {'form': form, 'order': order})

@login_required(login_url='login')
def order_item_edit(request, order_pk, pk):
    order = get_object_or_404(Order, pk=order_pk)
    order_item = get_object_or_404(OrderItem, pk=pk, order=order)
    old_quantity = order_item.quantity
    form = OrderItemForm(request.POST or None, instance=order_item)
    if form.is_valid():
        new_quantity = form.cleaned_data['quantity']
        diff = new_quantity - old_quantity
        inventory_item = order_item.item
        if diff > 0 and inventory_item.quantity < diff:
            form.add_error('quantity', 'Not enough stock.')
        else:
            form.save()
            inventory_item.quantity -= diff
            inventory_item.save()
            return redirect('order_detail', pk=order_pk)
    return render(request, 'orders/item_form.html', {'form': form, 'order': order, 'item': order_item})

@login_required(login_url='login')
def order_item_delete(request, order_pk, pk):
    order = get_object_or_404(Order, pk=order_pk)
    order_item = get_object_or_404(OrderItem, pk=pk, order=order)
    if request.method == 'POST':
        inventory_item = order_item.item
        inventory_item.quantity += order_item.quantity
        inventory_item.save()
        order_item.delete()
        return redirect('order_detail', pk=order_pk)
    return redirect('order_detail', pk=order_pk)