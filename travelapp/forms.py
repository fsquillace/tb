'''
Created on Nov 21, 2012

@author: Filippo Squillace
'''


from travelapp.models import Account
from django import forms

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account