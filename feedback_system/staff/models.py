import random
import string
import datetime
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator

class Lecture(models.Model):
    title = models.CharField(max_length=150)
    slide_count = models.IntegerField(
                    default=1,
                    validators=[MinValueValidator(1)])
    author_username = models.CharField(max_length=10)
    author_forename = models.CharField(max_length=30)
    author_surname = models.CharField(max_length=30)
    session_code = models.CharField(max_length=6, unique=True)
    is_running = models.BooleanField(default=False)
    is_taking_questions = models.BooleanField(default=True)
    notes = models.TextField(null=True)

    def getFirstStarted(self):
        sessions = self.session_set.all()
        if sessions.exists():
            return sessions.order_by('start_time').first().start_time

    def getFirstStarted_datetime(self):
        sessions = self.session_set.all()
        if sessions.exists():
            return sessions.order_by('start_time').first().start_time.strftime("%d/%m/%Y %H:%M:%S")

    def getFirstStarted_date(self):
        sessions = self.session_set.all()
        if sessions.exists():
            return sessions.order_by('start_time').first().start_time.strftime("%d/%m/%Y")

    def getLastEnded(self):
        sessions = self.session_set.all()
        try:
            if sessions.exists():
                return sessions.order_by('end_time').last().end_time
        except AttributeError:
            return None

    def getLastEnded_datetime(self):
        sessions = self.session_set.all()
        try:
            if sessions.exists():
                return sessions.order_by('end_time').last().end_time.strftime("%d/%m/%Y %H:%M:%S")
        except AttributeError:
            return None

    def getTotalRuntime(self):
        sessions = self.session_set.all()
        runtimes = [session.getRuntime() for session in sessions]
        return sum(runtimes, datetime.timedelta())

    def __str__(self):
        return self.title

    @staticmethod
    def getCode():
        code = ""
        #while code is empty or code already in db
        while code=="" or Lecture.objects.filter(session_code=code).count()>0:
            for i in range(6):
                code += random.choice(string.ascii_uppercase + string.digits)
        return code

class Session(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    lecture_id = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    def getRuntime(self):
        if self.end_time is None:
            return (timezone.now()-self.start_time)
        else:
            return (self.end_time-self.start_time)

    def getRuntime_timestr(self):
        time = None
        if self.end_time is None:
            time = (timezone.now()-self.start_time)
        else:
            time = (self.end_time-self.start_time)

        total_seconds = int(time.total_seconds())
        hours, remainder = divmod(total_seconds,60*60)
        minutes, seconds = divmod(remainder,60)
        return '{} hrs {} mins {} secs'.format(hours,minutes,seconds)

class Question(models.Model):
    question_text = models.CharField(max_length=300)
    time_posted = models.DateTimeField()
    is_reviewed = models.BooleanField(default=False)
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text
