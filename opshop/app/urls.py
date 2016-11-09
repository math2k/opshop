from django.conf.urls import url

from app.views import SaleFormView

urlpatterns = [
    url(r'^$', SaleFormView.as_view(), name='sale'),
]
