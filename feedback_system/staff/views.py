from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.template import RequestContext
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ldap3 import core
from PyPDF2.utils import PdfReadError
from itertools import chain
from staff.forms import LoginForm, NewLectureForm, PDFUploadForm, ConnectForm, FeedbackForm, QuestionForm
from staff.models import Lecture, Session, Question, Feedback
from staff.pdf_extractor import get_info
from staff.templatetags.format_extras import runtime_format, question_time_format

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

@login_required(login_url='/login/')
def index(request):
    # pdb.set_trace()
    previous_lectures = Lecture.objects.filter(user__username=request.user.username).order_by('-date_created')

    #if we have a search query filter previous_lectures that match the query
    query = request.GET.get("q")
    if query:
        previous_lectures = previous_lectures.filter(
                Q(title__icontains=query) |
                Q(date_created__icontains=query))

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

@login_required(login_url='/login/')
def lecture_detail(request, id=None):
    #pdb.set_trace()
    instance = get_object_or_404(Lecture, id=id)
    sessions = instance.session_set.all().order_by("start_time")
    last_session_questions = []
    feedbackSummary = []

    if sessions:
        #get last sessions questions
        last_session_questions = list(instance.get_last_session().question_set.filter(is_reviewed=False).order_by("-time_posted"))
        #put in feedback totals for each category - TODO


    if request.is_ajax() and request.method == 'GET':
        resp_data = {
            'total_runtime': runtime_format(instance.get_total_runtime()),
            # more data
        }
        return JsonResponse(resp_data, status=200)

    return render(request, 'staff/lecture_detail.html', {'lecture': instance, 'sessions': sessions, 'questions': last_session_questions})

@login_required(login_url='/login/')
def session_new(self, id=None):
    pdb.set_trace()
    instance = get_object_or_404(Lecture, id=id)
    #create a new feedback session and set it to be running
    Session.objects.create(start_time=timezone.now(),code=Session.generate_code(), lecture=instance)
    instance.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'id': id}))

@login_required(login_url='/login/')
def session_stop(self, id=None):
    instance = get_object_or_404(Session, id=id)
    if instance.is_running:
        #set session as no longer running and update end_time
        instance.end_time = timezone.now()
        instance.is_running = False
        instance.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'id': instance.lecture.id}))

@login_required(login_url='/login/')
def session_regenerate_code(request, id=None):
    instance = get_object_or_404(Session, id=id)
    instance.code = Session.generate_code()
    instance.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'id': instance.lecture.id}))

@login_required(login_url='/login/')
def session_toggle_questions(request, id=None):
    instance = get_object_or_404(Session, id=id)
    instance.is_taking_questions = not instance.is_taking_questions
    instance.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'id': instance.lecture.id}))

@login_required(login_url='/login/')
def lecture_delete(request, id=None):
    instance = get_object_or_404(Lecture, id=id)
    instance.delete()
    return redirect(reverse('staff:index'))

@login_required(login_url='/login/')
def lecture_new(request):
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
                                notes=notes,
                                date_created=timezone.now(),
                                user=request.user)
            #redirect to view lecture index
            return HttpResponseRedirect(reverse('staff:index'))
        #check pdf is valid
        elif pdf_form.is_valid():
            try:
                info = get_info(request.FILES['lecture_pdf_file'])
                context['form'] = NewLectureForm(initial={'title': info['title'], 'slide_count': info['pageCount']})
            except PdfReadError:
                messages.error(request, _('File has not been decrypted'))
        else:
            context['invalid_form_error'] = True
    else:
        context['form'] = NewLectureForm()
        context['pdf_form'] = PDFUploadForm()

    return render(request, 'staff/lecture_new.html', context)

@login_required(login_url='/login/')
def question_mark_reviewed(request, id=None):
    instance = get_object_or_404(Question, id=id)
    instance.is_reviewed = True
    instance.save()
    lecture = instance.session.lecture
    return redirect(reverse('staff:lecture_detail', kwargs={'id': lecture.id}))

