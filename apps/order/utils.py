import datetime
import os

from random import randint

from apps.cart.cart import Cart

from apps.order.models import Order, OrderItem

def checkout(request, first_name):
    order = Order(first_name=first_name)
    order.save()

    cart = Cart(request)

    for item in cart:
        OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
    
    return order.id