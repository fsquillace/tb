# -*- coding: utf-8 -*-

# From python


# From django
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


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




    def save(self, *args, **kwargs):
        """
        """

        data_get = {'api_key':settings.API_KEY, 'username':settings.USERNAME}

        # Checks first if the account still exists in master DB through
        # the email. We cannot check through the resource_uri because the
        # instance doesn't have it yet.
        res = api(settings.API_ENDPOINT+'/v1/account_lead/', data_get)
        if res.status_code != 200:
            raise Exception("Couldn't connect to the database."+\
                    " Status code: {0}, Reason: {1}.".format(res.status_code, res.reason))
        for a in res.json['objects']:
            #email = a.get('email', None)
            #if email is not None and email == self.email:
                ## The account already exists
                #raise Exception("Error: An account with the same email"+\
                        #" already exist into the master DB.")
            if a.get('resource_uri') == self.resource_uri:
                # Update the local account
                return super(Account, self).save(*args, **kwargs)

        # Make a POST request to update remote DB by API
        data_post = {}
        data_post['first_name'] = self.first_name
        data_post['last_name'] = self.last_name
        data_post['gender'] = self.gender
        data_post['birth_date'] = str(self.birth_date)
        data_post['street_number'] = self.street_number
        data_post['zipcode'] = self.zipcode
        data_post['city'] = self.city
        data_post['country'] = self.country
        data_post['phone'] = self.phone
        data_post['email'] = self.email
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

        # Take the resource_uri too
        self.resource_uri = res.headers.get('location',\
                '').replace(settings.API_ENDPOINT, '')
        if not self.resource_uri:
            raise Exception("No resource uri available in the header response")

        return super(Account, self).save(*args, **kwargs)


    def __unicode__(self):
        return "{0} {1} - {2}".format(self.first_name, self.last_name,
                self.resource_uri)


    class Meta:
        ordering = ['last_name']

@receiver(pre_delete, sender=Account)
def _account_delete(sender, instance, **kwargs):
    data_get = {'api_key':settings.API_KEY, 'username':settings.USERNAME}

    # Make a DELETE request to update remote DB by API
    res = api(settings.API_ENDPOINT+instance.resource_uri,
            data_get, method="DELETE")

    if res.status_code != 204:
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
