from django.urls import path
from store.api.views import (
    CategoryListView,
    MergeCartView,
    SubCategoryListView,
    ProductListByCategoryView,
    ProductListBySubCategoryView,
    ProductDetailView,
    ProductSearchView,
    WishListAPIView,
    CartView
    
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:category_id>/products/", ProductListByCategoryView.as_view(), name="product-by-category"),
    path("subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path("subcategories/<int:subcategory_id>/products/", ProductListBySubCategoryView.as_view(), name="product-by-subcategory"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
    path('wishlist/add-to-wishlist/',WishListAPIView.as_view(),name = "add-to-wishlist"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/merge/", MergeCartView.as_view(), name="merge-cart"),
]
