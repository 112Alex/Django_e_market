from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .services import OrderService, OrderCreationError

class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """
    A ViewSet for creating, listing and retrieving orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the orders
        for the currently authenticated user.
        """
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def create(self, request, *args, **kwargs):
        """
        Create a new order from the user's cart.
        """
        try:
            order = OrderService.create_order(user=request.user)
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except OrderCreationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)