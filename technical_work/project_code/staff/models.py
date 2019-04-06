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
    date_created = models.DateTimeField()
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
        return reverse('staff:lecture_detail', kwargs={'id': self.pk})

class Session(models.Model):
    # date_last_merged = models.DateTimeField(null=True)
    # total_runtime = models.IntegerField(default=0)
    code = models.CharField(max_length=6, unique=True, validators=[alphanumeric])
    is_running = models.BooleanField(default=True)
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
        times = self.time_set.all()
        return times.order_by('start').first().start

    def get_last_end_time(self):
        times = self.time_set.all()
        return times.order_by('end').last().end

    def end(self):
        instance = self.time_set.filter(end=None).first()
        instance.end = timezone.now()
        instance.save()

    def __str__(self):
        return self.code

    def get_feedback_summary(self):
        summary = []
        import pdb
        #pdb.set_trace()
        titles = ["Overall Lecture Feedback", "Lecture Delivery Speed", "Complexity of Lecture Content",
                    "Lecture Interest/Enagment", "Quality of Lecture Presentation"]
        three_option_colours = ["#3cba9f", "#c4c22f", "#c45850"] #green, yellow, red
        five_option_colours = ["#0000ff", "#00ccff", "#3cba9f", "#c45850", "#ff0000"]

        dict = {"title": titles[0],
                        "labels": [],
                        "data": []}
        choices = Feedback._meta.get_field('overall_feedback').choices
        for choice in choices:
            dict["labels"].append(choice[1])
            dict["data"].append(Feedback.objects.filter(overall_feedback=choice[0], session=self).count())
        dict["colours"] = three_option_colours
        summary.append(dict)

        dict = {"title": titles[1],
                        "labels": [],
                        "data": []}
        choices = Feedback._meta.get_field('delivery_speed').choices
        for choice in choices:
            dict["labels"].append(choice[1])
            dict["data"].append(Feedback.objects.filter(delivery_speed=choice[0], session=self).count())
        dict["colours"] = five_option_colours
        summary.append(dict)

        dict = {"title": titles[2],
                        "labels": [],
                        "data": []}
        choices = Feedback._meta.get_field('content_complexity').choices
        for choice in choices:
            dict["labels"].append(choice[1])
            dict["data"].append(Feedback.objects.filter(content_complexity=choice[0], session=self).count())
        dict["colours"] = five_option_colours
        summary.append(dict)

        dict = {"title": titles[3],
                        "labels": [],
                        "data": []}
        choices = Feedback._meta.get_field('level_of_engagement').choices
        for choice in choices:
            dict["labels"].append(choice[1])
            dict["data"].append(Feedback.objects.filter(level_of_engagement=choice[0], session=self).count())
        dict["colours"] = three_option_colours
        summary.append(dict)

        dict = {"title": titles[4],
                        "labels": [],
                        "data": []}
        choices = Feedback._meta.get_field('content_presentation').choices
        for choice in choices:
            dict["labels"].append(choice[1])
            dict["data"].append(Feedback.objects.filter(content_presentation=choice[0], session=self).count())
        dict["colours"] = three_option_colours
        summary.append(dict)

        return {'feedback_summary': summary}


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

    # class Meta:
    #     ordering = ('time__start', )

class Time(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def get_runtime(self):
        if self.session.is_running and self.end==None:
            return timezone.now()-self.start
        else:
            return self.end-self.start

    class Meta:
        ordering = ('start', 'end',)

class Question(models.Model):
    question_text = models.CharField(max_length=300)
    time_posted = models.DateTimeField()
    is_reviewed = models.BooleanField(default=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def get_time_posted_ago(self):
        return timezone.now() - self.time_posted

    def __str__(self):
        return self.question_text

class Feedback(models.Model):
    OVERALL_FEEDBACK_CHOICES = (
        ('POSITIVE', 'Good'),
        ('NEUTRAL', 'So-So'),
        ('NEGATIVE', 'Bad'),
    )
    DELIVERY_SPEED_CHOICES = (
        ('V-SLOW', 'Very Slow'),
        ('SLOW', 'Little Slow'),
        ('NORMAL', 'Just Right'),
        ('FAST', 'Little Fast'),
        ('V-FAST', 'Very Fast'),
    )
    CONTENT_COMPLEXITY_CHOICES = (
        ('V-EASY', 'Very Easy'),
        ('EASY', 'Slightly Easy'),
        ('NORMAL', 'Normal'),
        ('HARD', 'Slightly Difficult'),
        ('V-HARD', 'Very Difficult'),
    )
    CONTENT_PRESENTATION_CHOICES = (
        ('POSITIVE','Very Well Presented'),
        ('NEUTRAL','Well Presented'),
        ('NEGATIVE','Not Well Presented'),

    )
    LEVEL_OF_ENGAGMENT_CHOICES = (
        ('POSITIVE','Very Engaging/Interesting'),
        ('NEUTRAL','Engaging/Interesting'),
        ('NEGATIVE','Not Engaging/Interesting'),
    )

    time_posted = models.DateTimeField()
    slide_number = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    overall_feedback = models.CharField(max_length=30,
                                        choices=OVERALL_FEEDBACK_CHOICES,
                                        default='')
    delivery_speed = models.CharField(max_length=30,
                                        choices=DELIVERY_SPEED_CHOICES,
                                        default='NORMAL')
    content_complexity = models.CharField(max_length=30,
                                        choices=CONTENT_COMPLEXITY_CHOICES,
                                        default='')
    content_presentation = models.CharField(max_length=30,
                                        choices=CONTENT_PRESENTATION_CHOICES,
                                        default='')
    level_of_engagement = models.CharField(max_length=30,
                                        choices=LEVEL_OF_ENGAGMENT_CHOICES,
                                        default='')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
