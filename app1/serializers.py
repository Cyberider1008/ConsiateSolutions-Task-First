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


###########################


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    ph_no = serializers.CharField(max_length=100, required=False)
    post = serializers.CharField(max_length=100, required=False)
    username = serializers.CharField(max_length=120, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)

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
        if "password" in validated_data:
            instance.password = make_password(validated_data["password"])
        instance.save()
        return instance


############################
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


###############

# category and product serializers here


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active"]

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "categories", "is_active"]

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

