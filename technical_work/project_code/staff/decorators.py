from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from staff.models import Lecture, Session, Question
from django.utils.translation import ugettext as _

def must_own_lecture(func):
    def check_and_call(request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            lecture = Lecture.objects.get(pk=pk)
        except Lecture.DoesNotExist:
            raise Http404
        if request.user.is_authenticated:
            if not (lecture.user.id == request.user.id):
                raise PermissionDenied
        return func(request, *args, **kwargs)
    return check_and_call

def must_own_session(func):
    def check_and_call(request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            session = Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404
        if request.user.is_authenticated:
            if not (session.lecture.user.id == request.user.id):
                raise PermissionDenied
        return func(request, *args, **kwargs)
    return check_and_call

def must_own_question(func):
    def check_and_call(request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise Http404
        if request.user.is_authenticated:
            if not (question.session.lecture.user.id == request.user.id):
                raise PermissionDenied
        return func(request, *args, **kwargs)
    return check_and_call
