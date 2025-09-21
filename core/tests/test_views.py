from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from core.models import Customer
from unittest.mock import patch

class ViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester@example.com', email='tester@example.com', password='testpw')
        self.client = APIClient()
        # we'll authenticate using session auth via force_authenticate for tests
        self.client.force_authenticate(user=self.user)

    def test_create_customer(self):
        url = reverse('customer-list')
        data = {'name': 'Bob', 'code': 'B001', 'phone_number': '+254711111111'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.first().name, 'Bob')

    @patch('core.views.send_sms')
    def test_create_order_triggers_sms(self, mock_send_sms):
        # create customer
        cust = Customer.objects.create(name='SMS Test', code='S001', phone_number='+254703804272')
        url = reverse('order-list')
        data = {'customer': cust.id, 'item': 'Apple', 'amount': '50.00'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        # ensure SMS was called
        mock_send_sms.assert_called_once()
