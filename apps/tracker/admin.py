from django.contrib import admin
from .models import Ressource, RessourceValue, BuyIn, SellOut, RessourceImage

admin.site.register(RessourceValue)
admin.site.register(BuyIn)
admin.site.register(SellOut)
admin.site.register(RessourceImage)


@admin.register(Ressource)
class ResourceAdmin(admin.ModelAdmin):
    save_as = True
