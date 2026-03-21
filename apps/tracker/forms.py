from django import forms

from apps.tracker.models import SellOut, ResourceValue


class ResourceValueForm(forms.ModelForm):
    class Meta:
        model = ResourceValue
        fields = ["price"]


class SellOutValueForm(forms.ModelForm):
    class Meta:
        model = SellOut
        fields = ["price", "quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quantity"].initial = 1
