# coding=utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    ean = models.CharField(max_length=13, primary_key=True)
    quantity = models.IntegerField()
    last_refill = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u"{0} - {1}".format(self.name, self.price)


class Transaction(models.Model):
    user = models.ForeignKey(to=User)
    datetime = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return u"{0} - {1}€ available".format(self.user.username, self.amount)


class Sale(models.Model):
    user = models.ForeignKey(to=User, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        total = 0
        for sl in self.saleline_set.all():
            total += sl.quantity * sl.item.price
        return total

    def __unicode__(self):
        return u"{0} ({1})".format(self.user, self.total)


class SaleLine(models.Model):
    sale = models.ForeignKey(to=Sale)
    item = models.ForeignKey(to=Item)
    quantity = models.IntegerField()

    def __unicode__(self):
        return u"{0} ({1})".format(self.item.name, self.quantity)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=6, decimal_places=2)


@receiver(post_save, sender=Transaction)
def update_balance_from_transaction(sender, instance, **kwargs):
    def on_commit():
        if not kwargs['created']:
            # Shouldn't update a transaction.
            return
        instance.user.profile.balance += instance.amount
        instance.user.profile.save()

    from django.db import transaction
    transaction.on_commit(on_commit)


@receiver(post_save, sender=SaleLine)
def update_stock_from_sale(sender, instance, **kwargs):
    def on_commit():
        if not kwargs['created']:
            # Shouldn't update a sale.
            return
        instance.item.quantity -= instance.quantity
        instance.item.save()

    from django.db import transaction
    transaction.on_commit(on_commit)


class Delivery(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return sum(l.paid for l in self.deliveryline_set.all())


class DeliveryLine(models.Model):
    delivery = models.ForeignKey(Delivery, null=True)
    item = models.CharField(max_length=255)
    boxes = models.IntegerField()
    items_per_box = models.IntegerField()
    box_price = models.DecimalField(decimal_places=2, max_digits=3)
    price = models.DecimalField(decimal_places=2, max_digits=3)

    @property
    def individual_price(self):
        return self.box_price / self.items_per_box

    @property
    def suggested_retail_price(self):
        return self.individual_price * 1.1

    @property
    def paid(self):
        return self.boxes * self.box_price

