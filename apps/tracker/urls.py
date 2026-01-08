from django.urls import path
from .views import views, views_parital, views_api

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    # Page views
    path("create-wanted/", views.create_wanted_view, name="create_wanted"),
    path("wanted/", views.wanted_view, name="wanted"),
    # API views
    path(
        "api/buy-all/<wanted_id>/", views_api.buy_all_cards_view, name="buy_all_cards"
    ),
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
