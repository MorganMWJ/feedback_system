from django.urls import path

from . import views

#this sets the application namespace so that the {% url %} template tag
#creates links based of the names in this file  for this app
#might be mutliple urls with name='detail' across the project
app_name= 'staff'

#name variable is used to refer to URls to make links in view templates
urlpatterns = [
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
    #/staff/lectures/delete/?
    path('lectures/delete/<int:id>/', views.lecture_delete, name='lecture_delete'),
]
