from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.template import loader #can remove now we are using the render shortcut
from .models import Lecture, Question
# Create your views here.
def index(request):
    recent_lectures = Lecture.objects.order_by('-end_time')
    #when looking fot templates django will look in every apps templates folder
    #we add another directory layer with the same name as our app to avoid name clashes

    #long away about things
    # template = loader.get_template('student_feedback/index.html')
    # context = {
    #     'latest_lecture_list': recent_lectures,
    # }
    # return HttpResponse(template.render(context,request))

    #shortcut using render()
    context = {'latest_lecture_list': recent_lectures}
    return render(request, 'student_feedback/index.html', context)

def detail(request, lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        context = {'lectureToDetail': lecture}#fills varibales in the template (gives template context)
        return render(request, 'student_feedback/detail.html', context)
    except Lecture.DoesNotExist:
        raise Http404("Lecture %s does not exist" % lecture_id)
