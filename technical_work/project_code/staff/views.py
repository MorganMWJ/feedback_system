from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.template import RequestContext
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ldap3 import core
from PyPDF2.utils import PdfReadError
from itertools import chain

from staff.forms import LoginForm, LectureDetailsForm, PDFUploadForm, ConnectForm, FeedbackForm, QuestionForm
from staff.models import Lecture, Session, Time, Question, Feedback
from staff.helpers import get_info
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
                return HttpResponseRedirect(reverse('staff:lecture_list'))
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

class LectureList(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Lecture
    paginate_by = 8
    template_name = 'staff/lecture_list.html'

    def get_queryset(self):
        lectures = Lecture.objects.filter(user__username=self.request.user.username).order_by('-date_created')
        query = self.request.GET.get("q")
        if query:
            lectures = lectures.filter(
                    Q(title__icontains=query) |
                    Q(date_created__icontains=query))
        return lectures


class LectureDetail(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Lecture
    template_name = 'staff/lecture_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessions_list = self.get_object().session_set.all().order_by('time__start')
        paginator = Paginator(sessions_list, 5)
        page = self.request.GET.get('page', paginator.num_pages)
        try:
            context['sessions'] = paginator.page(page)
        except PageNotAnInteger:
            context['sessions'] = paginator.page(paginator.num_pages)
        except EmptyPage:
            context['sessions'] = paginator.page(paginator.num_pages)
        context['session'] = sessions_list.last()
        return context

class LectureDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    model = Lecture
    success_url =  '/lectures/'

@login_required(login_url='/login/')
def lecture_create(request):
    context = {}
    if request.method == 'POST':
        #create a form instance populated with the data sent in the form
        form = LectureDetailsForm(request.POST)
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
            return HttpResponseRedirect(reverse('staff:lecture_list'))
        #check pdf is valid
        elif pdf_form.is_valid():
            try:
                info = get_info(request.FILES['lecture_pdf_file'])
                context['form'] = LectureDetailsForm(initial={'title': info['title'], 'slide_count': info['pageCount']})
            except PdfReadError:
                messages.error(request, _('File has not been decrypted'))
        else:
            context['invalid_form_error'] = True
    else:
        context['form'] = LectureDetailsForm()
        context['pdf_form'] = PDFUploadForm()

    return render(request, 'staff/lecture_new.html', context)

# class LectureUpdate(LoginRequiredMixin, UpdateView):
#     login_url = '/login/'
#     model = Lecture
#     template_name_suffix = '_edit_form'
#     form_class = LectureDetailsForm
#
#     def get_initial(self):
#         return {'title': self.object.title,
#                 'slide_count': self.object.slide_count,
#                 'notes': self.object.notes}
#
#     def get_context_data(self, **kwargs):
#         pdb.set_trace()
#         context = super().get_context_data(**kwargs)
#         return context
#
#     def get_success_url(self):
#         return reverse('staff:lecture_detail', kwargs={'pk': self.kwargs.get('pk')})


@login_required(login_url='/login/')
def lecture_update(request, pk=None):
    context = {}
    lecture = get_object_or_404(Lecture, id=pk)
    context['lecture'] = lecture
    if request.method == 'POST':
        #create a form instance populated with the data sent in the form
        form = LectureDetailsForm(request.POST)
        context['form'] = form
        pdf_form = PDFUploadForm(request.POST, request.FILES)
        context['pdf_form'] = pdf_form
        #check new lecture data is valid
        if form.is_valid():
            lecture.title = form.cleaned_data.get('title')
            lecture.slide_count = form.cleaned_data.get('slide_count')
            lecture.notes = form.cleaned_data.get('notes')
            lecture.save()

            #redirect to view lecture index
            return redirect(reverse('staff:lecture_detail', kwargs={'pk': lecture.id}))
        #check pdf is valid
        elif pdf_form.is_valid():
            try:
                info = get_info(request.FILES['lecture_pdf_file'])
                context['form'] = LectureDetailsForm(initial={'title': info['title'], 'slide_count': info['pageCount']})
            except PdfReadError:
                messages.error(request, _('File has not been decrypted'))
        else:
            context['invalid_form_error'] = True
    else:
        context['form'] = LectureDetailsForm(initial={'title': lecture.title, 'slide_count': lecture.slide_count, 'notes': lecture.notes})
        context['pdf_form'] = PDFUploadForm()

    return render(request, 'staff/lecture_edit.html', context)

def session_feedback_chart_data(request, id=None):
    session = get_object_or_404(Session, id=id)
    return JsonResponse(session.get_feedback_summary())

@login_required(login_url='/login/')
def session_new(request, id=None):
    lecture = get_object_or_404(Lecture, id=id)
    #create a new feedback session and set it to be running (start time now)
    session = Session.objects.create(code=Session.generate_code(), lecture=lecture)
    Time.objects.create(start=timezone.now(), session=session)
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': id}))

@login_required(login_url='/login/')
def session_delete(request, id=None):
    session = get_object_or_404(Session, id=id)
    if session.is_owned_by_user(request.user):
        session.delete()
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@login_required(login_url='/login/')#Issues with this may need to remove?
def session_merge_previous(request, id=None):
    session = get_object_or_404(Session, id=id)
    if session.is_owned_by_user(request.user):
        session.merge('previous')
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@login_required(login_url='/login/')#Issues with this may need to remove?
def session_merge_next(request, id=None):
    session = get_object_or_404(Session, id=id)
    if session.is_owned_by_user(request.user):
        session.merge('next')
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@login_required(login_url='/login/')
def session_stop(request, id=None):
    session = get_object_or_404(Session, id=id)
    if session.is_running:
        #set session as no longer running and update end_time
        session.is_running = False
        session.end()
        session.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@login_required(login_url='/login/')
def session_regenerate_code(request, id=None):
    instance = get_object_or_404(Session, id=id)
    instance.code = Session.generate_code()
    instance.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': instance.lecture.id}))

@login_required(login_url='/login/')
def session_toggle_questions(request, id=None):
    instance = get_object_or_404(Session, id=id)
    instance.is_taking_questions = not instance.is_taking_questions
    instance.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': instance.lecture.id}))





@login_required(login_url='/login/')
def session_questions(request, id=None):
    pdb.set_trace()
    context = {}
    context['session'] = get_object_or_404(Session, id=id)
    questions_list = context['session'].question_set.filter(is_reviewed=False).order_by("-time_posted")

    paginator = Paginator(questions_list, 6)
    page = request.GET.get('page', paginator.num_pages)
    try:
        context['questions'] = paginator.page(page)
    except PageNotAnInteger:
        context['questions'] = paginator.page(paginator.num_pages)
    except EmptyPage:
        context['questions'] = paginator.page(paginator.num_pages)

    return render(request, 'staff/questions_list.html', context)

@login_required(login_url='/login/')
def lecture_sessions(request, id=None, version=None):
    context = {}
    lecture = get_object_or_404(Lecture, id=id)

    sessions_list = lecture.session_set.all().order_by('time__start')
    paginator = Paginator(sessions_list, 5)
    page = request.GET.get('page', paginator.num_pages)
    try:
        context['sessions'] = paginator.page(page)
    except PageNotAnInteger:
        context['sessions'] = paginator.page(paginator.num_pages)
    except EmptyPage:
        context['sessions'] = paginator.page(paginator.num_pages)
    context['session'] = sessions_list.last()

    if version=='v1':
        return render(request, 'staff/lecture_sessions_list.html', context)
    elif version=='v2':
        return render(request, 'staff/feedback_sessions_list.html', context)
    else:
        return HttpResponseNotFound("404 :(")



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
                    request.session['slides_with_feedback'] = []
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
    if 'slides_with_feedback' in request.session:
        del request.session['slides_with_feedback']
    if 'previous_feedback_form_state' in request.session:
        del request.session['previous_feedback_form_state']
    return HttpResponseRedirect(reverse('staff:connect'))

def feedback(request):
    context = {}
    try:
        session = Session.objects.get(pk=request.session['connected_session_id'])
    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))

    #ensure that session is active
    if session.is_running:
        context['session'] = session
        if 'previous_feedback_form_state' in request.session:
            context['feedback_form'] = FeedbackForm(session.lecture, request.session['previous_feedback_form_state'])
        else:
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

    pdb.set_trace()
    if session.is_running:
        if request.method == 'POST':
            form = FeedbackForm(session.lecture, request.POST)
            if form.is_valid():
                request.session['previous_feedback_form_state'] = request.POST

                slide = form.cleaned_data.get('slide_number')
                overall = form.cleaned_data.get('overall_feedback')
                speed = form.cleaned_data.get('delivery_speed')
                complexity = form.cleaned_data.get('content_complexity')
                presentation = form.cleaned_data.get('content_presentation')
                engagment = form.cleaned_data.get('level_of_engagement')
                if overall==None and speed==None and complexity==None and presentation==None and engagment==None:
                    messages.error(request, _('Please Specify Some Feedback Options'))
                elif 'slides_with_feedback' in request.session and slide in [x[1] for x in request.session['slides_with_feedback']]:
                    index = -1
                    for idx, val in enumerate(request.session['slides_with_feedback']):
                        if(val[1]==int(slide)):
                            index = idx
                    feedback_to_update = get_object_or_404(Feedback, pk=request.session['slides_with_feedback'][index][0])
                    feedback_to_update.overall_feedback = overall
                    feedback_to_update.delivery_speed = speed
                    feedback_to_update.content_complexity = complexity
                    feedback_to_update.content_presentation = presentation
                    feedback_to_update.level_of_engagement = engagment
                    feedback_to_update.save()

                    if int(slide)==0:
                        messages.success(request, _('General Feedback re-submitted'))
                    else:
                        messages.success(request, _('Slide ' + slide + ' feedback  re-submitted'))
                else:
                    new_feedback = Feedback.objects.create(time_posted=timezone.now(),
                                    slide_number=slide,
                                    overall_feedback=overall,
                                    delivery_speed=speed,
                                    content_complexity=complexity,
                                    content_presentation=presentation,
                                    level_of_engagement=engagment,
                                    session=session)
                    if 'slides_with_feedback' in request.session:
                        request.session['slides_with_feedback'].append((new_feedback.id, new_feedback.slide_number))
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

####################################################################################################
def feedback_detail(request, id=None):
    context ={}
    context['lecture'] = get_object_or_404(Lecture, id=id)
    context['sessions'] = context['lecture'].session_set.all().order_by("time__start")
    return render(request, 'staff/feedback_detail.html', context)


def session_feedback(request, id=None):
    session = get_object_or_404(Session, id=id)
    feedback = session.feedback_set.all()
    return JsonResponse({'feedback': feedback})
