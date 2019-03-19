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
    #/login/
    path('login/', views.login, name='login'),
    #/logout/
    path('logout/', views.logout, name='logout'),
    #/lectures/
    path('lectures/', views.index, name='index'),
    #/lectures/new/
    path('lecture/new/', views.lecture_create, name='lecture_create'),
    #/lectures/?
    path('lecture/<int:id>/', views.lecture_detail, name='lecture_detail'),
    #/lectures/?/edit/
    path('lecture/<int:id>/edit/', views.lecture_update, name='lecture_update'),
    #/lectures/?/delete/
    path('lecture/<int:id>/delete/', views.lecture_delete, name='lecture_delete'),
    #/lectures/?/start_session/
    path('lecture/<int:id>/session/new/', views.session_new, name='session_new'),
    #/lectures/?/stop_session/
    path('session/<int:id>/stop/', views.session_stop, name='session_stop'),
    #/lectures/?/generate_session_code/
    path('session/<int:id>/regenerate_code/', views.session_regenerate_code, name='session_regenerate_code'),
    #/lectures/?/toggle_questions/
    path('session/<int:id>/toggle_questions/', views.session_toggle_questions, name='session_toggle_questions'),
    #/questions/?/review/
    path('question/<int:id>/review/', views.question_mark_reviewed, name='question_mark_reviewed'),
    #/questions/?/delete/
    path('question/<int:id>/delete/', views.question_delete, name='question_delete'),
    #/questions/new/
    path('question/new/', views.question_new, name='question_new'),
    #/feedback/new/
    path('feedback/new/', views.feedback_new, name='feedback_new'),

    path('session/<int:id>/questions/', views.session_question_list, name='session_question_list'),

]
