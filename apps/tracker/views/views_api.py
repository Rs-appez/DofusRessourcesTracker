from django.http.response import HttpResponse
from django.db.models.expressions import Subquery
from django.db.models.expressions import OuterRef
from django.views.decorators.http import require_http_methods

from apps.tracker.models import BuyIn, Resource, ResourceType, ResourceValue


@require_http_methods(["POST"])
def buy_all_cards_view(request, wanted_id):
    latest_value = (
        ResourceValue.objects.filter(resource=OuterRef("pk"))
        .order_by("-timestamp")
        .values("value")[:1]
    )

    fragments = Resource.objects.filter(
        use_in__use_in__id=wanted_id,
        resource_type=ResourceType.CARD.value,
    ).annotate(latest_value=Subquery(latest_value))

    if not fragments:
        return HttpResponse("No fragments found for the wanted item", status=404)

    BuyIn.objects.bulk_create(
        [
            BuyIn(
                resource=fragment,
                price=fragment.latest_value if fragment.latest_value else 0,
                quantity=1,
            )
            for fragment in fragments
        ]
    )

    return HttpResponse("Buy all cards executed", status=200)
