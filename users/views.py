from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, BalanceUpdateSerializer
from .services import BalanceService

class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserBalanceView(generics.GenericAPIView):
    """
    API view for updating user balance.
    """
    serializer_class = BalanceUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        user = request.user
        
        # Use the service to update the balance
        BalanceService.deposit(user, amount)
        
        return Response({"status": "success", "new_balance": user.balance}, status=status.HTTP_200_OK)