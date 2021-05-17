import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from apps.cart.cart import Cart

from apps.algos.data import Userdata

from apps.order.utils import checkout

from .models import Product
from apps.order.models import Order


def api_checkout(request):
    cart = Cart(request)
    # dataset = Userdata(request)

    data = json.loads(request.body)
    jsonresponse = {'success': True}
    first_name = data['first_name']

    orderid = checkout(request, first_name)

    order = Order.objects.get(pk=orderid)
    order.save()

    cart.clear()
    # dataset.clear()

    return JsonResponse(jsonresponse)

def api_add_to_cart(request):
    data = json.loads(request.body)
    jsonresponse = {'success': True}
    product_id = data['product_id']
    update = data['update']
    quantity = data['quantity']

    cart = Cart(request)
    dataset = Userdata(request)

    product = get_object_or_404(Product, pk=product_id)

    if not update:
        cart.add(product=product, quantity=1, update_quantity=False)
        if request.user.is_authenticated:
            dataset.add(product=product, username=request.user.username, weight=1)
        else:
            dataset.add(product=product, username='guest', weight=1)
    else:
        cart.add(product=product, quantity=quantity, update_quantity=True)
        if request.user.is_authenticated:
            dataset.add(product=product, username=request.user.username, weight=1)
        else:
            dataset.add(product=product, username='guest', weight=1)

    return JsonResponse(jsonresponse)

def api_remove_from_cart(request):
    data = json.loads(request.body)
    jsonresponse = {'success': True}
    product_id = str(data['product_id'])

    cart = Cart(request)
    cart.remove(product_id)

    return JsonResponse(jsonresponse)
