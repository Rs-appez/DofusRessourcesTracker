from django.contrib import admin
from .models import Resource, ResourceValue, BuyIn, SellOut, ResourceImage

admin.site.register(ResourceValue)
admin.site.register(BuyIn)
admin.site.register(SellOut)
admin.site.register(ResourceImage)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    save_as = True
