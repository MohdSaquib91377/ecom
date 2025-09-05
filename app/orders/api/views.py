from orders.api.serializers import CreateOrderSerializer, OrderDetailSerializer, OrderListSerializer
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
from django.shortcuts import get_object_or_404


import hmac
import hashlib
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes


from django.core.paginator import Paginator

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






# -------------------------------
# USER ORDERS LIST API
# -------------------------------
class UserOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get User Orders",
        operation_description="Fetch a paginated list of logged-in user's orders.",
        responses={200: openapi.Response(description="Orders fetched successfully")},
    )
    def get(self, request):
        user = request.user
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 5))

        orders_qs = (
            Order.objects.filter(user=user)
            .select_related("shipping_address")
            .prefetch_related("items", "items__product")
            .order_by("-created_at")
        )

        paginator = Paginator(orders_qs, limit)
        orders = paginator.get_page(page)

        serializer = OrderListSerializer(orders, many=True)

        return Response({
            "success": True,
            "total_orders": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "orders": serializer.data,
        }, status=status.HTTP_200_OK)


# -------------------------------
# USER ORDER DETAIL API
# -------------------------------
class UserOrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Order Details",
        operation_description="Fetch full details of a specific order including items.",
        responses={200: openapi.Response(description="Order details fetched successfully")},
    )
    def get(self, request, order_id):
        user = request.user
        order = get_object_or_404(
            Order.objects.select_related("shipping_address")
            .prefetch_related("items", "items__product"),
            id=order_id,
            user=user
        )

        serializer = OrderDetailSerializer(order)
        return Response({
            "success": True,
            "order": serializer.data
        }, status=status.HTTP_200_OK)





@csrf_exempt
def razorpay_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    # Get the webhook body
    webhook_body = request.body.decode("utf-8")
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

    # Verify signature
    received_signature = request.headers.get("X-Razorpay-Signature")
    generated_signature = hmac.new(
        key=force_bytes(webhook_secret),
        msg=force_bytes(webhook_body),
        digestmod=hashlib.sha256
    ).hexdigest()

    if received_signature != generated_signature:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Parse webhook payload
    payload = json.loads(webhook_body)
    event = payload.get("event")
    payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})

    # Extract payment details
    razorpay_payment_id = payment_data.get("id")
    amount = payment_data.get("amount") / 100
    status = payment_data.get("status")
    order_id = payment_data.get("order_id")  # Razorpay order ID

    try:
        payment = Payment.objects.get(razorpay_payment_id=razorpay_payment_id)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

    # Handle events
    if event == "payment.captured":
        payment.status = "SUCCESS"
        payment.save()

        # Update Order Status
        order = Order.objects.get(id=payment.order.id)
        order.status = "CONFIRMED"
        order.save()

    elif event == "payment.failed":
        payment.status = "FAILED"
        payment.save()

        # Update Order Status
        order = Order.objects.get(id=payment.order.id)
        order.status = "FAILED"
        order.save()

    return JsonResponse({"status": "ok"}, status=200)
