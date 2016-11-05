from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    ean = models.CharField(max_length=50)

    def __unicode__(self):
        return u"{0}".format(self.name)


class Stock(models.Model):
    item = models.ForeignKey(to=Item)
    quantity = models.IntegerField()
    last_refill = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u"{0} ({1})".format(self.item.name, self.quantity)


class Sale(models.Model):
    user = models.ForeignKey(to=User, null=True)
    payment_mode = models.CharField(choices=(('cash', 'Cash'), ('credit', 'Credit')), max_length=50)

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


@receiver(post_save, sender=Sale)
def update_balance(sender, instance, **kwargs):
    def on_commit():
        if not kwargs['created']:
            # Shouldn't update a sale. sales are final.
            return
        if instance.payment_mode == 'credit':
            instance.user.profile.balance -= instance.total
            instance.user.profile.save()

    from django.db import transaction
    transaction.on_commit(on_commit)

