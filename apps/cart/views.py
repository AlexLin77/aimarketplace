from django.shortcuts import render

from .cart import Cart


def cart_detail(request):

    cart = Cart(request)
    productsstring = ''

    for item in cart:
        product = item['product']
        b = "{'id': '%s', 'title': '%s', 'price': '%s', 'quantity': '%s', 'total_price': '%s'}," % (product.id, product.title, product.price, item['quantity'], item['total_price'])
        productsstring = productsstring + b
    
    if request.user.is_authenticated:
        first_name = request.user.first_name
    else:
        first_name = 'guest'

    context = {
        'cart': cart,
        'first_name': first_name,
        'productsstring': productsstring
    }

    return render(request, 'cart.html', context)
