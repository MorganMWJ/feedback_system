from django.urls import path

from . import views

#this sets the application namespace so that the {% url %} template tag
#creates links based of the names in this file  for this app
#might be mutliple urls with name='detail' across the project
app_name= 'student_feedback'

#name variable is used to refer to URls to make links in view templates
urlpatterns = [
    #/student_feedback/history/lectures
    path('history/lectures', views.index, name='index'),
    #/student_feedback/history/lecture/5
    path('history/lecture/<int:lecture_id>/', views.detail, name='detail'),

    path('history/lecture/<int:lecture_id>/ask/', views.ask, name='ask'),
]
