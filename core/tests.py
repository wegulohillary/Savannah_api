from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import Customer, Order


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
            name="Test Customer", phone_number="+254700000000", email="test@example.com"
        )


class CustomerAPITests(BaseAPITestCase):
    def test_create_customer(self):
        url = reverse("customer-list")
        data = {"name": "New Customer", "phone_number": "+254735985062", "email": "wegulohillary@gmail.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

    def test_list_customers(self):
        url = reverse("customer-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class OrderAPITests(BaseAPITestCase):
    @patch("core.utils.send_sms")  # 👈 mock SMS sending
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
        mock_send_sms.assert_called_once_with(
            self.customer.phone_number,
            f"Hi {self.customer.name}, we received your order (Test Item) for amount 500."
        )


class SMSAPITests(BaseAPITestCase):
    @patch("core.utils.send_sms")  # 👈 mock SMS for sandbox
    def test_test_sms_endpoint(self, mock_send_sms):
        url = reverse("test_sms")
        response = self.client.get(url + "?phone=+254703804272")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_sms.assert_called_once()
        self.assertIn("SMS sent successfully", response.json()["status"])
