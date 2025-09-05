from django.urls import path
from orders.api.views import CreateOrderAPIView, UserOrderDetailAPIView, UserOrdersAPIView, razorpay_webhook

urlpatterns = [
    path("create-order/", CreateOrderAPIView.as_view(), name="create-order"),
    path("my-orders/", UserOrdersAPIView.as_view(), name="my-orders"),
    path("my-orders/<int:order_id>/", UserOrderDetailAPIView.as_view(), name="my-order-detail"),
    path("razorpay/webhook/", razorpay_webhook, name="razorpay_webhook"),

]
