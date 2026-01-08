from django.urls import path
from . import views
from . import views_parital

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("create-wanted/", views.create_wanted_view, name="create_wanted"),
    path("wanted/", views.wanted_view, name="wanted"),
    # Partial views (htmx)
    path(
        "wanted/<int:wanted_id>/",
        views_parital.wanted_detail_view,
        name="wanted_detail",
    ),
    path(
        "add-value/<int:resource_id>/", views_parital.add_value_view, name="add_value"
    ),
]
