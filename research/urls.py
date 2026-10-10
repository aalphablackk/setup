from django.urls import path

from . import views


app_name = "research"


urlpatterns = [
    path("", views.research_home, name="home"),
    path("create/", views.research_create, name="create"),
    path("<int:pk>/", views.research_detail, name="detail"),   
    path("<int:pk>/sources/add/", views.research_source_add, name="source_add"), 
    path("<int:pk>/run/",views.research_run,name="run",),
    path("<int:pk>/run-status/",views.research_run_status,name="run_status",),
    path("<int:pk>/sources/<int:source_pk>/remove/",views.research_source_remove,name="source_remove",),
]