import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal
from orders.models import Order

pytestmark = pytest.mark.django_db

class TestOrderEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self, api_client_authenticated, product_factory):
        self.api_client, self.user = api_client_authenticated
        self.product_factory = product_factory

    def test_create_order_success(self):
        # Add funds to user balance
        self.user.balance = Decimal('100.00')
        self.user.save()

        # Add items to cart
        product1 = self.product_factory.create(price=Decimal('10.00'), stock=5)
        product2 = self.product_factory.create(price=Decimal('25.00'), stock=5)
        self.user.cart.items.create(product=product1, quantity=2) # 20.00
        self.user.cart.items.create(product=product2, quantity=1) # 25.00
        # Total: 45.00

        url = reverse('orders:order-list')
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        self.user.refresh_from_db()
        
        # Check order details
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.user == self.user
        assert order.total_price == Decimal('45.00')
        assert order.items.count() == 2
        
        # Check balance and stock
        assert self.user.balance == Decimal('55.00') # 100 - 45
        product1.refresh_from_db()
        assert product1.stock == 3 # 5 - 2
        
        # Check cart is cleared
        assert self.user.cart.items.count() == 0
    
    def test_create_order_empty_cart(self):
        self.user.balance = Decimal('100.00')
        self.user.save()
        
        url = reverse('orders:order-list')
        response = self.api_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty cart" in response.data['error']

    def test_create_order_insufficient_funds(self):
        self.user.balance = Decimal('30.00') # Not enough for 45.00
        self.user.save()

        product1 = self.product_factory.create(price=Decimal('10.00'), stock=5)
        self.user.cart.items.create(product=product1, quantity=4) # 40.00

        url = reverse('orders:order-list')
        response = self.api_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Insufficient funds" in response.data['error']
        assert Order.objects.count() == 0

    def test_create_order_insufficient_stock(self):
        self.user.balance = Decimal('100.00')
        self.user.save()

        product1 = self.product_factory.create(price=Decimal('10.00'), stock=2)
        self.user.cart.items.create(product=product1, quantity=3) # Request 3, only 2 in stock

        url = reverse('orders:order-list')
        response = self.api_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Not enough stock" in response.data['error']
        assert Order.objects.count() == 0
        
        # Check that transaction was rolled back
        product1.refresh_from_db()
        assert product1.stock == 2 # Should not have changed
        self.user.refresh_from_db()
        assert self.user.balance == Decimal('100.00') # Should not have changed
        assert self.user.cart.items.count() == 1 # Cart should not be cleared

    def test_list_orders(self):
        # Create some orders for the user
        Order.objects.create(user=self.user, total_price='10.00')
        Order.objects.create(user=self.user, total_price='20.00')

        url = reverse('orders:order-list')
        response = self.api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
