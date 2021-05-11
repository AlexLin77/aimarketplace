from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product, Category

from apps.algos.data import Dataset

def search(request):
    query = request.GET.get('query')
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

    context = {
      'query': query,
      'products': products
    }

    dataset = Dataset(request)

    for product in products:
        if request.user.is_authenticated:
            dataset.add(product, request.user.username, 0.5)
        else:
            dataset.add(product, 'guest', 0.5)

    return render(request, 'search.html', context)

def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)

    context = {
        'product' : product
    }

    return render(request, 'product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()

    context = {
        'category' : category,
        'products' : products
    }

    return render(request, 'category_detail.html', context)

