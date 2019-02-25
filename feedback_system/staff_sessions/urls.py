from django.urls import path

from . import views

#this sets the application namespace so that the {% url %} template tag
#creates links based of the names in this file  for this app
#might be mutliple urls with name='detail' across the project
app_name= 'staff_sessions'

#name variable is used to refer to URls to make links in view templates
urlpatterns = [
    #/staff/login/
    path('login/', views.login, name='login'),
    #/staff/session/index
    path('session/index', views.index, name='index'),
]
