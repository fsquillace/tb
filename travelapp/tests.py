"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

"""

from django.test import TestCase

from travelapp.models import Account

class AccountJSONTestCase(TestCase):
    def setUp(self):
        self.acc = Account.objects.create(
                first_name='Barack',
                last_name='Obama',
                birth_date='1985-01-01',
                gender='m',
                email='booooo2@gmail.com'
                )
        # get the resource_uri from the server

    def tearDown(self):
        self.acc.delete()
        
    
    def test_pos_get(self):
        """
        Tests that the GET request return the right response.
        """
        res = self.client.get('/account_lead')
        self.assertEqual(simplejson.loads(res.content)[0]['fields']['first_name'], 'Barack')

        # Checks if it works with the resource_uri specified
        res = self.client.get('/account_lead'+self.acc.resource_uri)
        self.assertEqual(simplejson.loads(res.content)[0]['fields']['first_name'], 'Barack')
        
        
    def test_neg_get(self):
        """
        Tests whether the response gives the right error when the field is not correct.
        """
        res = self.client.get('/account_lead'+'/bad_resource_uri :)')
        self.assertEqual(simplejson.loads(res.content)['err_code'], 1)
        
        
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
        Account.objects.get(email='asdf@gmail.com').delete()
        
        
    def test_neg_post(self):
        """
        Test whether a POST request with bad parameter gives the right response and
        the DB is not updated.
        """
        pass
