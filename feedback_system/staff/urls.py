from django.urls import path

from . import views

#this sets the application namespace so that the {% url %} template tag
#creates links based of the names in this file  for this app
#might be mutliple urls with name='detail' across the project
app_name= 'staff'

#name variable is used to refer to URls to make links in view templates
urlpatterns = [
    #/
    path('', views.connect, name='connect'),
    path('connect/', views.connect, name='connect'),
    path('disconnect/', views.disconnect, name='disconnect'),
    path('feedback/', views.feedback, name='feedback'),
    #/staff/login/
    path('login/', views.login, name='login'),
    #/staff/logout/
    path('logout/', views.logout, name='logout'),
    #/staff/lectures/
    path('lectures/', views.index, name='index'),
    #/staff/lectures/new/
    path('lectures/new/', views.lecture_new, name='lecture_new'),
    #/staff/lectures/?
    path('lectures/<int:id>/', views.lecture_detail, name='lecture_detail'),
    #/staff/lectures/?/delete/
    path('lectures/<int:id>/delete/', views.lecture_delete, name='lecture_delete'),
    #/staff/lectures/?/start_session/
    path('lectures/<int:id>/start_session/', views.lecture_start_feedback_session, name='lecture_start_feedback_session'),
    #/staff/lectures/?/stop_session/
    path('lectures/<int:id>/stop_session/', views.lecture_stop_feedback_session, name='lecture_stop_feedback_session'),
    #/staff/lectures/?/generate_session_code/
    path('lectures/<int:id>/generate_session_code/', views.lecture_generate_session_code, name='lecture_generate_session_code'),
    #/staff/lectures/?/toggle_questions/
    path('lectures/<int:id>/toggle_questions/', views.lecture_toggle_questions, name='lecture_toggle_questions'),
    #/staff/questions/?/review/
    path('questions/<int:id>/review/', views.question_mark_reviewed, name='question_mark_reviewed'),
    #/staff/questions/?/delete/
    path('questions/<int:id>/delete/', views.question_delete, name='question_delete'),
    #/staff/questions/new/
    path('questions/new/', views.question_new, name='question_new'),
    #/staff/feedback/new/
    path('feedback/new/', views.feedback_new, name='feedback_new'),
]
