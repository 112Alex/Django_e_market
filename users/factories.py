import factory
from django.contrib.auth import get_user_model

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('email',)

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: f'{o.first_name.lower()}.{o.last_name.lower()}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    is_staff = False
    is_superuser = False
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default `_create` method to use our custom manager."""
        manager = cls._get_manager(model_class)
        # The default create_user manager method can't be used with is_staff=True, etc.
        # So we have to separate creation of staff and non-staff users
        if kwargs.get('is_staff') or kwargs.get('is_superuser'):
            return manager.create_superuser(*args, **kwargs)
        return manager.create_user(*args, **kwargs)
