from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .utils import send_sms


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("id")
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-time")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # After save - send SMS
        customer = order.customer
        if customer.phone_number:
            message = (
                f"Hi {customer.name}, we received your order "
                f"({order.item}) for amount {order.amount}."
            )
            send_sms(customer.phone_number, message)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# 👇 Add a simple test endpoint
@api_view(["GET"])
@permission_classes([AllowAny])  # no auth needed for testing
def test_sms(request):
    """Test sending SMS via Africa's Talking."""
    phone = request.query_params.get("phone", None)
    if not phone:
        return Response(
            {"error": "Please provide a phone number using ?phone=NUMBER"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    message = "Hello from Savannah_api test endpoint 🚀"
    try:
        send_sms(phone, message)
        return Response({"status": "SMS sent successfully", "phone": phone})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
