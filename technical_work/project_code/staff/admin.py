from django.contrib import admin
from staff.models import Lecture, Session, Question, Feedback
# Register your models here.
admin.site.register(Lecture)
admin.site.register(Session)
admin.site.register(Question)
admin.site.register(Feedback)
