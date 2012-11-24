
# From django
from django.http import HttpResponse
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth import authenticate, login
from django.views.defaults import permission_denied

# From travelapp
from travelapp.models import Account, MailingList
from travelapp.forms import AccountForm


# A simple way to identify each type of error is assigning them a code
ERR_CODE = {"ERR_INVALID_PARAM":1, "ERR_INVALID_URI":2}


def auth(request):
    """
    Authenticates the user with username and password passed by GET request.
    If it is already authenticated by the cookie it doesn't need the
    credentials.
    """
    username = request.GET.get('username')
    if not username and request.user.is_authenticated():
        return request.user
    elif request.user.username == username and request.user.is_authenticated():
            return request.user
    else:
        password = request.GET.get('password')
        if username and password:
            user = authenticate(username=username, password=password) #, request=request)
            if user is not None:
                if user.is_active:
                    # Save it into the django session for future accesses
                    login(request, user)
            return user
        else:
            return None



def account_lead(request, ruri):
    if not auth(request):
        return permission_denied(request)


    if request.method == "GET":
        if not request.user.has_perm('travelapp.view_account'):
            return permission_denied(request)

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
        if not request.user.has_perm('travelapp.add_account'):
            return permission_denied(request)

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
    if not auth(request):
        return permission_denied(request)
    if not request.user.has_perm('travelapp.view_mailing_list'):
        return permission_denied(request)


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

