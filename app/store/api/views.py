from rest_framework import generics, status,filters
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from store.models import Cart, CartItem, Category, SubCategory, Product,Wishlist
from store.api.serializers import AddCartItemInputSerializer, CartSerializer, CategorySerializer, MergeCartInputSerializer, SubCategorySerializer, ProductSerializer, UpdateCartItemInputSerializer,WishListCreateDeleteSerializer,WishListSerializer
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import django_filters
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404



# 1. Get all categories (ListAPIView)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        operation_description="Get a list of all categories",
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"status": "400", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# 2. Get all subcategories (ListAPIView)
class SubCategoryListView(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    @swagger_auto_schema(
        operation_description="Get a list of all subcategories",
        responses={200: SubCategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"status": "400", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )




# 3. Get products under a specific subcategory (ListAPIView)
class ProductListBySubCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        subcategory_id = self.kwargs.get("subcategory_id")
        return Product.objects.filter(sub_category_id=subcategory_id, is_active=True)

    @swagger_auto_schema(
        operation_description="Get all active products under a specific subcategory",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"status": "400", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductListByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Product.objects.filter(category_id=category_id, is_active=True)

    @swagger_auto_schema(
        operation_description="Get all active products under a specific subcategory",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"status": "400", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# 4. Get single product details (RetrieveAPIView)
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_description="Get detailed information of a single product",
        responses={200: ProductSerializer()}
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"status": "400", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProductPagination(PageNumberPagination):
    page_size = 10  # Default items per page
    page_size_query_param = "page_size"  # Allow client to control items per page
    max_page_size = 100  # Limit max items per page

# --- Product Filter ---
class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category_id")
    sub_category = django_filters.NumberFilter(field_name="sub_category_id")
    brand = django_filters.NumberFilter(field_name="brand_id")

    class Meta:
        model = Product
        fields = ["category", "sub_category", "brand"]

# --- Product Search API ---
class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "brand__name"]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]
    pagination_class = ProductPagination  # ✅ Added pagination here

    @swagger_auto_schema(
        operation_description="Search, filter, and sort products.",
        responses={200: ProductSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter("search", openapi.IN_QUERY, description="Search by name, description, brand", type=openapi.TYPE_STRING),
            openapi.Parameter("category", openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter("sub_category", openapi.IN_QUERY, description="Filter by sub-category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter("brand", openapi.IN_QUERY, description="Filter by brand ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter("min_price", openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter("max_price", openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter("ordering", openapi.IN_QUERY, description="Sort by price or created_at (use -price for desc)", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"status": "400", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        


# TODO: WishList


class WishListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags = ['wishlist'])
    def get(self,request,*args, **kwargs):
        queryset = Wishlist.objects.filter(user = request.user)
        serializer = WishListSerializer(queryset,many = True)
        return Response(serializer.data,status = 200)

    @swagger_auto_schema(tags = ['wishlist'],request_body = WishListCreateDeleteSerializer)
    def post(self,request,*args, **kwargs):
        serializer = WishListCreateDeleteSerializer(data = request.data)
        product = Product.objects.filter(id = request.data['product_id']).first()
        serializer.is_valid(raise_exception = True)
        found_wishlist = Wishlist.objects.filter(product = product,user=request.user).first()
        if found_wishlist:
            found_wishlist.delete()
            return Response({"status":"200","message":"Product removed from wishlist"},status=201)

        serializer.save(user = self.request.user,product = product)
        return Response({"status": "200","message":"Product added into wishlist"},status =200)
    
    @swagger_auto_schema(tags = ['wishlist'],request_body = WishListCreateDeleteSerializer)
    def delete(self,request,*args, **kwargs):       
        serializer = WishListCreateDeleteSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        product = Product.objects.filter(id = request.data['product_id']).first()
        if Wishlist.objects.filter(product = product,user = request.user).exists():
            Wishlist.objects.filter(product = product,user = request.user).delete()
            return Response({"status": "200","message":"Product removed from wishlist"},status = 203)
        return Response({"status": "400","message":"You dont have permission to remove product from wishlist"},status = 400)



# TODO: Cart

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['cart'])
    def get(self, request):
        """Get user's cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['cart'], request_body=AddCartItemInputSerializer)
    def post(self, request):
        """Add product to cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = AddCartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        product = get_object_or_404(Product, id=product_id)
        if product.quantity < quantity:
            return Response({"error": "Not enough stock"}, status=400)

        cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Product added to cart"})
   
    @swagger_auto_schema(tags=['cart'], request_body=UpdateCartItemInputSerializer)
    def patch(self, request):
        """Increment, decrement, or set quantity of a cart item."""
        serializer = UpdateCartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_id = serializer.validated_data["item_id"]
        action = serializer.validated_data["action"]

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if action == "add":
            new_quantity = cart_item.quantity + 1
        elif action == "remove":
            new_quantity = cart_item.quantity - 1
        else:
            return Response({"error": "Invalid action"}, status=400)

        # Remove item if quantity <= 0
        if new_quantity <= 0:
            cart_item.delete()
            return Response({"message": "Item removed successfully"})

        # Check stock
        if cart_item.product.quantity < new_quantity:
            return Response({"error": "Not enough stock available"}, status=400)

        cart_item.quantity = new_quantity
        cart_item.save()

        cart = cart_item.cart
        total_price = cart.total_price

        return Response({
            "message": "Cart updated successfully",
            "item_id": cart_item.id,
            "quantity": cart_item.quantity,
            "item_subtotal": cart_item.subtotal,
            "cart_total": total_price
        })



class MergeCartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['cart'], request_body=MergeCartInputSerializer)
    def post(self, request):
        """
        Merge guest cart after login.
        Example input:
        {
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 3, "quantity": 1}
            ]
        }
        """
        serializer = MergeCartInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guest_items = serializer.validated_data.get("items", [])

        cart, _ = Cart.objects.get_or_create(user=request.user)

        messages = []

        for item in guest_items:
            product = get_object_or_404(Product, id=item["product_id"])
            quantity = item.get("quantity", 1)

            if product.quantity <= 0:
                messages.append(f"{product.name} is out of stock and was not added.")
                continue

            if product.quantity < quantity:
                messages.append(f"{product.name} quantity reduced to {product.quantity} due to limited stock.")
                quantity = product.quantity

            cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart)
        return Response({
            "cart": cart_serializer.data,
            "messages": messages
        })

