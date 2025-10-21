from django.test import TestCase
from core.models import Customer, Order
from core.utils import send_sms
from decimal import Decimal

class ModelsTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Alice',
            code='C001',
            phone_number='+254700000000'
        )

    def test_create_customer_and_order(self):
        order = Order.objects.create(
            customer=self.customer,
            item='Widget',
            amount=Decimal('123.45')
        )

        self.assertEqual(self.customer.orders.count(), 1)
        self.assertEqual(order.item, 'Widget')

    def test_send_sms_simulation_or_real(self):
        response = send_sms(self.customer.phone_number, "Test message")
        self.assertIsNotNone(response)

        # Handle both simulated and real responses
        if isinstance(response, dict) and "status" in response:
            self.assertEqual(response["status"], "simulated")
        elif isinstance(response, dict) and "SMSMessageData" in response:
            self.assertIn("Recipients", response["SMSMessageData"])
            self.assertEqual(
                response["SMSMessageData"]["Recipients"][0]["status"], "Success"
            )
        else:
            self.fail("Unexpected SMS response format.")
