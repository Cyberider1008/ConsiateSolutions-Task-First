from django.contrib import admin
from .models import CustomUserModel, CustomGroupModel, PendingUser
from django.contrib.auth.admin import UserAdmin, GroupAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUserModel
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('ph_no', 'post')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('ph_no', 'post')}),
    )


class CustomGroupAdmin(GroupAdmin):
    model = CustomGroupModel
    fieldsets = GroupAdmin.fieldsets + (
        (None, {'fields': ('description','name')}),
    ) if GroupAdmin.fieldsets else (
        (None, {'fields': ('description','name')}),
    )

admin.site.register(CustomGroupModel, CustomGroupAdmin)

admin.site.register(CustomUserModel, CustomUserAdmin)

admin.site.register(PendingUser)

