# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms import widgets

from app.models import Sale, Item


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return "{0} ({1}€ available)".format(obj.username, obj.profile.balance)


class SaleForm(forms.ModelForm):

    item = forms.ModelChoiceField(queryset=Item.objects.all())
    user = UserModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = Sale
        exclude = []
