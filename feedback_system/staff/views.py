from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from ldap3 import core
from staff.forms import LoginForm, NewLectureForm, PDFUploadForm
from staff.models import Lecture, Session
from staff.pdf_extractor import get_info

import pdb #pdb.set_trace() to start

# Create your views here.
def login(request):
    context = {}
    #if POST request
    if request.method == 'POST':
        #create a form instance populated with the data sent in the form
        form = LoginForm(request.POST)
        context['form'] = form
        #check provided data is valid
        if form.is_valid():
            #process data form.cleaned_data (ldap authenticate)
            username = form.cleaned_data.get('uid')
            password = form.cleaned_data.get('pswd')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect(reverse('staff:index'))
            else:
                # Return an 'invalid login' error message.
                context['login_error'] = True
        else:
            context['invalid_form_error'] = True
    else:
        context['form'] = LoginForm()

    return render(request, 'staff/login.html', context)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('staff:login'))

@login_required(login_url='/staff/login/')
def index(request):
    previous_lectures = Lecture.objects.filter(author_username=request.user.username).order_by('session__start_time')

    #pagination code
    paginator = Paginator(previous_lectures, 10)
    page = request.GET.get('page')
    try:
        previous_lectures = paginator.page(page)
    except PageNotAnInteger:
        previous_lectures = paginator.page(1)
    except EmptyPage:
        previous_lectures = paginator.page(paginator.num_pages)

    context = {'lecture_list': previous_lectures}
    return render(request, 'staff/lecture_list.html', context)

@login_required(login_url='/staff/login/')
def lecture_delete(request, id=None):
    instance = get_object_or_404(Lecture, id=id)
    instance.delete()
    return redirect(reverse('staff:index'))

@login_required(login_url='/staff/login/')
def lecture_new(request):
    #pdb.set_trace()
    context = {}
    if request.method == 'POST':
        #create a form instance populated with the data sent in the form
        form = NewLectureForm(request.POST)
        context['form'] = form
        pdf_form = PDFUploadForm(request.POST, request.FILES)
        context['pdf_form'] = pdf_form
        #check new lecture data is valid
        if form.is_valid():
            #create new lecture from cleaned_data
            title = form.cleaned_data.get('title')
            slide_count = form.cleaned_data.get('slide_count')
            notes = form.cleaned_data.get('notes')

            Lecture.objects.create(title=title,
                                slide_count=slide_count,
                                author_username=request.user.username,
                                author_forename=request.user.first_name,
                                author_surname=request.user.last_name,
                                session_code=Lecture.getCode(),
                                notes=notes)
            #redirect to view lecture index
            return HttpResponseRedirect(reverse('staff:index'))
        #check pdf is valid
        elif pdf_form.is_valid():
            #if so extarct it from there
            info = get_info(request.FILES['lecture_pdf_file'])
            context['form'] = NewLectureForm(initial={'title': info['title'], 'slide_count': info['pageCount']})
        else:
            context['invalid_form_error'] = True
    else:
        context['form'] = NewLectureForm()
        context['pdf_form'] = PDFUploadForm()

    return render(request, 'staff/lecture_new.html', context)
