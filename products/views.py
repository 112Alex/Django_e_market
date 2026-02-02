from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAdminOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]