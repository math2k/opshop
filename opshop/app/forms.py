from django import forms
from django.contrib.auth.models import User

from app.models import Sale, Item


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return "{0} ({1})".format(obj.username, obj.profile.balance)


class SaleForm(forms.ModelForm):
    user = UserModelChoiceField(queryset=User.objects.all())
    item = forms.ModelChoiceField(queryset=Item.objects.all())

    class Meta:
        model = Sale
        exclude = []
