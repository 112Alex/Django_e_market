from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart
from .serializers import CartSerializer, CartItemAddSerializer
from .services import CartService

class CartViewSet(viewsets.GenericViewSet):
    """
    A ViewSet for retrieving and managing the user's cart.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'add_item':
            return CartItemAddSerializer
        return CartSerializer

    def list(self, request):
        """Get the current user's cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add a product to the cart."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = request.user.cart
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            CartService.add_item(cart, product_id, quantity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove a product from the cart."""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        cart = request.user.cart
        try:
            CartService.remove_item(cart, product_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Update the quantity of a product in the cart."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        if not all([product_id, quantity]):
            return Response({"error": "product_id and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = request.user.cart
        try:
            CartService.update_item_quantity(cart, product_id, int(quantity))
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from the cart."""
        cart = request.user.cart
        CartService.clear_cart(cart)
        return Response(status=status.HTTP_204_NO_CONTENT)