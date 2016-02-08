from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from apps.brahman.models import Organisation, RankedAffairVote, AffairVoteKarma


class OrganisationInline(admin.StackedInline):
    model = Organisation
    can_delete = False
    verbose_name_plural = 'Organisation'


class UserAdmin(BaseUserAdmin):
    inlines = (OrganisationInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(RankedAffairVote)
admin.site.register(AffairVoteKarma)
