
# From django
from django.http import HttpResponse
from django.core import serializers
from django.utils import simplejson

# From travelapp
from travelapp.models import Account, MailingList
from travelapp.forms import AccountForm


# A simple way to identify each type of error is assigning them a code
ERR_CODE = {"ERR_INVALID_PARAM":1, "ERR_INVALID_URI":2}


def account_lead(request, ruri):
    if request.method == "GET":
        if not ruri or ruri == '/':
            res = serializers.serialize('json', Account.objects.all())
        else:
            res = None

            acc = Account.objects.filter(resource_uri=ruri)
            if len(acc) != 0:
                res = serializers.serialize('json', acc)
            else:
                d = {'err_code':ERR_CODE["ERR_INVALID_URI"],\
                        'message':'resource_uri no correct.'}
                res = simplejson.dumps(d)

        return HttpResponse(res)

    elif request.method == "POST":
        if ruri and ruri != '/':
            d = {'err_code':ERR_CODE["ERR_INVALID_URI"],\
                    'message':'Not correct URI for POST request.'}
        else:
            form = AccountForm(request.POST)
            if form.is_valid():
                # Assure that the tenant will be added into the current property
                form.save()
                d = {'message':'OK'}
            else:
                d = {'err_code':ERR_CODE["ERR_INVALID_PARAM"],\
                        'message':'Some fields are not valid.'}
                d.update(form.errors)

        res = simplejson.dumps(d)
        return HttpResponse(res)


def mailing_list(request, ruri):
    if request.method == 'GET':
        if not ruri or ruri == '/':
            res = serializers.serialize('json', MailingList.objects.all())
        else:
            res = None

            acc = MailingList.objects.filter(resource_uri=ruri)
            if len(acc) != 0:
                res = serializers.serialize('json', acc)
            else:
                d = {'err_code':ERR_CODE["ERR_INVALID_URI"],\
                        'message':'resource_uri no correct.'}
                res = simplejson.dumps(d)

        return HttpResponse(res)

