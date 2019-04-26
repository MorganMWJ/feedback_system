from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from staff.models import Lecture, Session, Question
from django.utils.translation import ugettext as _
from django.contrib import messages

def must_own_lecture(func):
    def check_and_call(request, *args, **kwargs):
        pk = kwargs["pk"]
        lecture = Lecture.objects.get(pk=pk)
        if request.user.is_authenticated:
            if not (lecture.user.id == request.user.id):
                messages.error(request, _('You do not have permission to access this lecture'))
                raise PermissionDenied
        return func(request, *args, **kwargs)
    return check_and_call

def must_own_session(func):
    def check_and_call(request, *args, **kwargs):
        pk = kwargs["pk"]
        session = Session.objects.get(pk=pk)
        if request.user.is_authenticated:
            if not (session.lecture.user.id == request.user.id):
                raise PermissionDenied
        return func(request, *args, **kwargs)
    return check_and_call

def must_own_question(func):
    def check_and_call(request, *args, **kwargs):
        pk = kwargs["pk"]
        question = Question.objects.get(pk=pk)
        if request.user.is_authenticated:
            if not (question.session.lecture.user.id == request.user.id):
                raise PermissionDenied
        return func(request, *args, **kwargs)
    return check_and_call
