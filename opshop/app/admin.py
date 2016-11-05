from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User

from app.models import UserProfile, SaleLine, Sale, Stock, Item
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class SaleInlineAdmin(admin.StackedInline):
    model = SaleLine
    extra = 1


class SaleAdmin(ModelAdmin):
    inlines = (SaleInlineAdmin,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Item)
admin.site.register(Stock)
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleLine)