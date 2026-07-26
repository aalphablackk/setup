from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("all_products", views.all_products, name="all_products"),
    path("product/<int:product_id>/",views.product_detail,name="product_detail"),
]
