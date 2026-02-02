import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal

pytestmark = pytest.mark.django_db

class TestCartEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self, api_client_authenticated):
        self.api_client, self.user = api_client_authenticated
        self.cart = self.user.cart

    def test_get_cart(self):
        url = reverse('cart:cart-list')
        response = self.api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == self.user.id

    def test_add_item_to_cart(self, product_factory):
        product = product_factory.create(stock=10)
        url = reverse('cart:cart-add-item')
        data = {'product_id': product.id, 'quantity': 2}
        
        response = self.api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        self.cart.refresh_from_db()
        assert self.cart.items.count() == 1
        cart_item = self.cart.items.first()
        assert cart_item.product == product
        assert cart_item.quantity == 2

    def test_add_item_insufficient_stock(self, product_factory):
        product = product_factory.create(stock=1)
        url = reverse('cart:cart-add-item')
        data = {'product_id': product.id, 'quantity': 2}
        
        response = self.api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Not enough stock' in response.data['error']
        assert self.cart.items.count() == 0

    def test_remove_item_from_cart(self, product_factory):
        product = product_factory.create(stock=10)
        # Add item first
        self.cart.items.create(product=product, quantity=1)
        assert self.cart.items.count() == 1

        url = reverse('cart:cart-remove-item')
        data = {'product_id': product.id}
        
        response = self.api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert self.cart.items.count() == 0

    def test_update_item_quantity(self, product_factory):
        product = product_factory.create(stock=10)
        self.cart.items.create(product=product, quantity=1)
        
        url = reverse('cart:cart-update-quantity')
        data = {'product_id': product.id, 'quantity': 5}
        
        response = self.api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        self.cart.refresh_from_db()
        assert self.cart.items.first().quantity == 5

    def test_clear_cart(self, product_factory):
        product1 = product_factory.create(stock=10)
        product2 = product_factory.create(stock=10)
        self.cart.items.create(product=product1, quantity=1)
        self.cart.items.create(product=product2, quantity=2)
        assert self.cart.items.count() == 2

        url = reverse('cart:cart-clear')
        response = self.api_client.post(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert self.cart.items.count() == 0
