from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils import timezone

from datetime import timedelta

from rest_framework.authtoken.models import Token

class CustomGroupModel(Group):
    description = models.TextField(blank=True, null=True)

    leader = models.OneToOneField(
        "CustomUserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_group",
    )

    def __str__(self):
        return f"{self.name}"


# CustomUser
class CustomUserModel(User):
    ph_no = models.CharField(max_length=100, null=True)
    post = models.CharField(max_length=100, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')

    group = models.ForeignKey(
        CustomGroupModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )

    def __str__(self):
        return f"{self.username} - {self.email}"


# Pending user is Temp for otp verification
class PendingUser(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    ph_no = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class ExpiringToken(Token):
    expires = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires:
            self.expires = timezone.now() + timedelta(
                minutes=1
            )  # Set the token to expire after 1 minute
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires

# Product and Category Models here
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("product", "category")

# oredr and payment
class Order(models.Model):
    PICKUP = 'PICKUP'
    DELIVERY = 'DELIVERY'
    DINEIN = 'DINE_IN'

    ORDER_TYPE = {
        PICKUP:'Pickup',
        DELIVERY:'Delivery',
        DINEIN:'Dine_in'
    }

    PENDING = 'PENDIND'
    PROCESSING = 'PROCESSING'
    COMPLETE = 'COMPLETE'
    READY = 'READY'
    CANCEL = 'CANCEL'

    ORDER_STATUS = {
        PENDING:'Pending',
        PROCESSING:'Processing',
        COMPLETE:'Complete',
        READY:'Ready',
        CANCEL:'Cancel'
    }

    customer= models.CharField(max_length=255)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    type = models.CharField(max_length=20, choices=ORDER_TYPE, default=PICKUP, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default=PENDING, null=True, blank=True)
    shipping_address = models.TextField()
    placed_by = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.customer)  + "   "+ str(self.id)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment')
    reference_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.payment_amount) + "  " + self.payment_mode

