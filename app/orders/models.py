from django.db import models
from django.conf import settings
from store.models import Product
from config.base import TimeStampModel
from accounts.models import Address,User
# --------------------------
# ORDER MODEL
# --------------------------
class Order(TimeStampModel):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PLACED", "Placed"),
        ("PAID", "Paid"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("FAILED", "Failed"),
    )

    PAYMENT_METHODS = (
        ("COD", "Cash on Delivery"),
        ("RAZORPAY", "Razorpay"),
        ("STRIPE", "Stripe"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="COD")
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} by {self.user}"

    @property
    def item_count(self):
        return self.items.count()


# --------------------------
# ORDER ITEM MODEL
# --------------------------
class OrderItem(TimeStampModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    


# --------------------------
# PAYMENT MODEL
# --------------------------
class Payment(TimeStampModel):
    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=Order.PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="PENDING")

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
