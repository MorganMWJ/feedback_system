from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound,HttpResponseBadRequest, FileResponse, HttpResponse, Http404
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.template import RequestContext
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ldap3 import core
from PyPDF2.utils import PdfReadError
from itertools import chain
import datetime

from staff.forms import LoginForm, LectureDetailsForm, ConnectForm, FeedbackForm, QuestionForm
from staff.models import Lecture, Session, Time, Question, Feedback
from staff.helpers import get_pdf_pages
from staff.decorators import must_own_lecture, must_own_session, must_own_question
from staff.templatetags.format_extras import runtime_format, question_time_format

import pdb #pdb.set_trace() to start

def get_session_list(request, lecture, per_page):
    """
    Helper method to reduce duplictate Code
    Paginates sessions ready to send to the templates
    """
    context = {'per_page': per_page}
    sessions_queryset = lecture.session_set.all()
    #hack to remove pesky duplicates
    sessions_list = list(dict.fromkeys(list(sessions_queryset)))
    paginator = Paginator(sessions_list, context['per_page'])
    page = request.GET.get('page', paginator.num_pages)
    try:
        context['sessions'] = paginator.page(page)
    except PageNotAnInteger:
        context['sessions'] = paginator.page(paginator.num_pages)
    except EmptyPage:
        context['sessions'] = paginator.page(paginator.num_pages)
    if sessions_list!=[]:
        context['session'] = sessions_list[-1]
    return context

def login(request):
    #pdb.set_trace()
    context = {}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        context['form'] = form
        if form.is_valid():
            username = form.cleaned_data.get('uid')
            password = form.cleaned_data.get('pswd')
            # LDAP Authenticate
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if 'next' in request.POST and request.POST.get('next')!='':
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect(reverse('staff:lecture_list'))
        else:
            messages.error(request, _('Invalid form data'))
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
        lectures = Lecture.objects.filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            for q in query.split('/'):
                lectures = lectures.filter(
                        Q(title__icontains=q) |
                        Q(date_created__icontains=q))
            messages.success(self.request, "Search Result For: " + query)
        return lectures

@method_decorator(must_own_lecture, name='dispatch')
class LectureDetail(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Lecture
    template_name = 'staff/lecture_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_session_list(self.request, self.get_object(), 5))
        return context

@method_decorator(must_own_lecture, name='dispatch')
class LectureDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    model = Lecture
    success_url =  '/lectures/'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Lecture Deleted: "+self.get_object().title)
        return super().delete(request, *args, **kwargs)

class LectureCreate(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    model = Lecture
    success_url =  '/lectures/'
    form_class = LectureDetailsForm
    template_name_suffix = '_new'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.file = self.request.FILES.get('file')
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, "Lecture Created: " + self.object.title)
        return HttpResponseRedirect(reverse('staff:lecture_list'))

    def form_invalid(self, form):
        messages.error(self.request, _('Invalid form data'))
        return super().form_invalid(form)

@method_decorator(must_own_lecture, name='dispatch')
class LectureUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    model = Lecture
    form_class = LectureDetailsForm
    template_name_suffix = '_edit'

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.file = self.request.FILES.get('file')
        self.object.save()
        messages.success(self.request, "Lecture Updated")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _('Invalid form data'))
        return super().form_invalid(form)

@must_own_lecture
@login_required(login_url='/login/')
def extarct_from_pdf(request, pk=None):
    """
    Extarcts the number of slides of a lecture from a PDF of the lecture slides
    Useful incase users are unsure of the number of slides in the presentation they are giving
    """
    lecture = get_object_or_404(Lecture, id=pk)
    if lecture.file:
        lecture.slide_count = get_pdf_pages(lecture.file)
        lecture.save()
        messages.success(request, _("Number of slides got from PDF"))
    else:
        messages.error(request, _("There is no PDF associated with this lecture"))
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': lecture.id}))

def lecture_file_view(request, pk=None):
    lecture = get_object_or_404(Lecture, id=pk)
    try:
        filename = lecture.file.path
        if request.user.is_authenticated and lecture.user==request.user:
            return FileResponse(open(filename, 'rb'), content_type='application/pdf')
        elif lecture==Session.objects.get(pk=request.session['connected_session_id']).lecture:
            return FileResponse(open(filename, 'rb'), content_type='application/pdf')
        else:
            return HttpResponse('Unauthorized', status=401)

    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))
    except ValueError:
        raise Http404
    except FileNotFoundError:
        raise Http404

@must_own_lecture
@login_required(login_url='/login/')
def session_new(request, pk=None):
    lecture = get_object_or_404(Lecture, id=pk)
    lecture.session_set.create(code=Session.generate_code())
    messages.success(request, _('Created New Session'))
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': pk}))

