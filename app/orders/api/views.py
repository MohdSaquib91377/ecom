from orders.api.serializers import CreateOrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from store.models import Cart
from orders.models import Order, OrderItem, Payment
from accounts.models import Address
from django.conf import settings
import razorpay


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create Order",
        operation_description="Place an order using the selected address and payment method.",
        request_body=CreateOrderSerializer,
        responses={
            201: openapi.Response(description="Order successfully created"),
            400: openapi.Response(description="Bad Request"),
            404: openapi.Response(description="Address or Cart not found"),
            500: openapi.Response(description="Server Error"),
        },
    )
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        address_id = serializer.validated_data["address_id"]
        payment_method = serializer.validated_data["payment_method"]

        # Validate shipping address
        try:
            shipping_address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address ID!"}, status=status.HTTP_404_NOT_FOUND)

        # Get user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found!"}, status=status.HTTP_404_NOT_FOUND)

        if cart.items.count() == 0:
            return Response({"error": "Cart is empty!"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        total = sum(item.subtotal for item in cart.items.all())

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_price=total,
            payment_method=payment_method,
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Clear cart after placing order
        cart.items.all().delete()

        # If payment method is Razorpay → create Razorpay order
        if payment_method == "RAZORPAY":
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            payment_data = client.order.create({
                "amount": int(order.total_price * 100),
                "currency": "INR",
                "payment_capture": 1,
            })

            # Save Razorpay order ID
            order.razorpay_order_id = payment_data["id"]
            order.save()

            # Create payment record
            Payment.objects.create(
                user=user,
                order=order,
                payment_method=payment_method,
                amount=order.total_price,
                status="PENDING",
            )

            return Response({
                "success": True,
                "payment_type": "ONLINE",
                "order_id": order.id,
                "razorpay_order_id": payment_data["id"],
                "amount": payment_data["amount"],
                "currency": payment_data["currency"],
                "razorpay_key": settings.RAZORPAY_KEY_ID
            }, status=status.HTTP_201_CREATED)

        # If payment method is COD → no Razorpay, just mark as PENDING
        else:
            Payment.objects.create(
                user=user,
                order=order,
                payment_method=payment_method,
                amount=order.total_price,
                status="PENDING",  # COD payments are collected later
            )

            return Response({
                "success": True,
                "payment_type": "COD",
                "order_id": order.id,
                "amount": order.total_price,
                "currency": "INR",
                "message": "Order placed successfully. Pay cash on delivery."
            }, status=status.HTTP_201_CREATED)
