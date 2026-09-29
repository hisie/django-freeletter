from django import forms
from django.utils.translation import gettext_lazy as _


class SubscribeForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    name = forms.CharField(label=_("Name"), required=False)
