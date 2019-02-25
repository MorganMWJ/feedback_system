from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

from .forms import LoginForm

import pdb

# Create your views here.
def login(request):
    #pdb.set_trace()
    #if POST request
    if request.method == 'POST':
        #create a form instance populated with the data sent in the form
        form = LoginForm(request.POST)
        #check provided data is valid
        if form.is_valid():
            #process data form.cleaned_data (ldap authenticate)
            #ldapDetails = staff_auth(form.cleaned_data.get('uid'),form.cleaned_data.get('pswd'))
            #ldapDetails = {'uid': 'mwj7', 'name': 'Morgan Jones', 'role': 'Staff', 'access': True}
            username = request.POST['uid']
            password = request.POST['pswd']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                #redirect to session history
                return HttpResponseRedirect(reverse('staff_sessions:index'))
            else:
                # Return an 'invalid login' error message.
                pass
    else:
        form = LoginForm()

    return render(request, 'staff_sessions/login.html', {'form': form})

@login_required
def index(request):
    return render(request, 'staff_sessions/session_history.html')
