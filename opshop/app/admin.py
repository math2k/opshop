from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User

from app.models import UserProfile, SaleLine, Sale, Item, Transaction
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'balance')

    def balance(self, obj):
        return obj.profile.balance


class SaleInlineAdmin(admin.StackedInline):
    model = SaleLine

    def get_extra(self, request, obj=None, **kwargs):
        if obj is not None:
            return 0
        return 1

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ['item', 'quantity']
        return []


class ItemAdmin(ModelAdmin):
    list_display = ('name', 'price', 'quantity')


class SaleAdmin(ModelAdmin):
    inlines = (SaleInlineAdmin,)
    list_display = ('user', 'total', 'datetime')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ['datetime', 'total', 'user', 'payment_mode']
        return []


class TransactionAdmin(ModelAdmin):

    list_display = ('user', 'amount', 'datetime')
    list_display_links = None

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ['datetime', 'amount', 'user']
        return []

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Transaction, TransactionAdmin)