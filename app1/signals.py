from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import Product, Category


# Signal to deactivate products when a category is deactivated
@receiver(post_save, sender=Category)
def deactivate_products_on_category_deactivation(sender, instance, **kwargs):
    Product.objects.filter(
        productcategory__category=instance, is_active = not instance.is_active
    ).update(is_active=instance.is_active)
