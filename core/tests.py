from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import Customer, Order
from .utils import send_sms


class BaseAPITestCase(APITestCase):
    def setUp(self):
        # Create and login a superuser for authentication
        self.user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.client = APIClient()
        self.client.login(username="admin", password="adminpass")

        # Create a customer for tests
        self.customer = Customer.objects.create(
            name="Test Customer", phone_number="+254700000000", code="C001"
        )


class CustomerAPITests(BaseAPITestCase):
    def test_create_customer_via_api(self):
        url = reverse("customer-list")
        data = {"name": "New Customer", "phone_number": "+254735985062", "code": "C002"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

    def test_list_customers(self):
        url = reverse("customer-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class OrderAPITests(BaseAPITestCase):
    @patch("core.views.send_sms")  # Mock the send_sms used in views
    def test_create_order_sends_sms(self, mock_send_sms):
        url = reverse("order-list")
        data = {
            "customer": self.customer.id,
            "item": "Test Item",
            "amount": 500,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        expected_message = f"Hi {self.customer.name}, we received your order for {data['item']} worth {data['amount']:.2f}."
        mock_send_sms.assert_called_once_with(self.customer.phone_number, expected_message)

    def test_create_order_with_negative_amount(self):
        url = reverse("order-list")
        data = {
            "customer": self.customer.id,
            "item": "Bad Item",
            "amount": -100,
        }
        response = self.client.post(url, data, format="json")
        # If no serializer validation for negative amounts exists, this might still be 201
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders(self):
        Order.objects.create(customer=self.customer, item="Sample", amount=100)
        url = reverse("order-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class SMSAPITests(BaseAPITestCase):
    @patch("core.views.send_sms")
    def test_test_sms_endpoint(self, mock_send_sms):
        mock_send_sms.return_value = {"status": "simulated"}
        url = reverse("test_sms")
        response = self.client.get(url + f"?phone={self.customer.phone_number}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_sms.assert_called_once()
        self.assertIn("status", response.json())


class UtilsTestCase(APITestCase):
    @patch("core.utils.sms", None)
    def test_send_sms_returns_simulated_when_not_configured(self):
        resp = send_sms("+254700000000", "Hello test")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status"], "simulated")

    @patch("core.utils.sms")
    def test_send_sms_success(self, mock_sms):
        mock_sms.send.return_value = {"status": "success"}
        response = send_sms("+254700000000", "Hello test")
        self.assertEqual(response, {"status": "success"})
