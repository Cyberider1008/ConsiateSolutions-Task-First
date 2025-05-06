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
