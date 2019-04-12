from django.urls import path

from . import views
from staff.views import LectureList, LectureDetail, LectureDelete
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
    path('feedback/new/', views.feedback_new, name='feedback_new'),


    #/login/
    path('login/', views.login, name='login'),
    #/logout/
    path('logout/', views.logout, name='logout'),
    #/lectures/
    path('lectures/', LectureList.as_view(), name="lecture_list"),
    #/lecturs/new/
    path('lecture/new/', views.lecture_create, name='lecture_create'),
    #/lecture/?
    path('lecture/<int:pk>/', LectureDetail.as_view(), name='lecture_detail'),
    #/lecture/?/feedback_detail
    path('lecture/<int:id>/feedback_detail/', views.feedback_detail, name='feedback_detail'),
    #/lecture/?/edit/
    path('lecture/<int:pk>/edit/', views.lecture_update, name='lecture_update'),
    #/lecture/?/delete/
    path('lecture/<int:pk>/delete/', LectureDelete.as_view(), name='lecture_delete'),
    #/lecture/?/start_session/
    path('lecture/<int:id>/session/new/', views.session_new, name='session_new'),
    #/lecture/?/stop_session/
    path('session/<int:id>/stop/', views.session_stop, name='session_stop'),
    #/session/?/delete/
    path('session/<int:id>/delete/', views.session_delete, name='session_delete'),
    #/session/?/merge_with_previous/
    path('session/<int:id>/merge_with_previous/', views.session_merge_previous, name='session_merge_previous'),
    #/session/?/merge_with_previous/
    path('session/<int:id>/merge_with_next/', views.session_merge_next, name='session_merge_next'),
    #/lecture/?/generate_session_code/
    path('session/<int:id>/regenerate_code/', views.session_regenerate_code, name='session_regenerate_code'),
    #/lecture/?/toggle_questions/
    path('session/<int:id>/toggle_questions/', views.session_toggle_questions, name='session_toggle_questions'),
    #/questions/?/review/
    path('question/<int:id>/review/', views.question_mark_reviewed, name='question_mark_reviewed'),
    #/questions/?/delete/
    path('question/<int:id>/delete/', views.question_delete, name='question_delete'),
    #/questions/new/
    path('question/new/', views.question_new, name='question_new'),



    #html reloaded via ajax
    path('session/<int:id>/questions/', views.session_questions, name='session_questions'),
    path('lecture/<int:id>/sessions/<str:version>/', views.lecture_sessions, name='lecture_sessions'),


    #probably no longer using these below
    path('api/feedbackdata/', views.session_feedback_chart_data, name='session_feedback_chart_data'),

]
