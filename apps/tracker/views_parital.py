from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import ResourceValue, SellOut, Resource, ResourceType

from .forms import ResourceValueForm


@require_http_methods(["POST"])
def wanted_detail_view(request, wanted_id):
    wanted = get_object_or_404(Resource, id=wanted_id)
    if wanted.resource_type != ResourceType.WANTED.value:
        raise Http404("Wanted not found")

    wanted.add_stats()
    wanted.last_sell_value = SellOut.get_last_sell_out_price(wanted)
    wanted.average_sell_values = SellOut.get_average_sell_out_price(wanted, days=30)

    card = Resource.objects.filter(
        use_in=wanted, resource_type=ResourceType.CARD.value
    ).first()

    fragments = Resource.objects.filter(
        use_in=card, resource_type=ResourceType.CARD.value
    ).order_by("name")

    cards = list(fragments) + [card]

    for card in cards:
        card.add_stats()

    wanted.all_card_price = sum(
        [card.current_value for card in cards[:-1] if card.current_value]
    )

    form = ResourceValueForm()
    context = {
        "form": form,
        "wanted": wanted,
        "cards": cards,
    }

    response = render(
        request,
        "tracker/partials/wanted-detail.html",
        context,
    )
    response["HX-Trigger"] = "wantedDetailLoaded"
    return response


@require_http_methods(["POST"])
def add_value_view(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    form = ResourceValueForm(request.POST)
    if not form.is_valid():
        raise NotImplementedError("Form validation not implemented yet")

    value = form.cleaned_data["value"]
    ResourceValue.objects.create(resource=resource, value=value)

    resource.add_stats()

    response = render(
        request, "tracker/partials/resource-price.html", {"resource": resource}
    )
    response["HX-Trigger"] = "resourceValueAdded"
    return response
