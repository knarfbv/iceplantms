from django.db import models

# Create your models here.

class IceProduct(models.Model):
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.OneToOneField(IceProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    order_date = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return sum(item.quantity * item.product.price for item in self.items.all())

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(IceProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def unit_price(self):
        return self.product.price

    @property
    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"