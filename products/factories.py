import factory
from factory.django import DjangoModelFactory
from products.models import Product
from decimal import Decimal

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    title = factory.Faker('word')
    description = factory.Faker('sentence')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True, min_value=Decimal('1.00'))
    stock = factory.Faker('random_int', min=1, max=100)
