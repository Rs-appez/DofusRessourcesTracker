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

    card = Resource.objects.filter(
        use_in=wanted, resource_type=ResourceType.CARD.value
    ).first()

    fragments = Resource.objects.filter(
        use_in=card, resource_type=ResourceType.CARD.value
    ).order_by("name")

    return render(
        request, "tracker/wanted_detail.html", {"wanted": wanted, "card": card, "fragments": fragments}
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
