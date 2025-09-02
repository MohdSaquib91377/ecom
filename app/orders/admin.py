from django.contrib import admin
from .models import Order, OrderItem, Payment

# Inline for OrderItem so it appears inside Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "subtotal")
    can_delete = False

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "payment_method", "total_price", "is_paid", "created_at")
    list_filter = ("status", "payment_method", "is_paid", "created_at")
    search_fields = ("user__username", "id", "razorpay_order_id", "razorpay_payment_id")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "payment_method", "amount", "status", "created_at")
    list_filter = ("payment_method", "status", "created_at")
    search_fields = ("payment_id", "user__username", "order__id")
    ordering = ("-created_at",)
