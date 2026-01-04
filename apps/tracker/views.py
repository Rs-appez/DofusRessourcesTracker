from apps.tracker.models import BuyIn
from apps.tracker.models import SellOut
from apps.tracker.models import ResourceValue
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.tracker.models import Resource, ResourceImage, ResourceType


def dashboard_view(request):
    return render(request, "tracker/dashboard.html")


def wanted_view(request):
    wanteds = Resource.objects.filter(resource_type=ResourceType.WANTED.value)
    return render(request, "tracker/wanted.html", {"wanteds": wanteds})


def wanted_detail_view(request, wanted_id):
    wanted = get_object_or_404(Resource, id=wanted_id)
    if wanted.resource_type != ResourceType.WANTED.value:
        raise Http404("Wanted not found")

    last_wanted_value = ResourceValue.get_last_value(wanted)
    average_wanted_values = ResourceValue.get_average_price(wanted, days=30)
    last_wanted_sell_value = SellOut.get_last_sell_out_price(wanted)
    average_wanted_sell_values = SellOut.get_average_sell_out_price(wanted, days=30)

    card = Resource.objects.filter(
        use_in=wanted, resource_type=ResourceType.CARD.value
    ).first()

    last_card_value = ResourceValue.get_last_value(card)
    average_card_values = ResourceValue.get_average_price(card, days=30)
    last_card_buy_value = BuyIn.get_last_buy_in_price(card)
    average_card_buy_values = BuyIn.get_average_buy_in_price(card, days=30)

    fragments = Resource.objects.filter(
        use_in=card, resource_type=ResourceType.CARD.value
    ).order_by("name")

    return render(
        request,
        "tracker/wanted_detail.html",
        {
            "wanted": wanted,
            "card": card,
            "fragments": fragments,
            "last_wanted_value": last_wanted_value or "Unknown",
            "average_wanted_values": average_wanted_values or "Unknown",
            "last_wanted_sell_value": last_wanted_sell_value or "Unknown",
            "average_wanted_sell_values": average_wanted_sell_values or "Unknown",
            "last_card_value": last_card_value or "Unknown",
            "average_card_values": average_card_values or "Unknown",
            "last_card_buy_value": last_card_buy_value or "Unknown",
            "average_card_buy_values": average_card_buy_values or "Unknown",
        },
    )


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

    return redirect("create_wanted")
