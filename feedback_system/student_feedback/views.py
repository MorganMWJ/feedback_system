from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.urls import reverse
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

def ask(request, lecture_id):
    try:
        lecture = get_object_or_404(Lecture, id=lecture_id)
        #if question already asked, dislay error and form again
        if request.POST['question_asked'] in [q.question_text for q in lecture.question_set.all()]:
            # Redisplay the question voting form.
            return render(request, 'student_feedback/detail.html', {
                'lectureToDetail': lecture,
                'error_message': "That Question has already been asked.",
            })
        elif request.POST['question_asked'] == "":
            #Redisplay voting form
            return render(request, 'student_feedback/detail.html', {
                'lectureToDetail': lecture,
                'error_message': "Cannot have empty question",
            })
        else:
            lecture.question_set.create(question_text=request.POST['question_asked'], pub_date=timezone.now())
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('student_feedback:details', args=(lecture.id,))) #trailing comma require to disambiguate between tuple and expression in paranthesis
    except (KeyError, Lecture.DoesNotExist):
        return render(request, 'student_feedback/detail.html', {
            'lectureToDetail': lecture,
            'error_message': "Please enter a valid question"
        })
