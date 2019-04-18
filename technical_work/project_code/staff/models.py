import random
import string
import datetime
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters allowed.')

class Lecture(models.Model):
    title = models.CharField(max_length=150)
    slide_count = models.IntegerField(
                    default=1,
                    validators=[MinValueValidator(1)])
    notes = models.TextField(null=True)
    file = models.FileField(null=True, upload_to='documents/')
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_last_active_date(self):
        sessions = self.session_set.all()
        for session in sessions:
            if session.is_running:
                return timezone.now()
        if sessions.exists():
            return sessions.order_by('time__end').last()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('staff:lecture_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('-date_created', )

class Session(models.Model):
    code = models.CharField(max_length=6, unique=True, validators=[alphanumeric])
    is_running = models.BooleanField(default=False)
    is_taking_questions = models.BooleanField(default=True)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    @staticmethod
    def generate_code():
        code = ""
        #while code is empty or code already in db
        while code=="" or Session.objects.filter(code=code).count()>0:
            for i in range(6):
                code += random.choice(string.ascii_uppercase + string.digits)
        return code

    def get_total_runtime(self):
        times = self.time_set.all()
        total = sum([int(time.get_runtime().total_seconds()) for time in times])
        return total

    def is_owned_by_user(self, logged_in_user):
        return self.lecture.user==logged_in_user

    def get_first_start_time(self):
        try:
            time = self.time_set.earliest('start')
            first_start_time = time.start
            return first_start_time
        except Time.DoesNotExist:
            print("This session has no start times")
            return None

    def get_last_end_time(self):
        try:
            time = self.time_set.filter(end__isnull=False).latest('end')
            last_end_time = time.end
            return last_end_time
        except Time.DoesNotExist:
            print("This session has no end times")
            return None

    def end(self):
        instance = self.time_set.filter(end=None).first()
        instance.end = timezone.now()
        instance.save()

    def __str__(self):
        return self.code

    def merge(self, merge_type):
        #get the sessions ordered by start time
        sessions = self.lecture.session_set.all()
        #get the session before this session in the result
        indexOfMergeTarget = -1
        if merge_type=='previous':
            for index, item in enumerate(sessions, 0):
                #if this is first one throw exception
                if index==0 and item==self:
                    raise Exception('No MergeTarget session to merge with')
                elif item==self:
                    indexOfMergeTarget = index-1
        elif merge_type=='next':
            for index, item in enumerate(sessions, 0):
                #if this is last one throw exception
                if index==len(sessions)-1 and item==self:
                    raise Exception('No MergeTarget session to merge with')
                elif item==self:
                    indexOfMergeTarget = index+1
        #merge with that session
        mergeTargetSession = Session.objects.get(pk=list(sessions)[indexOfMergeTarget].id)
        mergeTargetSessionFeedback = mergeTargetSession.feedback_set.all()
        for f in mergeTargetSessionFeedback:
            f.session = self
            f.save()
        mergeTargetSessionQuestions = mergeTargetSession.question_set.all()
        for q in mergeTargetSessionQuestions:
            q.session = self
            q.save()
        mergeTargetSessionTimes = mergeTargetSession.time_set.all()
        for t in mergeTargetSessionTimes:
            t.session = self
            t.save()
        #when done delete the uneeded session
        mergeTargetSession.delete()

    class Meta:
        ordering = ('time', )

class Time(models.Model):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def get_runtime(self):
        if self.session.is_running and self.end==None:
            return timezone.now()-self.start
        elif self.end!=None and self.start!=None:
            return self.end-self.start
        else:
            return datetime.timedelta(0, 0, 0)

    class Meta:
        ordering = ('start', )

class Question(models.Model):
    question_text = models.CharField(max_length=300)
    time_posted = models.DateTimeField()
    is_reviewed = models.BooleanField(default=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def get_time_posted_ago(self):
        return timezone.now() - self.time_posted

    def __str__(self):
        return self.question_text

class FeedbackManager(models.Manager):
    def get_feedback_summary(self, session, feedback_subset):
        if feedback_subset not in ['all', 'general'] and not isinstance(feedback_subset, int):
            raise ValueError("Not valid feedback subset option")
        if isinstance(feedback_subset, int) and (feedback_subset<=1 or feedback_subset>=session.lecture.slide_count):
            raise ValueError("Not valid feedback subset option")

        summary = {}
        three_chart_colours = ["#3cba9f", "#c4c22f", "#c45850"] #green, yellow, red
        five_chart_colours = ["#0000ff", "#00ccff", "#3cba9f", "#c45850", "#ff0000"]
        feedback_meta_info =  [["overall_feedback", "Overall Lecture Feedback", three_chart_colours],
                               ["delivery_speed", "Lecture Delivery Speed", five_chart_colours],
                               ["content_complexity", "Complexity of Lecture Content", five_chart_colours],
                               ["level_of_engagement", "Lecture Interest/Enagment", three_chart_colours],
                               ["content_presentation", "Quality of Lecture Presentation", three_chart_colours]]

        #create the feedback dictionary to return
        for fmi in feedback_meta_info:
            summary[fmi[0]] = {'title': fmi[1],
                                'labels': [],
                                'data': [],
                                'colours': fmi[2]}
            for choice in Feedback._meta.get_field(fmi[0]).choices:
                if choice[0]!=None:
                    summary[fmi[0]]['labels'].append(choice[1])
                    if feedback_subset=='all':
                        exec("summary[fmi[0]]['data'].append(Feedback.objects.filter("+ fmi[0] +"=choice[0], session=session).count())")
                    elif feedback_subset=='general':
                        exec("summary[fmi[0]]['data'].append(Feedback.objects.filter("+ fmi[0] +"=choice[0], slide_number=0, session=session).count())")
                    else:
                        exec("summary[fmi[0]]['data'].append(Feedback.objects.filter("+ fmi[0] +"=choice[0], slide_number="+ str(feedback_subset) +", session=session).count())")
        return summary

class Feedback(models.Model):
    OVERALL_FEEDBACK_CHOICES = (
        (None, 'Not Specified'),
        ('POSITIVE', 'Good'),
        ('NEUTRAL', 'So-So'),
        ('NEGATIVE', 'Bad'),
    )
    DELIVERY_SPEED_CHOICES = (
        (None, 'Not Specified'),
        ('V-SLOW', 'Very Slow'),
        ('SLOW', 'Little Slow'),
        ('NORMAL', 'Just Right'),
        ('FAST', 'Little Fast'),
        ('V-FAST', 'Very Fast'),
    )
    CONTENT_COMPLEXITY_CHOICES = (
        (None, 'Not Specified'),
        ('V-EASY', 'Very Easy'),
        ('EASY', 'Slightly Easy'),
        ('NORMAL', 'Normal'),
        ('HARD', 'Slightly Difficult'),
        ('V-HARD', 'Very Difficult'),
    )
    CONTENT_PRESENTATION_CHOICES = (
        (None, 'Not Specified'),
        ('POSITIVE','Very Well Presented'),
        ('NEUTRAL','Well Presented'),
        ('NEGATIVE','Not Well Presented'),

    )
    LEVEL_OF_ENGAGMENT_CHOICES = (
        (None, 'Not Specified'),
        ('POSITIVE','Very Engaging/Interesting'),
        ('NEUTRAL','Engaging/Interesting'),
        ('NEGATIVE','Not Engaging/Interesting'),
    )

    time_posted = models.DateTimeField()
    slide_number = models.IntegerField(validators=[MinValueValidator(0)])
    overall_feedback = models.CharField(max_length=30,
                                        blank=True,
                                        null=True,
                                        choices=OVERALL_FEEDBACK_CHOICES)
    delivery_speed = models.CharField(max_length=30,
                                        blank=True,
                                        null=True,
                                        choices=DELIVERY_SPEED_CHOICES)
    content_complexity = models.CharField(max_length=30,
                                        blank=True,
                                        null=True,
                                        choices=CONTENT_COMPLEXITY_CHOICES)
    content_presentation = models.CharField(max_length=30,
                                        blank=True,
                                        null=True,
                                        choices=CONTENT_PRESENTATION_CHOICES)
    level_of_engagement = models.CharField(max_length=30,
                                        blank=True,
                                        null=True,
                                        choices=LEVEL_OF_ENGAGMENT_CHOICES)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    objects = FeedbackManager()
