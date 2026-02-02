import logging
from django.db import transaction
from cart.models import Cart
from cart.services import CartService
from products.models import Product
from .models import Order, OrderItem
from users.models import User

logger = logging.getLogger(__name__)

class OrderCreationError(Exception):
    pass

class OrderService:
    @staticmethod
    def create_order(user: User) -> Order:
        cart = Cart.objects.prefetch_related('items__product').get(user=user)

        if not cart.items.exists():
            raise OrderCreationError("Cannot create an order from an empty cart.")

        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        if user.balance < total_price:
            raise OrderCreationError(f"Insufficient funds. Required: {total_price}, Available: {user.balance}")

        with transaction.atomic():
            # Lock user and product rows to prevent race conditions
            user_for_update = User.objects.select_for_update().get(pk=user.pk)
            
            # Check stock availability again inside the transaction
            for item in cart.items.all():
                product_for_update = Product.objects.select_for_update().get(id=item.product.id)
                if product_for_update.stock < item.quantity:
                    raise OrderCreationError(
                        f"Not enough stock for {product_for_update.title}. Available: {product_for_update.stock}"
                    )
                product_for_update.stock -= item.quantity
                product_for_update.save()

            user_for_update.balance -= total_price
            user_for_update.save()

            order = Order.objects.create(user=user_for_update, total_price=total_price)

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                ) for item in cart.items.all()
            ]
            OrderItem.objects.bulk_create(order_items)

            CartService.clear_cart(cart)

        logger.info(f"Successfully created Order {order.id} for user {user.email}. Total price: {total_price}")
        return order
