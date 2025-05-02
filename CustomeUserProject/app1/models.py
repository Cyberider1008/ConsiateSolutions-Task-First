from django.db import models
from django.contrib.auth.models import User, Group


class CustomGroupModel(Group):
    description = models.TextField(blank=True, null=True)
    
    leader = models.OneToOneField(
        'CustomUserModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_group'
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
        related_name='members'
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


