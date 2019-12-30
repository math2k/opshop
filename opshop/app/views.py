# coding=utf-8
import random
import string

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, View
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from app.forms import SaleForm, TopUpForm, AccountForm
from app.models import Sale, SaleLine, Transaction, Item, UserProfile

class SharedSecretMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_SECRET') == settings.SHARED_SECRET:
           
	    return super(SharedSecretMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(request.META)

class SaleFormView(CreateView):
    form_class = SaleForm
    model = Sale
    template_name = "app/sale.html"

    def get_context_data(self, **kwargs):
        context = super(SaleFormView, self).get_context_data(**kwargs)
        context['sale'] = self.request.GET.get('sale')
        context['items'] = Item.objects.all().order_by('name')
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
        if self.object.user.profile.balance > 0:
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

class PayJsonView(SharedSecretMixin, View):

    allowed_methods = ['POST']
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PayJsonView, self).dispatch(*args, **kwargs)

    def post(self, request):
	user_profile = UserProfile.objects.get(badge=request.POST.get('badge'))
	user = user_profile.user
	item = Item.objects.get(code=request.POST.get('code'))
	sale = Sale(user=user)
	sale.save()
	sl = SaleLine(quantity=1, item=item, sale=sale)
        sl.save()
        t = Transaction(user=user, amount=-sale.total)
        t.save()
	return HttpResponse()
	
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

class ListItemsJsonView(SharedSecretMixin, View):
    def get(self, request):
    	return JsonResponse(["{} - {}€".format(i.name, i.price) for i in Item.objects.all().order_by('name')], safe=False)

class GetUserJsonView(SharedSecretMixin, View):
    def get(self, request):
    	user_profile = UserProfile.objects.filter(badge=self.request.GET.get('badge')).first()
	if user_profile:	
		return JsonResponse(user_profile.user.username, safe=False)
	raise Http404

class GetBalanceJsonView(SharedSecretMixin, View):
    def get(self, request):
    	user_profile = UserProfile.objects.filter(badge=self.request.GET.get('badge')).first()
	if user_profile:	
		return JsonResponse(user_profile.balance, safe=False)
	raise Http404

class GetItemJsonView(SharedSecretMixin, View):
    def get(self, request):
    	item = Item.objects.filter(code=self.request.GET.get('code')).first()
	if item:	
		return JsonResponse({'id':item.code, 'name': item.name, 'price': item.price}, safe=False)
	raise Http404
