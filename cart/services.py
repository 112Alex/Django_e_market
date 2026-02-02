from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from products.models import Product

class CartService:
    @staticmethod
    def add_item(cart: Cart, product_id: int, quantity: int) -> CartItem:
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock < quantity:
            raise ValueError(f"Not enough stock for {product.title}. Available: {product.stock}")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )
        
        new_quantity = cart_item.quantity + quantity
        if product.stock < new_quantity:
            raise ValueError(f"Not enough stock for {product.title}. Requested: {new_quantity}, Available: {product.stock}")

        cart_item.quantity = new_quantity
        cart_item.save()
        return cart_item

    @staticmethod
    def remove_item(cart: Cart, product_id: int):
        product = get_object_or_404(Product, id=product_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()

    @staticmethod
    def update_item_quantity(cart: Cart, product_id: int, quantity: int) -> CartItem:
        if quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
            
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock < quantity:
            raise ValueError(f"Not enough stock for {product.title}. Requested: {quantity}, Available: {product.stock}")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity = quantity
            cart_item.save()
            
        return cart_item
    
    @staticmethod
    def clear_cart(cart: Cart):
        cart.items.all().delete()
