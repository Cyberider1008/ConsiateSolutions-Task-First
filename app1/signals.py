from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from .models import Product, Category


# Signal to deactivate products when a category is deactivated
# Signal to deactivate products when a category is deactivated
@receiver(pre_save, sender=Category)
def deactivate_products_on_category_deactivation(sender, instance, **kwargs):
    # Check if the category is being deactivated and was previously active
    if instance.pk:
        # print("---" * 20, instance.name)
        old_instance = Category.objects.get(pk=instance.pk)
        if not instance.is_active and old_instance.is_active:
            # Deactivate all products related to this category
            Product.objects.filter(
                productcategory__category=instance, is_active=True
            ).update(is_active=False)
        else:
            Product.objects.filter(
                productcategory__category=instance, is_active=False
            ).update(is_active=True)
