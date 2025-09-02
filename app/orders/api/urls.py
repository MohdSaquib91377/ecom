from django.urls import path
from orders.api.views import CreateOrderAPIView

urlpatterns = [
    path("create-order/", CreateOrderAPIView.as_view(), name="create-order"),
]
