import pytest
from users.models import User

pytestmark = pytest.mark.django_db

def test_create_user(user_factory):
    user = user_factory.create()
    assert isinstance(user, User)
    assert user.email is not None
    assert not user.is_staff
    assert not user.is_superuser

def test_create_superuser(user_factory):
    admin_user = user_factory.create(is_staff=True, is_superuser=True)
    assert isinstance(admin_user, User)
    assert admin_user.is_staff
    assert admin_user.is_superuser

def test_create_user_without_email_raises_error():
    with pytest.raises(ValueError, match="The given email must be set"):
        User.objects.create_user(email=None, password="password123")

def test_create_superuser_without_is_staff_raises_error(user_factory):
    with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
        user_factory.create(is_staff=False, is_superuser=True)

def test_create_superuser_without_is_superuser_raises_error(user_factory):
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
        user_factory.create(is_staff=True, is_superuser=False)
