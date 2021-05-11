from django.shortcuts import render

from apps.store.models import Product

from apps.algos.algorithms import refresh

# Create your views here.
def frontpage(request):
    refresh(request)

    products = Product.objects.filter(is_featured=True)

    context = {
        'products' : products
    }

    return render(request, 'core/frontpage.html', context)

def contact(request):
    return render(request, 'core/contact.html')