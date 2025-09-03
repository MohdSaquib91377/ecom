from django.contrib import admin
from .models import Order, OrderItem, Payment

# Inline for OrderItem so it appears inside Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "subtotal")
    can_delete = False
    
    def subtotal(self, obj):
        if obj.pk:  # Check if object exists (for existing items)
            return obj.quantity * obj.price
        return 0  # For new items being added
    
    subtotal.short_description = "Subtotal"
    
    # Prevent deletion of individual order items
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "payment_method", "total_price", "is_paid", "created_at")
    list_filter = ("status", "payment_method", "is_paid", "created_at")
    search_fields = ("user__username", "id", "razorpay_order_id", "razorpay_payment_id")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)
    
    # Prevent deletion of orders
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Optional: Also disable bulk delete action
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "payment_method", "amount", "status", "created_at")
    list_filter = ("payment_method", "status", "created_at")
    search_fields = ("payment_id", "user__username", "order__id")
    ordering = ("-created_at",)
    
    # Prevent deletion of payments
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Optional: Also disable bulk delete action
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions