from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from store.models import Cart, CartItem
from orders.models import Order, OrderItem, Payment
from django.conf import settings
import razorpay


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            shipping_address = request.data.get("shipping_address")
            payment_method = request.data.get("payment_method", "RAZORPAY")

            # Fetch user's cart
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({"error": "Cart not found!"}, status=status.HTTP_404_NOT_FOUND)

            if cart.items.count() == 0:
                return Response({"error": "Cart is empty!"}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total price
            total = sum(item.subtotal for item in cart.items.all())

            # Create the order
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

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Create Razorpay order
            payment_data = client.order.create({
                "amount": int(order.total_price * 100),  # Amount in paise
                "currency": "INR",
                "payment_capture": 1,
            })

            # Save Razorpay order ID in our database
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

            # Return payment details to frontend
            return Response({
                "success": True,
                "order_id": order.id,
                "razorpay_order_id": payment_data["id"],
                "amount": payment_data["amount"],
                "currency": payment_data["currency"],
                "razorpay_key": settings.RAZORPAY_KEY_ID
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
