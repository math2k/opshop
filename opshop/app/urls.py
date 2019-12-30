from django.conf.urls import url

from app.views import *

urlpatterns = [
    url(r'^create-account$', CreateAccountFormView.as_view(), name='create-account'),
    url(r'^top-up$', TopUpFormView.as_view(), name='top-up'),
    url(r'^$', SaleFormView.as_view(), name='sale'),
    url(r'^list-items$', ListItemsJsonView.as_view(), name='list-items'),
    url(r'^user$', GetUserJsonView.as_view(), name='get-user'),
    url(r'^item$', GetItemJsonView.as_view(), name='get-item'),
    url(r'^balance$', GetBalanceJsonView.as_view(), name='get-balance'),
    url(r'^pay$', PayJsonView.as_view(), name='pay'),
]
