from django.urls import path
from django.views.i18n import set_language
from .views import views, views_parital, views_api

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    # Page views
    path("create-wanted/", views.create_wanted_view, name="create_wanted"),
    path("wanted/", views.wanted_view, name="wanted"),
    path("familiar/", views.familiar_view, name="familiar"),
    # API views
    path("api/set-lang/", set_language, name="set_language"),
    path(
        "api/buy-all/<wanted_id>/", views_api.buy_all_cards_view, name="buy_all_cards"
    ),
    path("api/buy-card/<resource_id>/", views_api.buy_card_view, name="buy_card"),
    # Partial views (htmx)
    path(
        "wanted/<int:wanted_id>/",
        views_parital.wanted_detail_view,
        name="wanted_detail",
    ),
    path(
        "familiar/<int:familiar_id>/",
        views_parital.familiar_detail_view,
        name="familiar_detail",
    ),
    path(
        "add-value/<int:resource_id>/", views_parital.add_value_view, name="add_value"
    ),
    path(
        "add-sell-value/<int:resource_id>/",
        views_parital.add_sell_value_view,
        name="add_sell_value",
    ),
    path(
        "all-price-cards/<int:wanted_id>/",
        views_parital.get_all_price_card_view,
        name="all_price_cards",
    ),
]
