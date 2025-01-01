from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main_app import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='main_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main_app:home'), name='logout'),
    path('register/', main_views.register, name='register'),
]
