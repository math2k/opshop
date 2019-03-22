# coding=utf-8
import random
import string

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from app.forms import SaleForm, TopUpForm, AccountForm
from app.models import Sale, SaleLine, Transaction, Item


class SaleFormView(CreateView):
    form_class = SaleForm
    model = Sale
    template_name = "app/sale.html"

    def get_context_data(self, **kwargs):
        context = super(SaleFormView, self).get_context_data(**kwargs)
        context['sale'] = self.request.GET.get('sale')
        context['items'] = Item.objects.all()
        context['top_up_form'] = TopUpForm(prefix='top-up', initial=self.get_initial())
        context['account_form'] = AccountForm(prefix='account')
        return context

    def get_initial(self):
        return {'user': self.request.session.get('userid', '')}

    def form_valid(self, form):
        ret = super(SaleFormView, self).form_valid(form)
        sl = SaleLine(quantity=1, item=form.cleaned_data['item'], sale=self.object)
        sl.save()
        t = Transaction(user=self.object.user, amount=-self.object.total)
        t.save()
        self.request.session['userid'] = self.object.user.pk
        if self.object.user.profile.balance >= 0:
            messages.success(self.request,
                             "{0}€ have been substracted from your balance. You now have {1}€ available".format(
                                 self.object.total, self.object.user.profile.balance))
        else:
            messages.warning(self.request,
                             "{0}€ have been substracted from your balance. Your balance is negative! ({1}€)".format(
                                 self.object.total, self.object.user.profile.balance))
        return ret

    def get_success_url(self):
        return reverse_lazy('sale') + "?sale=1"


class TopUpFormView(FormView):

    form_class = TopUpForm
    template_name = "app/topup.html"
    prefix = "top-up"

    def form_valid(self, form):
        ret = super(TopUpFormView, self).form_valid(form)
        t = Transaction(user=form.cleaned_data['user'], amount=form.cleaned_data['amount'])
        t.save()
        messages.success(self.request, "{}€ have been added to your balance. You now have {}€ available".format(form.cleaned_data['amount'], form.cleaned_data['user'].profile.balance))
        return ret

    def get_initial(self):
        return {'user': self.request.session.get('userid', '')}

    def get_success_url(self):
        return reverse_lazy('sale')


class CreateAccountFormView(FormView):
    form_class = AccountForm
    template_name = "app/account.html"
    prefix = "account"

    def form_valid(self, form):
        ret = super(CreateAccountFormView, self).form_valid(form)
        email = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        u = User(username=form.cleaned_data['user'], password="xxxx", email=email+"@nowhere.eu")
        try:
            u.save()
            messages.success(self.request, "Your account has been created. You can now top up your account.")
        except IntegrityError as e:
            messages.error(self.request, "You're not the first one with that name.. pick another one!")
        return ret

    def get_success_url(self):
        return reverse_lazy('sale')
