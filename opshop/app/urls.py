from django.conf.urls import url

from app.views import SaleFormView, TopUpFormView, CreateAccountFormView

urlpatterns = [
    url(r'^create-account$', CreateAccountFormView.as_view(), name='create-account'),
    url(r'^top-up$', TopUpFormView.as_view(), name='top-up'),
    url(r'^$', SaleFormView.as_view(), name='sale'),
]
