import pytest
from users.factories import UserFactory
from products.factories import ProductFactory

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def product_factory():
    return ProductFactory

@pytest.fixture
def api_client():
  from rest_framework.test import APIClient
  return APIClient()

@pytest.fixture
def authenticated_user(db, user_factory):
    def create_user(**kwargs):
        return user_factory.create(**kwargs)
    return create_user

@pytest.fixture
def api_client_authenticated(db, authenticated_user, api_client):
    user = authenticated_user()
    api_client.force_authenticate(user=user)
    return api_client, user
