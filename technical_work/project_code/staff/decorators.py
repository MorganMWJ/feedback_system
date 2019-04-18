from django.http import HttpResponse
from staff.models import Lecture, Session, Question

def must_own_lecture(func):
    def check_and_call(request, *args, **kwargs):
        #user = request.user
        #print user.id
        pk = kwargs["pk"]
        lecture = Lecture.objects.get(pk=pk)
        if not (lecture.user.id == request.user.id):
            return HttpResponse("It is not yours ! You are not permitted !",
                        content_type="application/json", status=403)
        return func(request, *args, **kwargs)
    return check_and_call

def must_own_session(func):
    def check_and_call(request, *args, **kwargs):
        #user = request.user
        #print user.id
        pk = kwargs["pk"]
        session = Session.objects.get(pk=pk)
        if not (session.lecture.user.id == request.user.id):
            return HttpResponse("It is not yours ! You are not permitted !",
                        content_type="application/json", status=403)
        return func(request, *args, **kwargs)
    return check_and_call

def must_own_question(func):
    def check_and_call(request, *args, **kwargs):
        #user = request.user
        #print user.id
        pk = kwargs["pk"]
        question = Question.objects.get(pk=pk)
        if not (question.session.lecture.user.id == request.user.id):
            return HttpResponse("It is not yours ! You are not permitted !",
                        content_type="application/json", status=403)
        return func(request, *args, **kwargs)
    return check_and_call
