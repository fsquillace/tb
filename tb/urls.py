from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from travelapp.views import account_lead, mailing_list

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'travelbird.views.home', name='home'),
    # url(r'^travelbird/', include('travelbird.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    ('account_lead(.*)$', account_lead),
    ('mailing_list(.*)$', mailing_list),
)
