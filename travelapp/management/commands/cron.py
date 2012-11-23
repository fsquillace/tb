#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Nov 21, 2012

@author: Filippo Squillace
'''

# From travelapp
from travelapp.utils import api
from travelapp.models import Account, MailingList


# From django
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'It checks for update into the master DB and update the slave DB properly'

    def handle(self, *args, **options):
        # Make a GET request to get all the accounts
        data_get = {'api_key':settings.API_KEY, 'username':settings.USERNAME}

        # Update the accounts according to res
        res = api(settings.API_ENDPOINT+'/v1/mailing_list/', data_get)
        if res.status_code != 200:
            raise Exception("Couldn't connect to the DB."+\
                    " Status code: {0} Reason: {1}".format(res.status_code,
                        res.reason))

        for mailing in res.json['objects']:
            ml, created =\
            MailingList.objects.get_or_create(resource_uri=mailing['resource_uri'])
            # Either if ml is created or already exists update the other fields
            ml.name = mailing['name']
            ml.resource_uri = mailing['resource_uri']
            ml.save()


        # Update the accounts according to res
        res = api(settings.API_ENDPOINT+'/v1/account_lead/', data_get)
        if res.status_code != 200:
            raise Exception("Couldn't connect to the DB."+\
                    " Status code: {0} Reason: {1}".format(res.status_code,
                        res.reason))


        for account in res.json['objects']:
            acc, created = Account.objects.get_or_create(resource_uri=account['resource_uri'])
            # Either if acc is created or already exists update the other fields
            acc.first_name = account['first_name']
            acc.last_name = account['last_name']
            acc.birth_date = account['birth_date']
            acc.gender = account['gender']
            acc.city = account['city']
            acc.country = account['country']
            acc.street_number = account['street_number']
            acc.zipcode = account['zipcode']
            acc.email = account['email']
            acc.phone = account['phone']
            acc.lead = account['lead']
            mailing_lists = []
            for ml in account['mailing_lists']:
                m, created = MailingList.objects.get_or_create(resource_uri=ml['resource_uri'])
                m.name = ml['name']
                m.save()
                mailing_lists.append(m)
            acc.mailing_lists = mailing_lists
            acc.save()


