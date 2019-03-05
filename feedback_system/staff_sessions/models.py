import random
import string
from django.db import models
from django.core.validators import MinValueValidator

class Lecture(models.Model):
    title = models.CharField(max_length=50)
    slide_count = models.IntegerField(
                    default=1,
                    validators=[MinValueValidator(1)])
    author_username = models.CharField(max_length=10)
    author_forename = models.CharField(max_length=30)
    author_surname = models.CharField(max_length=30)
    session_code = models.CharField(max_length=6, unique=True)
    is_running = models.BooleanField(default=False)
    is_taking_questions = models.BooleanField(default=True)

    def getFirstStartDate(self):
        sessions = self.session_set.all()
        if sessions.exists():
            return sessions.order_by('start_time').first().start_time

    #don't think this function is good or needed, remove?
    def getFirstStartDate_displayStr(self):
        return getFirstStartDate().strftime("%d/%m/%Y, %H:%M")

    @staticmethod
    def getCode():
        code = ""
        for i in range(6):
            code += random.choice(string.ascii_uppercase + string.digits)
        return code

class Session(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    lecture_id = models.ForeignKey(Lecture, on_delete=models.CASCADE)
