# -*- coding: utf-8 -*-

# From python


# From django
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver
from django.core.exceptions import ValidationError


# From travelapp
from travelapp.utils import api

GENDER_CHOICES = (
    (u'm', u'Male'),
    (u'f', u'Female'),
)



class BasicData(models.Model):
    """
    The abstract class is used to define common fields once
    """
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class MailingList(BasicData):
    name = models.CharField(max_length=100)
    resource_uri = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        permissions = (
            ("view_mailing_list", "View the mailing list information"),
        )





class Account(BasicData):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)

    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    street_number = models.CharField(max_length=10, null=True, blank=True)
    zipcode = models.CharField(max_length=5, null=True, blank=True)

    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100, null=True, blank=True)

    lead = models.BooleanField()
    mailing_lists = models.ManyToManyField(MailingList, null=True, blank=True)

    resource_uri = models.CharField(max_length=512, null=True, blank=True,
            editable=False)

    def __unicode__(self):
        return "{0} {1} - {2}".format(self.first_name, self.last_name,
                self.resource_uri)


    class Meta:
        ordering = ['last_name']
        permissions = (
            ("view_account", "View the account information"),
        )


@receiver(pre_save, sender=Account)
def _account_save(sender, instance, **kwargs):

    # Do not do anything if the instance is not valid!
    try:
        instance.full_clean()
    except ValidationError:
        return

    data_get = {'api_key':settings.API_KEY, 'username':settings.USERNAME}

    res = api(settings.API_ENDPOINT+'/v1/account_lead/', data_get)
    if res.status_code != 200:
        raise Exception("Couldn't connect to the database."+\
                " Status code: {0}, Reason: {1}.".format(res.status_code, res.reason))


    # If the resource_uri already exists means that the operation is to update
    # the record. There is no UPDATE request for the API, there fore do not
    # sync with the master DB.
    if instance.resource_uri:
        return

    # Make a POST request to update remote DB by API
    data_post = {}
    data_post['first_name'] = instance.first_name
    data_post['last_name'] = instance.last_name
    data_post['gender'] = instance.gender
    if instance.birth_date:
        data_post['birth_date'] = instance.birth_date.strftime("%Y-%m-%d")
    else:
        data_post['birth_date'] = None
    data_post['street_number'] = instance.street_number
    data_post['zipcode'] = instance.zipcode
    data_post['city'] = instance.city
    data_post['country'] = instance.country
    data_post['phone'] = instance.phone
    data_post['email'] = instance.email
    data_post['tr_referral'] = settings.TR_REFERRAL
    data_post['mailing_lists'] = 1
    data_post['utm_medium'] = 'api'
    data_post['ip_address'] = '192.168.10.10'

    res = api(settings.API_ENDPOINT+'/v1/account_lead/', data_get, data_post, method="POST")


    # Save the object into the current db only if was correctly saved into
    # the master DB
    if res.status_code != 201:
        raise Exception("Couldn't change the master db"+\
                " Status code: {0}, Reason: {1}.".format(res.status_code, res.reason))

    # Takes the resource_uri from the header of the response
    instance.resource_uri = res.headers.get('location',\
            '').replace(settings.API_ENDPOINT, '')
    if not instance.resource_uri:
        raise Exception("No resource uri available in the header response")






@receiver(pre_delete, sender=Account)
def _account_delete(sender, instance, **kwargs):
    data_get = {'api_key':settings.API_KEY, 'username':settings.USERNAME}

    # Make a DELETE request to update remote DB by API
    res = api(settings.API_ENDPOINT+instance.resource_uri,
            data_get, method="DELETE")

    # Two possible right cases when request a deletion:
    # 204 (NO CONTENT): Successfully deleted
    # 404 (NOT FOUND): Resource not found
    # all the other cases raise an Exception.
    if res.status_code != 204 and res.status_code != 404:
        raise Exception("Couldn't delete to the master db."+\
                " Status code:{0}, Reason: {1}".format(res.status_code,
                    res.reason))


# Missing fields are:
#"tr_input_method": "", 
#"tr_ip_address": "192.168.123.80", 
#"tr_language": "en_EN", 
#"tr_referral": {"name": "FilippoFeed", "resource_uri": ""},
#
# "utm_campaign": "", "utm_medium": "", "utm_source": "FilippoFeed", }, 
