import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.fixture
def admin_api_client(db, authenticated_user, api_client):
    user = authenticated_user(is_staff=True, is_superuser=True)
    api_client.force_authenticate(user=user)
    return api_client

class TestProductEndpoints:
    def test_list_products_anonymous(self, api_client, product_factory):
        product_factory.create_batch(3)
        url = reverse('products:product-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_retrieve_product_anonymous(self, api_client, product_factory):
        product = product_factory.create()
        url = reverse('products:product-detail', kwargs={'pk': product.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == product.title

    def test_create_product_admin(self, admin_api_client):
        url = reverse('products:product-list')
        data = {'title': 'New Product', 'price': '19.99', 'stock': 10}
        response = admin_api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Product'

    def test_create_product_regular_user_forbidden(self, api_client_authenticated):
        api_client, _ = api_client_authenticated
        url = reverse('products:product-list')
        data = {'title': 'New Product', 'price': '19.99', 'stock': 10}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_product_admin(self, admin_api_client, product_factory):
        product = product_factory.create()
        url = reverse('products:product-detail', kwargs={'pk': product.pk})
        data = {'price': '25.50'}
        response = admin_api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['price'] == '25.50'

    def test_update_product_regular_user_forbidden(self, api_client_authenticated, product_factory):
        api_client, _ = api_client_authenticated
        product = product_factory.create()
        url = reverse('products:product-detail', kwargs={'pk': product.pk})
        data = {'price': '25.50'}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_product_admin(self, admin_api_client, product_factory):
        product = product_factory.create()
        url = reverse('products:product-detail', kwargs={'pk': product.pk})
        response = admin_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_product_regular_user_forbidden(self, api_client_authenticated, product_factory):
        api_client, _ = api_client_authenticated
        product = product_factory.create()
        url = reverse('products:product-detail', kwargs={'pk': product.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
