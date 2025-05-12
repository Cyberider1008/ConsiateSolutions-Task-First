from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from .models import (
    CustomUserModel,
    CustomGroupModel,
    PendingUser,
    Product,
    Category,
    ProductCategory,
    Order,
    OrderItem,
    Payment,
)

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    ph_no = serializers.CharField(max_length=100)
    post = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken")
        
        return value

    def create(self, validated_data):
        # validated_data['password'] = make_password(validated_data['password'])
        
        return PendingUser.objects.create(**validated_data)

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        
        if user is None:
            raise serializers.ValidationError("Invalid username or password")
        
        data["user"] = user
        return data

class GroupCreateSerializers(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    users = serializers.ListField(child=serializers.IntegerField(), required=False)

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    ph_no = serializers.CharField(max_length=100, required=False)
    post = serializers.CharField(max_length=100, required=False)
    username = serializers.CharField(max_length=120, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    pincode = serializers.CharField(required=False)
    country = serializers.CharField(required=False)

    def validate_username(self, value):
        
        if self.instance:
        
            # If username is unchanged, don't validate
            if self.instance.username == value:
        
                return value
        
            # If username is changed, check if new one already exists for another user
            if (
                CustomUserModel.objects.filter(username=value)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError("Username is already taken")
        else:
        
            # If creating a new user
            if CustomUserModel.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username is already taken")
        
        return value

    def create(self, validated_data):
        # validated_data['password'] = make_password(validated_data['password'])
        return CustomUserModel.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.ph_no = validated_data.get("ph_no", instance.ph_no)
        instance.post = validated_data.get("post", instance.post)
        instance.address = validated_data.get("address", instance.address)
        instance.city = validated_data.get("city", instance.city)
        instance.pincode = validated_data.get("pincode", instance.pincode)
        instance.country = validated_data.get("country", instance.country)

        if "password" in validated_data:
            instance.password = make_password(validated_data["password"])
        instance.save()
        
        return instance

# fetch user and group get method
class UserSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUserModel
        fields = ["id", "username", "email"]

class GroupWithUsersSerializer(serializers.ModelSerializer):
    users = UserSummarySerializer(source="user_set", many=True)
    
    class Meta:
        model = CustomGroupModel
        fields = ["id", "name", "users"]

class GroupSerializer(serializers.ModelSerializer):
    users = UserSerializer(source="members", many=True, read_only=True)
    
    class Meta:
        model = CustomGroupModel
        fields = ["id", "name", "description", "users"]

class ProductSerializer(serializers.ModelSerializer):
    # categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description","is_active"]

class CategorySerializer(serializers.ModelSerializer):

    products = ProductSerializer(many=True, read_only= True)

    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active",  "products"]

    
   

class ProductCategorySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = ProductCategory
        fields = ["product", "category"]

    def to_representation(self, instance):

        return {
            "product": ProductSerializer(instance.product).data,
            "category": CategorySerializer(instance.category).data,
        }

# order and payments
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True), source='product'
    )

    class Meta:
        model = OrderItem
        fields = ['product_id', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id','customer', 'subtotal', 'delivery_charge', 'discount',
            'total', 'paid_amount', 'type', 'status', 'shipping_address',
            'placed_by', 'paid', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

class PaymentSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['payment_amount', 'payment_mode', 'order', 'reference_id', 'remaining_balance']

    def get_remaining_balance(self, obj):
        order = obj.order
        # Get all payments sorted by creation time
        payments = order.payment.order_by('id')
        total_paid = 0
        for p in payments:
            total_paid += p.payment_amount
            if p.id == obj.id:
                break
        return float(order.total - total_paid)

    def validate(self, data):
        order = data['order']
        new_amount = data['payment_amount']
        
        if order.paid:
            raise serializers.ValidationError("This order has already been fully paid.")

        existing_payments = order.payment.all()
        total_paid = sum(p.payment_amount for p in existing_payments)
        remaining_amount = order.total - total_paid

        if new_amount > remaining_amount:
            raise serializers.ValidationError({
                "payment_amount": f"Payment exceeds the remaining amount of ₹{remaining_amount:.2f}."
            })

        return data

    def create(self, validated_data):
        order = validated_data['order']
        new_amount = validated_data['payment_amount']

        existing_payments = order.payment.all()
        total_paid = sum(p.payment_amount for p in existing_payments) + new_amount

        order.paid_amount = total_paid
        if total_paid >= order.total:
            order.paid = True
        order.save()

        return super().create(validated_data)


# Excel Serializers
class ProductExcelSerializers(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category')
    
    def get_category(self, obj):
        return ", ".join([cat.name for cat in Category.objects.filter(productcategory__product=obj)])

    
class CategoryExcelSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ('id','name', 'products')

    def get_products(self, obj):
        products = Product.objects.filter(productcategory__category=obj)
        return [prod.name for prod in products] if products.exists() else ""
   

    