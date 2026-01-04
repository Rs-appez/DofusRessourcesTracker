from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("create-wanted/", views.create_wanted_view, name="create_wanted"),
    path("wanted/", views.wanted_view, name="wanted"),
]
