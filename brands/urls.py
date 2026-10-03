from django.urls import path

from . import views


app_name = "brands"


urlpatterns = [
    path(
        "",
        views.brand_list,
        name="list",
    ),

    path(
        "create/",
        views.brand_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.brand_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.brand_update,
        name="update",
    ),
# Brand Brain
    path(
        "<int:pk>/knowledge/",
        views.brand_knowledge,
        name="knowledge",
    ),

    path(
        "<int:pk>/knowledge/save/",
        views.brand_knowledge_save,
        name="knowledge_save",
    ),
]