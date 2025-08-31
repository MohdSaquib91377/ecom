from rest_framework import generics, status,filters
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from store.models import Category, SubCategory, Product,Wishlist
from store.api.serializers import CategorySerializer, SubCategorySerializer, ProductSerializer,WishListCreateDeleteSerializer,WishListSerializer
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import django_filters
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

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