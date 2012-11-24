"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

"""

# From python
import simplejson

# From django
from django.test import TestCase
from django.db import IntegrityError
from django.conf import settings

# from tb
from travelapp.models import Account, MailingList
from travelapp.utils import api
from travelapp.views import ERR_CODE


class MailingListTestCase(TestCase):
    def setUp(self):
        self.ml = MailingList(
                name='Classical NL')

    def tearDown(self):
        pass

    def test_pos_add(self):
        """
        Checks when saving the record it appears stored in local DB
        """
        self.ml.save()
        self.assertEqual(self.ml, MailingList.objects.get(name='Classical NL'))
        self.ml.delete()

    def test_neg_add(self):
        """
        Raise error in case of the model is not valid 
        """
        # name to None
        self.ml.name = None
        self.assertRaises(IntegrityError, self.ml.save)
        self.ml.name = 'Classical NL'

    def test_pos_del(self):
        """
        Checks when deleting a record it disappears in local and DB
        """
        self.ml.save()
        self.ml.delete()

        self.assertRaises(MailingList.DoesNotExist, MailingList.objects.get,
                name='Classical NL')





class AccountTestCase(TestCase):
    def setUp(self):
        self.acc = Account(
                first_name='Barack',
                last_name='Obama',
                birth_date='1985-01-01',
                gender='m',
                email='bo0099o0o2@gmail.com'
                )

    def tearDown(self):
        pass

    def test_pos_add(self):
        """
        Checks when saving the record it appears stored in both local and remote DB
        """
        self.acc.save()
        self.assertEqual(self.acc, Account.objects.get(first_name='Barack'))
        res = api(settings.API_ENDPOINT+self.acc.resource_uri, {'username':settings.USERNAME,
            'api_key':settings.API_KEY})
        self.assertEqual(res.json['first_name'], 'Barack')
        self.acc.delete()

    def test_neg_add(self):
        """
        Raise error in case of the model is not valid 
        """
        # first_name to None
        self.acc.first_name = None
        self.assertRaises(IntegrityError, self.acc.save)
        self.acc.first_name = 'Barack'

        # last_name to None
        self.acc.last_name = None
        self.assertRaises(IntegrityError, self.acc.save)
        self.acc.last_name = 'Obama'

        # birth_date to None
        self.acc.birth_date = None
        self.assertRaises(IntegrityError, self.acc.save)
        self.acc.birth_date = '1985-01-01'

        # gender to None
        self.acc.gender = None
        self.assertRaises(IntegrityError, self.acc.save)
        self.acc.gender = 'm'
        
        # email to None
        self.acc.email = None
        self.assertRaises(IntegrityError, self.acc.save)

    def test_pos_del(self):
        """
        Checks when deleting a record it disappears in both local and remote DB
        """
        self.acc.save()
        self.acc.delete()

        self.assertRaises(Account.DoesNotExist, Account.objects.get, first_name='Barack')
        res = api(settings.API_ENDPOINT+self.acc.resource_uri, {'username':settings.USERNAME,
            'api_key':settings.API_KEY})
        # Checks the NOT FOUND status code
        self.assertEqual(res.status_code, 404)



class APIAccountTestCase(TestCase):
    def setUp(self):
        self.acc = Account.objects.create(
                first_name='Barack',
                last_name='Obama',
                birth_date='1985-01-01',
                gender='m',
                email='boo0000ooo2@gmail.com'
                )

    def tearDown(self):
        self.acc.delete()
        
    
    def test_pos_get(self):
        """
        Tests that the GET request return the right response.
        """
        res = self.client.get('/account_lead/')
        self.assertEqual(simplejson.loads(res.content)[0]['fields']['first_name'],
                self.acc.first_name)

        # Checks if it works with the resource_uri specified
        res = self.client.get('/account_lead'+self.acc.resource_uri)
        self.assertEqual(simplejson.loads(res.content)[0]['fields']['first_name'],
                self.acc.first_name)
        
        
    def test_neg_get(self):
        """
        Tests whether the response gives the right error when the field is not correct.
        """
        res = self.client.get('/account_lead'+'/bad_resource_uri :)')
        self.assertEqual(simplejson.loads(res.content)['err_code'],
                ERR_CODE["ERR_INVALID_URI"])
        
        
    def test_pos_post(self):
        """
        Tests whether a POST request returns the right response and
        the DB is updated properly.
        """
        data = {'first_name':'Johnny','last_name':'Depp',
                'birth_date':'1985-01-06', 'gender':'m',
                'email':'asdf@gmail.com'}
        res = self.client.post('/account_lead', data)
        self.assertEqual(simplejson.loads(res.content)['message'], 'OK')
        self.assertEqual(Account.objects.get(first_name='Johnny').first_name,
                'Johnny')
        Account.objects.get(email='asdf@gmail.com').delete()
        
        
    def test_neg_post(self):
        """
        Test whether a POST request with bad parameter gives the right response and
        the DB is not updated.
        """
        data = {'first_name':'','last_name':'Depp',
                'birth_date':'1985-01-06', 'gender':'m',
                'email':'asdf@gmail.com'}
        res = self.client.post('/account_lead', data)
        self.assertEqual(simplejson.loads(res.content)['err_code'],
                ERR_CODE["ERR_INVALID_PARAM"])
        self.assertRaises(Account.DoesNotExist,
                Account.objects.get, email='asdf@gmail.com')

        res = self.client.post('/account_lead/bad_resource', data)
        self.assertEqual(simplejson.loads(res.content)['err_code'],
                ERR_CODE["ERR_INVALID_URI"])
        self.assertRaises(Account.DoesNotExist,
                Account.objects.get, email='asdf@gmail.com')
        
        

class APIMailingListTestCase(TestCase):
    def setUp(self):
        self.ml = MailingList.objects.create(
                name='Rock Linux',
                resource_uri='/v1/mailing_list/22222/')

    def tearDown(self):
        self.ml.delete()
        
    
    def test_pos_get(self):
        """
        Tests that the GET request return the right response.
        """
        res = self.client.get('/mailing_list/')
        self.assertEqual(simplejson.loads(res.content)[0]['fields']['name'],
                self.ml.name)

        # Checks if it works with the resource_uri specified
        res = self.client.get('/mailing_list'+self.ml.resource_uri)
        self.assertEqual(simplejson.loads(res.content)[0]['fields']['name'],
                self.ml.name)
        
        
    def test_neg_get(self):
        """
        Tests whether the response gives the right error when the uri is not correct.
        """
        res = self.client.get('/mailing_list'+'/bad_resource_uri :)')
        self.assertEqual(simplejson.loads(res.content)['err_code'],
                ERR_CODE["ERR_INVALID_URI"])
        

