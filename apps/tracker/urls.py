from django.urls import path
from . import views

urlpatterns = [
    path("create-wanted/", views.create_wanted_view, name="create_wanted"),
]
