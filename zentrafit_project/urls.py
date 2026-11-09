"""
URL configuration for zentrafit_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from tienda import views
from tienda import api_views
from tienda import admin_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/csrf/", api_views.csrf_token, name="api_csrf"),
    path("api/catalog/", api_views.catalog_api, name="api_catalog"),
    path("api/cart/", api_views.cart_api, name="api_cart"),
    path("api/orders/", api_views.order_api, name="api_orders"),
    path("api/admin/overview/", admin_api.overview, name="api_admin_overview"),
    path("api/admin/categories/", admin_api.categories, name="api_admin_categories"),
    path("api/admin/products/", admin_api.products, name="api_admin_products"),
    path("api/admin/variants/", admin_api.variants, name="api_admin_variants"),
    path("api/admin/inventory/", admin_api.inventory, name="api_admin_inventory"),
    path("api/admin/orders/", admin_api.orders, name="api_admin_orders"),
    path('', views.vistaCatalogo, name='catalogo'),
    path('carrito/add/<str:varianteId>/', views.agregarAlCarritoVista, name='agregar_carrito'),
]
