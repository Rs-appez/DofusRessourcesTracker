from django.contrib import admin
from .models import Resource, RessourceValue, BuyIn, SellOut

admin.site.register(RessourceValue)
admin.site.register(BuyIn)
admin.site.register(SellOut)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    save_as = True
