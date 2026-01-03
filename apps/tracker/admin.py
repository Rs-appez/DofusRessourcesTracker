from django.contrib import admin
from .models import Resource, RessourceValue, BuyIn, SellOut

admin.site.register(Resource)
admin.site.register(RessourceValue)
admin.site.register(BuyIn)
admin.site.register(SellOut)
