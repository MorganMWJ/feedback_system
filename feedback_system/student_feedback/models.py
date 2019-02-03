from django.db import models
from django.utils import timezone
# Create your models here.
#class name = relation NAME
#variable name = field/attribute name
#models.FieldType = attribute/column datatype
#parameters: 1st parameter = optional overwrite of column name
#            2nd parameter = Data options
#
#if python manage.py migrate says there are no migration to apply
#try removing any possible conflicts in the django_migrations table :-)
class Lecture(models.Model):
    lecture_title = models.CharField('title', max_length=200)
    start_time = models.DateTimeField('start_time')
    end_time = models.DateTimeField('end_time')

    def is_currently_on(self):
        return self.start_time < timezone.now() and timezone.now() < self.end_time

    def __str__(self):
        return self.lecture_title


class Question(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('time_posted')

    def __str__(self):
        return self.question_text
