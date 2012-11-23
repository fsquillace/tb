#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Nov 21, 2012

@author: Filippo Squillace
'''

# From travelapp
from travelapp.utils import api
from travelapp.models import Account


# From django
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'It checks for update into the master DB and update the slave DB properly'

    def handle(self, *args, **options):
        # Make a GET request to get all the accounts
        data_get = {'api_key':settings.API_KEY, 'username':settings.USERNAME}

        # Update the accounts according to res
        res = api(settings.API_ENDPOINT+'/v1/account_lead/', data_get)
        for account in res.json['objects']:
            ml, created = Account.objects.get_or_create(resource_uri=account['resource_uri'])
            # Either if ml is created or already exists update the other fields
            ml.first_name = account['first_name']
            ml.last_name = account['last_name']
            ml.birth_date = account['birth_date']
            ml.gender = account['gender']
            ml.city = account['city']
            ml.country = account['country']
            ml.street_number = account['street_number']
            ml.zipcode = account['zipcode']
            ml.email = account['email']
            ml.phone = account['phone']
            ml.lead = account['lead']
            #ml.mailing_lists = account['first_name']
            ml.save()

