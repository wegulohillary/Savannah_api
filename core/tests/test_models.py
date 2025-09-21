from django.test import TestCase
from core.models import Customer, Order
from decimal import Decimal

class ModelsTestCase(TestCase):
    def test_customer_and_order_creation(self):
        cust = Customer.objects.create(name='Alice', code='C001', phone_number='+254700000000')
        order = Order.objects.create(customer=cust, item='Widget', amount=Decimal('123.45'))
        self.assertEqual(cust.orders.count(), 1)
        self.assertEqual(order.item, 'Widget')
        self.assertEqual(str(order), f'Order {order.pk} - Widget for {cust}')
