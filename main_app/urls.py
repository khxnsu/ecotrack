from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activity/add/', views.add_activity, name='add_activity'),
    path('goal/add/', views.add_goal, name='add_goal'),
]
