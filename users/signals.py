from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from cart.models import Cart

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart(sender, instance=None, created=False, **kwargs):
    """
    Create a cart for a new user.
    """
    if created:
        Cart.objects.create(user=instance)
