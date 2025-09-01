from rest_framework import serializers
from store.models import Category, SubCategory, Product, Image,Wishlist,Cart,CartItem
from accounts.api.serializers import UserRegisterSerializer

class ImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    class Meta:
        model = Image
        fields = ["id", "image"]


class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer for subcategories under a category."""
    class Meta:
        model = SubCategory
        fields = ["id", "name","image"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories including their subcategories."""
    sub_categories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "image", "sub_categories"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products with related images and subcategory info."""
    images = ImageSerializer(many=True, read_only=True)  # Better naming
    sub_category = serializers.StringRelatedField()  # To show subcategory name instead of ID
    category = serializers.CharField(source="sub_category.category.name", read_only=True)  # Auto fetch category name

    class Meta:
        model = Product
        fields = "__all__"




class WishListCreateDeleteSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = Wishlist
        fields = ["product_id"]
        extra_kwargs = {"user": {"required": False, "allow_null": True},"product": {"required": False, "allow_null": True}}


class WishListSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer()
    product = ProductSerializer()
    class Meta:
        model = Wishlist
        fields = "__all__"

class AddCartItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

class UpdateCartItemInputSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['add', 'remove'])


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "subtotal"]
        read_only_fields = ["subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


    
class MergeCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

class MergeCartInputSerializer(serializers.Serializer):
    items = MergeCartItemSerializer(many=True)