def connect(request):
    context = {}
    if request.method == 'POST':
        form = ConnectForm(request.POST)
        context['form'] = form
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                session = Session.objects.get(code=code.upper())
                #ensure that session is running
                if session.is_running:
                    request.session['connected_session_id'] = session.id
                    request.session.set_expiry(0) #exipre upon web browser close
                    return HttpResponseRedirect(reverse('staff:feedback'))
                else:
                    messages.error(request, _('Lecture is not active'))
            except Session.DoesNotExist:
                messages.error(request, _('Invalid lecture feedback code'))
        else:
            messages.error(request, _('Invalid POST Data'))
    else:
        form = ConnectForm()
        context['form'] = form

    return render(request, 'staff/connect.html', context)

def disconnect(request):
    if 'connected_session_id' in request.session:
        del request.session['connected_session_id']
    if 'questions_asked' in request.session:
        del request.session['questions_asked']
    return HttpResponseRedirect(reverse('staff:connect'))

def feedback(request):
    context = {}
    try:
        session = Session.objects.get(pk=request.session['connected_session_id'])
    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))

    #ensure that lecture is active (running a session)
    if session.is_running:
        context['session'] = session
        context['feedback_form'] = FeedbackForm(session.lecture)
        context['question_form'] = QuestionForm()
        if 'questions_asked' in request.session:
            context['questions'] = Question.objects.filter(pk__in=request.session['questions_asked']).order_by("-time_posted")
    else:
        messages.error(request, _('Session is not active'))
        return HttpResponseRedirect(reverse('staff:disconnect'))

    return render(request, 'staff/feedback.html', context)

def feedback_new(request):
    context = {}
    try:
        session = Session.objects.get(pk=request.session['connected_session_id'])
    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))

    if session.is_running:
        if request.method == 'POST':
            form = FeedbackForm(session.lecture, request.POST)
            if form.is_valid():
                overall = form.cleaned_data.get('overall_option')
                speed = form.cleaned_data.get('speed_options')
                complexity = form.cleaned_data.get('complexity_options')
                presentation = form.cleaned_data.get('presentation_options')
                engagment = form.cleaned_data.get('engagment_options')
                slide = form.cleaned_data.get('slide_options')
                Feedback.objects.create(time_posted=timezone.now(),
                                slide_number=slide,
                                overall_feedback=overall,
                                delivery_speed=speed,
                                content_complexity=complexity,
                                content_presentation=presentation,
                                level_of_engagement=engagment,
                                session=session)
            else:
                messages.error(request, _('Invalid POST Data'))
    else:
        messages.error(request, _('Please connect to active session with valid feedback code'))

    return HttpResponseRedirect(reverse('staff:feedback'))

def question_new(request):
    try:
        session = Session.objects.get(pk=request.session['connected_session_id'])
    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))

    if session.is_running and session.is_taking_questions:
        if request.method == 'POST':
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.cleaned_data.get('question')
                newQuestion = Question.objects.create(question_text=question, time_posted=timezone.now(), session=session)
                if 'questions_asked' in request.session:
                    request.session['questions_asked'].append(newQuestion.id)
                else:
                    request.session['questions_asked'] = [newQuestion.id]
            else:
                messages.error(request, _('Invalid POST Data'))
    elif not session.is_running:
        messages.error(request, _('Please connect to active session with valid feedback code'))
    else:
        messages.error(request, _('Session not currently taking questions'))
    return redirect(reverse('staff:feedback'))

#currently assumes staff cannot delete questions only those who post them during their sesssion
def question_delete(request, id=None):
    try:
        session = Session.objects.get(pk=request.session['connected_session_id'])
    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))

    if 'questions_asked' in request.session:
        if id in request.session['questions_asked']:
            questionToDelete = get_object_or_404(Question, id=id)
            questionToDelete.delete()
        else:
            messages.error(request, _('You can only delete questions you have posted'))
    else:
        messages.error(request, _('You can only delete questions you have posted'))
    return redirect(reverse('staff:feedback'))
