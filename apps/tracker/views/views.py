from django.shortcuts import redirect, render


from apps.tracker.models import Resource, ResourceImage, ResourceType


def dashboard_view(request):
    return render(request, "tracker/dashboard.html")


def wanted_view(request):
    wanteds = Resource.objects.filter(resource_type=ResourceType.WANTED.value)
    context = {
        "title": "Wanted",
        "list_template": "tracker/partials/wanted-list.html",
        "detail_template": "tracker/partials/wanted-detail.html",
        "resource_extra_css": "tracker/css/wanted-detail.css",
        "resource_extra_js": "tracker/js/wanted-detail.js",
    }
    context.update({"wanteds": wanteds})

    return render(request, "tracker/resource.html", context=context)


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
        name=f"Carte {wanted_name}",
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


def familiar_view(request):
    familiars = Resource.objects.filter(resource_type=ResourceType.FAMILIAR.value)
    print("familars : ", familiars)
    context = {
        "title": "Familier",
        "list_template": "tracker/partials/familiar-list.html",
        "detail_template": "tracker/partials/familiar-detail.html",
        "resource_extra_css": "tracker/css/familiar-detail.css",
        # "resource_extra_js": "tracker/js/familiar-detail.js",
    }
    context.update({"familiars": familiars})
    return render(request, "tracker/resource.html", context=context)
