import json
from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.formats import number_format
from django.views.decorators.http import require_POST

from apps.tracker.forms import ResourceValueForm
from apps.tracker.models import Resource, ResourceType, ResourceValue, SellOut


@require_POST
def wanted_detail_view(request, wanted_id):
    wanted = get_object_or_404(Resource, id=wanted_id)
    if wanted.resource_type != ResourceType.WANTED.value:
        raise Http404("Wanted not found")

    wanted.add_stats()

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

    wanted.all_card_price_formatted = (
        number_format(wanted.all_card_price, force_grouping=True)
        if wanted.all_card_price
        else "N/A"
    )

    wanted.days_values = json.dumps(wanted.days_values)
    wanted.days_labels = json.dumps(wanted.days_labels)

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


@require_POST
def add_value_view(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    form = ResourceValueForm(request.POST)
    if not form.is_valid():
        raise NotImplementedError("Form validation not implemented yet")

    value = form.cleaned_data["price"]
    ResourceValue.objects.create(resource=resource, price=value)

    resource.add_stats()

    response = render(
        request, "tracker/partials/resource-price.html", {"resource": resource}
    )
    response["HX-Trigger"] = "resourceValueAdded"
    return response


@require_POST
def get_all_price_card_view(request, wanted_id):
    wanted = get_object_or_404(Resource, id=wanted_id)
    if wanted.resource_type != ResourceType.WANTED.value:
        raise Http404("Wanted not found")

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

    wanted.all_card_price_formatted = (
        number_format(wanted.all_card_price, force_grouping=True)
        if wanted.all_card_price
        else "N/A"
    )

    response = render(
        request,
        "tracker/partials/all-card-price.html",
        {"wanted": wanted},
    )
    return response
