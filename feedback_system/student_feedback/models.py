from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
# Create your models here. These are the classes for Obeject Relational Mapping(ORM)
#class name = relation NAME
#variable name = field/attribute name
#models.FieldType = attribute/column datatype
#parameters: 1st parameter = optional overwrite of column name
#            2nd parameter = Data options
#
#if python manage.py migrate says there are no migration to apply
#try removing any possible conflicts in the django_migrations table :-)
#
#
#good practice for each obejct/relation class to have (__str__) toString

class Lecture(models.Model):
    lecture_title = models.CharField('title', max_length=200)
    slide_count = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
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
