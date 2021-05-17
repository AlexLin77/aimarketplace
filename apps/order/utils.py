import datetime
import os

from random import randint

from apps.cart.cart import Cart

from apps.order.models import Order, OrderItem

from apps.algos.data import Userdata

def checkout(request, first_name):
    order = Order(first_name=first_name)

    if request.user.is_authenticated:
        order.user = request.user

    order.save()

    cart = Cart(request)
    dataset = Userdata(request)

    for item in cart:
        OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
        if request.user.is_authenticated:
            dataset.add(product=item['product'], username=request.user.username, weight=1.5)
        else:
            dataset.add(product=item['product'], username='guest', weight=1.5)
    
    return order.id