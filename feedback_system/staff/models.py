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

    def get_last_session(self):
        sessions = self.session_set.all()
        if sessions.exists():
            return sessions.order_by('start_time').last()

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
        ('NEGATIVE', 'Bad'),
        ('NEUTRAL', 'So-So'),
    )
    DELIVERY_SPEED_CHOICES = (
        ('V-SLOW', 'Very Slow'),
        ('SLOW', 'Little Slow'),
        ('NORMAL', 'Just Right'),
        ('FAST', 'Little Fast'),
        ('V-FAST', 'Very Fast'),
    )
    CONTENT_COMPLEXITY_CHOICES = (
        ('V-HARD', 'Very Difficult'),
        ('HARD', 'Slightly Difficult'),
        ('NORMAL', 'Normal'),
        ('EASY', 'Slightly Easy'),
        ('V-EASY', 'Very Easy'),
    )
    CONTENT_PRESENTATION_CHOICES = (
        ('NEGATIVE','Not Well Presented'),
        ('NEUTRAL','Well Presented'),
        ('POSITIVE','Very Well Presented'),
    )
    LEVEL_OF_ENGAGMENT_CHOICES = (
        ('NEGATIVE','Not Engaging/Interesting'),
        ('NEUTRAL','Engaging/Interesting'),
        ('POSITIVE','Very Engaging/Interesting'),
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
