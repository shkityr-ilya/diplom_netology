from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    ProductParameter,
    Contact,
    Order,
    OrderItem,
)

User = get_user_model()

# Сериализатор для регистрации пользователя


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})

        email = attrs["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует"}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"].lower(),
            username=validated_data["email"].lower(),
            password=validated_data["password"],
            is_active=True,
        )
        return user


# Сериализатор для входа пользователя


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
            "is_active",
            "type",
        ]


# Сериализатор для магазина


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", "url", "state"]


# Сериализатор для категории


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "shop"]


# Сериализатор для продукта


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "category"]


# Сериализатор для информации о продукте


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = [
            "id",
            "model",
            "external_id",
            "product",
            "shop",
            "quantity",
            "price",
            "price_rrc",
        ]


# Сериализатор  для параметра продукта


class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductParameter
        fields = ["id", "parameter", "value"]


# Сериализатор для контакта


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "user",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
            "phone",
        ]


# Сериализатор для заказа


class OrderSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "dt", "state", "contact"]


# Сериализатор для позиции заказа


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "order", "product_info", "quantity"]
