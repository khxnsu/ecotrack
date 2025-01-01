from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activity/add/', views.add_activity, name='add_activity'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('pricing/', views.pricing, name='pricing'),
    
    # Subscription URLs
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='checkout'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
