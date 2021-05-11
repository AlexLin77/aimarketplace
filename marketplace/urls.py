"""marketplace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views

from apps.cart.views import cart_detail
from apps.core.views import frontpage, contact
from apps.store.views import product_detail, category_detail, search
from apps.userprofile.views import signup, myaccount

from apps.store.api import api_add_to_cart, api_remove_from_cart, api_checkout

urlpatterns = [
    path('', frontpage, name='frontpage'),
    path('search/', search, name='search'),
    path('cart/', cart_detail, name='cart'),
    path('contact/', contact, name='contact'),
    path('admin/', admin.site.urls),

    # Auth

    path('myaccount/', myaccount, name='myaccount'),
    path('signup/', signup, name='signup'),
    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # API

    path('api/add_to_cart/', api_add_to_cart, name='api_add_to_cart'),
    path('api/remove_from_cart/', api_remove_from_cart, name='api_remove_from_cart'),
    path('api/checkout/', api_checkout, name='api_checkout'),

    # Store
    path('<slug:category_slug>/<slug:slug>/',
         product_detail, name='product_detail'),
    path('<slug:slug>/', category_detail, name='category_detail'),

    path('', include('apps.core.urls')),
]
