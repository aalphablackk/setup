from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard_home,name='dashboard_home'),
    path('product_list/',views.product_list,name='product_list'),
    path('product/add/',views.product_add,name='product_add'),
    # path("products/<int:product_id>/images/",views.product_images,name="product_images"),
    path("products/<int:product_id>/specifications/",views.product_specifications,name="product_specifications"),
    path("products/edit/<int:product_id>/",views.product_edit,name="product_edit"),



    path(
    "products/<int:product_id>/images/",
    views.product_images,
    name="product_images"
),


path(
    "images/delete/<int:image_id>/",
    views.delete_product_image,
    name="delete_product_image"
),



path(
    "images/set-cover/<int:image_id>/",
    views.set_cover_image,
    name="set_cover_image"
),

path(
    "specifications/delete/<int:specification_id>/",
    views.delete_specification,
    name="delete_specification"
),


path(
    "specifications/edit/<int:specification_id>/",
    views.edit_specification,
    name="edit_specification"
),

path(
    "products/delete/<int:product_id>/",
    views.product_delete,
    name="product_delete"
),
]
