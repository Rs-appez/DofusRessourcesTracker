from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.tracker.models import BuyIn, ResourceValue, SellOut

from .forms import ResourceValueForm
from .models import Resource, ResourceImage, ResourceType


def dashboard_view(request):
    return render(request, "tracker/dashboard.html")


def wanted_view(request):
    wanteds = Resource.objects.filter(resource_type=ResourceType.WANTED.value)
    return render(request, "tracker/wanted.html", {"wanteds": wanteds})


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


def create_wanted_view(request):
    if request.method == "GET":
        return render(request, "tracker/createWanted.html")

    name = request.POST.get("name")
    wanted_name = request.POST.get("wanted_name")
    nb = request.POST.get("nb")
    image = request.FILES.get("image")

    card_img = ResourceImage.objects.get(name="Carte")
    frag_img = ResourceImage.objects.get(name="Fragment carte")

    ress_img, created = ResourceImage.objects.get_or_create(name=name)
    if created:
        ress_img.image.save(image.name, image)

    ress = Resource.objects.create(
        name=name, image=ress_img, resource_type=ResourceType.WANTED.value
    )
    card = Resource.objects.create(
        name=f"Carte de {wanted_name}",
        image=card_img,
        resource_type=ResourceType.CARD.value,
    )
    card.use_in.add(ress)

    for i in range(int(nb)):
        Resource.objects.create(
            name=f"Fragment de carte {wanted_name} {i + 1}/{nb}",
            image=frag_img,
            resource_type=ResourceType.CARD.value,
        ).use_in.add(card)

    return redirect("tracker:create_wanted")


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
