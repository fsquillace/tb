'''
Created on Nov 21, 2012

@author: Filippo Squillace
'''

from django.contrib import admin
from travelapp.models import MailingList, Account


AUDIT_FIELDS = ('date_created', 'date_updated')

class AccountAdmin(admin.ModelAdmin):
    filter_vertical = ('mailing_lists',)
    list_display = ('last_name', 'first_name', 'resource_uri') + AUDIT_FIELDS

    fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': ('first_name', 'last_name', 'birth_date', 'gender',\
                        'city', 'country', 'street_number', 'zipcode',\
                        'phone', 'email')
        }),
        ('Advanced options', {
            'classes': ('collapse', 'wide', 'extrapretty'),
            'fields': ('lead', 'mailing_lists')
        }),
    )



class MailingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_uri') + AUDIT_FIELDS

    def has_add_permission(self, request):
        return False
    

admin.site.register(MailingList, MailingListAdmin)
admin.site.register(Account, AccountAdmin)
