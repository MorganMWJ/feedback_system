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

    def get_first_started(self):
        sessions = self.session_set.all()
        if sessions.exists():
            return sessions.order_by('start_time').first().start_time
        else:
            return None

    def get_last_ended(self):
        sessions = self.session_set.all()
        if sessions.exists() and not sessions.order_by('start_time').last().is_running:
            return sessions.order_by('start_time').last().end_time
        elif sessions.exists() and sessions.order_by('start_time').last().is_running and len(sessions)>1:
            return sessions.order_by('start_time').reverse()[1].end_time
        else:
            return None

    def get_total_runtime(self):
        sessions = self.session_set.all()
        runtimes = [session.get_runtime() for session in sessions]
        return sum(runtimes, datetime.timedelta())

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('staff:lecture_detail', kwargs={'id': self.pk})

class Session(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
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

    def get_runtime(self):
        if self.end_time is None:
            return (timezone.now()-self.start_time)
        else:
            return (self.end_time-self.start_time)

    def is_owned_by_user(self, logged_in_user):
        return self.lecture.user==logged_in_user

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


    def merge_previous(self):
        #get the sessions ordered by start time
        sessions = self.lecture.session_set.all().order_by("start_time")
        #get the session before this session in the result
        indexOfPrevious = -1
        for index, item in enumerate(sessions, 0):
            #if this is first one throw exception
            if index==0 and item==self:
                raise Exception('No previous session to merge with')
            elif item==self:
                indexOfPrevious = index-1
        #merge with that session
        previousSession = list(sessions)[indexOfPrevious]
        previousSessionFeedback = previousSession.feedback_set.all()
        for f in previousSessionFeedback:
            f.session = self
            f.save()
        self.start_time = previousSession.start_time
        self.save()
        #when done delete the uneeded session
        previousSession.delete()

    def merge_next(self):
        pass

class StartEndTime(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

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



    # def __str__(self):
    #     res = str(self.slide_number) + "=>"
    #     res += self.overall_feedback + "|"
    #     res += self.delivery_speed + "|"
    #     res += self.content_complexity + "|"
    #     res += self.content_presentation + "|"
    #     res += self.level_of_engagement + "|"
    #     return res
