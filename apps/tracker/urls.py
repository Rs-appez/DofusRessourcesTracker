from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("create-wanted/", views.create_wanted_view, name="create_wanted"),
    path("wanted/", views.wanted_view, name="wanted"),
    path("wanted/<int:wanted_id>/", views.wanted_detail_view, name="wanted_detail"),
]
