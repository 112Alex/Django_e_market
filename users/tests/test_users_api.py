import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from decimal import Decimal

pytestmark = pytest.mark.django_db

class TestUserEndpoints:
    def test_user_registration(self, api_client, user_factory):
        url = reverse('users:register')
        user_data = user_factory.build()
        data = {
            'email': user_data.email,
            'password': 'password123',
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data.email).exists()

    def test_user_login(self, api_client, authenticated_user):
        user = authenticated_user(email='test@example.com', password='password123')
        url = reverse('users:token_obtain_pair')
        data = {'email': 'test@example.com', 'password': 'password123'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_get_user_profile(self, api_client_authenticated):
        api_client, user = api_client_authenticated
        url = reverse('users:profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_update_user_profile(self, api_client_authenticated):
        api_client, user = api_client_authenticated
        url = reverse('users:profile')
        data = {'first_name': 'Updated Name'}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated Name'

    def test_balance_deposit(self, api_client_authenticated):
        api_client, user = api_client_authenticated
        url = reverse('users:balance')
        initial_balance = user.balance
        
        data = {'amount': '50.00'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        
        assert user.balance == initial_balance + Decimal('50.00')
        assert Decimal(response.data['new_balance']) == user.balance


    def test_balance_deposit_negative_amount(self, api_client_authenticated):
        api_client, user = api_client_authenticated
        url = reverse('users:balance')
        data = {'amount': '-50.00'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

