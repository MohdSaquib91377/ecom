from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .models import Category, Brand, Product, Image, SubCategory, RecentView, Wishlist,CartItem,Cart


# ==============================
# SubCategory Inline for Category (Removed Tab Here)
# ==============================
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ['name', 'is_active']
    show_change_link = True

# ==============================
# SubCategory Admin
# ==============================
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'is_active']
    search_fields = ['name']
    list_filter = ['category', 'is_active']
    ordering = ['id']  # Ensures a sorted display
    list_per_page = 25  # Optional: Better pagination
    save_as = True  # Allows saving as a new instance

    # ✅ Ensures SubCategory shows in the side menu properly
    def get_model_perms(self, request):
        """
        Return all permissions to make sure it's always visible in the admin menu.
        """
        perms = super().get_model_perms(request)
        perms["view"] = True
        return perms

admin.site.register(SubCategory, SubCategoryAdmin)

# ==============================
# Category Admin (No Tabs in Product)
# ==============================
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'image']
    # ❌ Removed inlines to avoid unwanted tabs for Category
    inlines = [SubCategoryInline]

admin.site.register(Category, CategoryAdmin)


# ==============================
# SubCategory Admin
# ==============================



# ==============================
# Brand Admin
# ==============================
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']

admin.site.register(Brand, BrandAdmin)


# ==============================
# Image Inline (Only for Product)
# ==============================
class ImageAdmin(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['image']
    show_change_link = True


# ==============================
# Product Admin (Keeps Image Tab + Dynamic SubCategory Logic)
# ==============================
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description", "price", "quantity", "category", "sub_category", "brand"]
    list_filter = ["category", "sub_category", "brand"]
    search_fields = ["name", "description"]
    inlines = [ImageAdmin]  # ✅ Keep only Image Tab

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(Image)


# ==============================
# RecentView Admin
# ==============================
class RecentViewAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "user", "views_counter"]
    search_fields = ["product__name", "user__username"]

admin.site.register(RecentView, RecentViewAdmin)


class WishListAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "user"]
    search_fields = ["product__name", "user__username"]

admin.site.register(Wishlist, WishListAdmin)





class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ("product", "quantity", "subtotal")
    readonly_fields = ("subtotal",)

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "Subtotal (₹)"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "item_count")
    search_fields = ("user__username", "user__email")
    list_filter = ("user",)
    inlines = [CartItemInline]
    readonly_fields = ("total_price",)

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "subtotal")
    search_fields = ("product__name", "cart__user__username")
    list_filter = ("cart", "product")

    readonly_fields = ("subtotal",)

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "Subtotal (₹)"
