from django.urls import include, path

from .views import *

urlpatterns = [
    path("", home_view, name="home"),
]
