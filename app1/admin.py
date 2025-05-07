from django.contrib import admin
from .models import (
    CustomUserModel,
    CustomGroupModel,
    PendingUser,
    Product,
    Category,
    Order,
    Payment,
)

from django.contrib.auth.admin import UserAdmin, GroupAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUserModel
    
    # Custom fields to be displayed in the user edit form
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("ph_no", "post", "address", "city", "pincode", "country")}),
    )
    
    # Custom fields to be displayed in the user creation form
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("ph_no", "post", "address", "city", "pincode", "country")}),
    )
    
    # Custom list display for the user list page in the admin
    list_display = UserAdmin.list_display + ('ph_no', 'post', 'address', 'city', 'pincode', 'country')

    # Allow filtering by custom fields
    list_filter = UserAdmin.list_filter + ('ph_no', 'post')

    # Optional: Add search functionality for custom fields
    search_fields = UserAdmin.search_fields + ('ph_no', 'post')

    # Optionally, you can define ordering
    ordering = ('username',)

# Register the CustomUserModel with the CustomUserAdmin
admin.site.register(CustomUserModel, CustomUserAdmin)

class CustomGroupAdmin(GroupAdmin):
    model = CustomGroupModel
    fieldsets = (
        GroupAdmin.fieldsets + ((None, {"fields": ("description", "name")}),)
        if GroupAdmin.fieldsets
        else ((None, {"fields": ("description", "name")}),)
    )


admin.site.register(CustomGroupModel, CustomGroupAdmin)


admin.site.register(PendingUser)


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)

# order and payments


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id",)

admin.site.register(Order)
admin.site.register(Payment)