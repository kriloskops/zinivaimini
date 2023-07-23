from django import forms
from .models import Player
from django.core.exceptions import ValidationError

class NameForm(forms.Form):
    username = forms.CharField(max_length=30, label="Ieraksti savu vārdu.", widget=forms.TextInput(attrs={"class": "form-label"}))


    def clean_username(self):
        org_data = self.cleaned_data["username"]
        data = self.cleaned_data["username"]
        counter = 2
        while (Player.objects.filter(username=data).count() > 0):
            data = f"{org_data}_{counter}"
            counter += 1
        return data


