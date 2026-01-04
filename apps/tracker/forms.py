from django import forms
from .models import ResourceValue


class ResourceValueForm(forms.ModelForm):
    class Meta:
        model = ResourceValue
        fields = ["value"]
