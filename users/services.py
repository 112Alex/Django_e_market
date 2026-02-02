from decimal import Decimal
from django.db import transaction
from .models import User

class BalanceService:
    @staticmethod
    def deposit(user: User, amount: Decimal) -> User:
        """
        Deposits a given amount to the user's balance.
        Uses a transaction to ensure atomicity.
        """
        with transaction.atomic():
            # Use select_for_update to lock the row for the duration of the transaction
            user_to_update = User.objects.select_for_update().get(pk=user.pk)
            user_to_update.balance += amount
            user_to_update.save(update_fields=['balance'])
        
        user.refresh_from_db()
        return user
