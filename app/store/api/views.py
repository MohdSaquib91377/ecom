from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from store.models import Category, SubCategory, Product
from store.api.serializers import CategorySerializer, SubCategorySerializer, ProductSerializer


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