@must_own_session
@login_required(login_url='/login/')
def session_start(request, pk=None):
    pdb.set_trace()
    session = get_object_or_404(Session, id=pk)
    if session.is_running:
        messages.error(request, _('Session') + ' ' + str(session) + ': ' + _('Already running'))
    else:
        session.is_running = True
        session.save()
        Time.objects.create(start=timezone.now(), session=session)
        messages.success(request, _('Session') + ' ' + str(session) + ': ' + _('Started'))
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_stop(request, pk=None):
    session = get_object_or_404(Session, id=pk)
    if session.is_running:
        session.is_running = False #set session as no longer running
        session.end() #update end_time
        session.save()
    messages.success(request, _('Session') + ' ' + str(session) + ': ' + _('Ended'))
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_delete(request, pk=None):
    session = get_object_or_404(Session, id=pk)
    session.delete()
    messages.success(request, _('Session') + ' ' + str(session) + ': ' + _('Deleted'))
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_merge_previous(request, pk=None):
    session = get_object_or_404(Session, id=pk)
    session.merge('previous')
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_merge_next(request, pk=None):
    session = get_object_or_404(Session, id=pk)
    session.merge('next')
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_regenerate_code(request, pk=None):
    session = get_object_or_404(Session, id=pk)
    session.code = Session.generate_code()
    session.save()
    messages.success(request, _('Session') + ' ' + str(session) + ': ' + _('New Code Generated'))
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_toggle_questions(request, pk=None):
    session = get_object_or_404(Session, id=pk)
    session.is_taking_questions = not session.is_taking_questions
    session.save()
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': session.lecture.id}))

@must_own_session
@login_required(login_url='/login/')
def session_questions(request, pk=None):
    context = {}
    context['session'] = get_object_or_404(Session, id=pk)
    context['questions'] = context['session'].question_set.filter(is_reviewed=False).order_by("time_posted")
    return render(request, 'staff/questions_list.html', context)

@must_own_lecture
@login_required(login_url='/login/')
def lecture_sessions(request, pk=None, version=None):
    context = {}
    lecture = get_object_or_404(Lecture, id=pk)
    if version=='v1':
        context.update(get_session_list(request, lecture, 5))
        return render(request, 'staff/lecture_sessions_list.html', context)
    elif version=='v2':
        context.update(get_session_list(request, lecture, 10))
        return render(request, 'staff/feedback_sessions_list.html', context)
    else:
        return HttpResponseNotFound("404 :(")

@must_own_question
@login_required(login_url='/login/')
def question_mark_reviewed(request, pk=None):
    question = get_object_or_404(Question, id=pk)
    question.is_reviewed = True
    question.save()
    lecture = question.session.lecture
    return redirect(reverse('staff:lecture_detail', kwargs={'pk': lecture.id}))

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

    context['lecture'] = session.lecture
    return render(request, 'staff/feedback.html', context)

def feedback_create(request):
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
                request.session['previous_feedback_form_state'] = request.POST

                slide = form.cleaned_data.get('slide_number')
                overall = form.cleaned_data.get('overall_feedback')
                speed = form.cleaned_data.get('delivery_speed')
                complexity = form.cleaned_data.get('content_complexity')
                presentation = form.cleaned_data.get('content_presentation')
                engagment = form.cleaned_data.get('level_of_engagement')
                if overall==None and speed==None and complexity==None and presentation==None and engagment==None:
                    messages.warning(request, _('Please Specify Some Feedback Options'))
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
                    if int(slide)==0:
                        messages.success(request, _('General Feedback submitted'))
                    else:
                        messages.success(request, _('Slide ' + slide + ' feedback submitted'))
            else:
                messages.error(request, _('Invalid POST Data'))
    else:
        messages.error(request, _('Please connect to active session with valid feedback code'))

    return HttpResponseRedirect(reverse('staff:feedback'))

def question_create(request):
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
def question_delete(request, pk=None):
    try:
        session = Session.objects.get(pk=request.session['connected_session_id'])
    except (KeyError, Session.DoesNotExist):
        messages.error(request, _('Please connect to active session with valid feedback code'))
        return redirect(reverse('staff:connect'))

    if 'questions_asked' in request.session:
        if id in request.session['questions_asked']:
            questionToDelete = get_object_or_404(Question, id=pk)
            questionToDelete.delete()
        else:
            messages.error(request, _('You can only delete questions you have posted'))
    else:
        messages.error(request, _('You can only delete questions you have posted'))
    return redirect(reverse('staff:feedback'))

####################################################################################################
@must_own_lecture
def feedback_detail(request, pk=None):
    context = {}
    context['lecture'] = get_object_or_404(Lecture, id=pk)
    context.update(get_session_list(request, context['lecture'], 10))
    return render(request, 'staff/feedback_detail.html', context)


def session_feedback_chart_data(request):
    if 'session' in request.GET and 'feedback_request' in request.GET:
        print("session: " + request.GET.get('session'))#DEBUG
        print("feedback_request: " + request.GET.get('feedback_request'))#DEBUG
        session = get_object_or_404(Session, id=request.GET['session'])
        try:
            if request.GET.get('feedback_request').isdigit():
                feedback = Feedback.objects.get_feedback_summary(session, int(request.GET.get('feedback_request')))
            else:
                feedback = Feedback.objects.get_feedback_summary(session, request.GET.get('feedback_request'))
            return JsonResponse(feedback)
        except ValueError:
            pass
    return HttpResponseBadRequest()
