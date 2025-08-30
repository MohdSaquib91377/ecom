from django.urls import path
from store.api.views import (
    CategoryListView,
    SubCategoryListView,
    ProductListByCategoryView,
    ProductListBySubCategoryView,
    ProductDetailView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:category_id>/products/", ProductListByCategoryView.as_view(), name="product-by-category"),
    path("subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path("subcategories/<int:subcategory_id>/products/", ProductListBySubCategoryView.as_view(), name="product-by-subcategory"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
