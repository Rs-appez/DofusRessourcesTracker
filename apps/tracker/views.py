from apps.tracker.models import ResourceImage, Resource
from django.shortcuts import redirect
from django.shortcuts import render


def dashboard_view(request):
    return render(request, "tracker/dashboard.html")

def wanted_view(request):
    wanteds = Resource.objects.filter(resource_type=5)
    return render(request, "tracker/wanted.html", {"wanteds": wanteds})

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

    ress = Resource.objects.create(name=name, image=ress_img, resource_type=5)
    card = Resource.objects.create(
        name=f"Carte de {wanted_name}",
        image=card_img,
        resource_type=6,
    )
    card.use_in.add(ress)

    for i in range(int(nb)):
        Resource.objects.create(
            name=f"Fragment de carte {wanted_name} {i + 1}/{nb}",
            image=frag_img,
            resource_type=6,
        ).use_in.add(card)

    return redirect("create_wanted")
