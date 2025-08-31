from rest_framework import serializers
from store.models import Category, SubCategory, Product, Image,Wishlist
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