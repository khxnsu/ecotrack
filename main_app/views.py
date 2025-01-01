from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import EcoActivity, SustainabilityGoal, SubscriptionPlan
from .forms import EcoActivityForm, SustainabilityGoalForm, UserRegistrationForm
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .utils import create_stripe_checkout_session, handle_subscription_created, handle_subscription_deleted

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

def home(request):
    return render(request, 'main_app/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'main_app/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get recent activities
    recent_activities = EcoActivity.objects.filter(
        user=request.user
    ).order_by('-date')[:5]

    # Get active goals
    active_goals = SustainabilityGoal.objects.filter(
        user=request.user,
        status__in=['PENDING', 'IN_PROGRESS']
    ).order_by('deadline')

    # Calculate summary statistics
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    monthly_stats = EcoActivity.objects.filter(
        user=request.user,
        date__gte=month_start
    ).values('category').annotate(
        total=Sum('value')
    )

    context = {
        'recent_activities': recent_activities,
        'active_goals': active_goals,
        'monthly_stats': monthly_stats,
    }
    return render(request, 'main_app/dashboard.html', context)

@login_required
def add_activity(request):
    if request.method == 'POST':
        form = EcoActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            messages.success(request, 'Activity added successfully!')
            return redirect('main_app:dashboard')
    else:
        form = EcoActivityForm()
    
    return render(request, 'main_app/activity_form.html', {'form': form})

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = SustainabilityGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal created successfully!')
            return redirect('main_app:dashboard')
    else:
        form = SustainabilityGoalForm()
    
    return render(request, 'main_app/goal_form.html', {'form': form})

@login_required
def create_checkout_session(request, plan_id):
    """Create a Stripe Checkout Session for subscription"""
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        checkout_session = create_stripe_checkout_session(request, plan)
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def subscription_success(request):
    """Handle successful subscription"""
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return render(request, 'main_app/subscription_success.html', {
                'subscription': session
            })
        except Exception as e:
            messages.error(request, f"Error processing subscription: {str(e)}")
    return redirect('main_app:pricing')

@login_required
def cancel_subscription(request):
    """Cancel user's subscription"""
    if request.method == 'POST':
        try:
            subscription = request.user.usersubscription
            subscription.cancel()
            messages.success(request, "Your subscription has been cancelled.")
        except Exception as e:
            messages.error(request, f"Error cancelling subscription: {str(e)}")
    return redirect('main_app:dashboard')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event.type == 'customer.subscription.created':
        handle_subscription_created(event)
    elif event.type == 'customer.subscription.deleted':
        handle_subscription_deleted(event)

    return HttpResponse(status=200)

def pricing(request):
    """Display pricing plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    # Convert features text to list for each plan
    for plan in plans:
        # Split features by newline and clean up
        plan.feature_list = [
            feature.strip('- ').strip() 
            for feature in plan.features.strip().split('\n') 
            if feature.strip()
        ]
    
    context = {
        'plans': plans,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
    }
    return render(request, 'main_app/pricing.html', context)
