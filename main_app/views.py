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
    try:
        # Get all active plans
        plans = list(SubscriptionPlan.objects.filter(is_active=True).order_by('price'))
        print(f"Initial plans count: {len(plans)}")  # Debug print
        
        # Create default plans if none exist
        if not plans:
            print("No plans found, creating defaults...")  # Debug print
            default_plans = [
                {
                    'name': 'Community',
                    'price': 0.00,
                    'billing_cycle': 'monthly',
                    'features': '''
                        - Basic activity tracking
                        - Simple goal setting
                        - Community support
                        - Basic reporting
                    '''
                },
                {
                    'name': 'Professional',
                    'price': 29.00,
                    'billing_cycle': 'monthly',
                    'features': '''
                        - Advanced activity tracking
                        - Detailed goal analytics
                        - Priority support
                        - Custom reporting
                        - Team collaboration
                    '''
                },
                {
                    'name': 'Enterprise',
                    'price': 99.00,
                    'billing_cycle': 'monthly',
                    'features': '''
                        - All Professional features
                        - Enterprise-grade support
                        - Custom integrations
                        - Advanced analytics
                        - Dedicated account manager
                        - Custom branding
                    '''
                }
            ]
            
            for plan_data in default_plans:
                try:
                    # Check if plan already exists
                    plan = SubscriptionPlan.objects.filter(name=plan_data['name']).first()
                    if not plan:
                        print(f"Creating plan: {plan_data['name']}")  # Debug print
                        plan = SubscriptionPlan.objects.create(
                            name=plan_data['name'],
                            price=plan_data['price'],
                            billing_cycle=plan_data['billing_cycle'],
                            features=plan_data['features'],
                            is_active=True
                        )
                        print(f"Created plan: {plan.name}")  # Debug print
                except Exception as e:
                    print(f"Error creating plan {plan_data['name']}: {str(e)}")  # Debug print
            
            # Get all plans again after creation
            plans = list(SubscriptionPlan.objects.filter(is_active=True).order_by('price'))
            print(f"Plans after creation: {len(plans)}")  # Debug print
        
        # Convert features text to list for each plan
        for plan in plans:
            print(f"Processing plan: {plan.name}")  # Debug print
            features = []
            for feature in plan.features.strip().split('\n'):
                feature = feature.strip('- ').strip()
                if feature:  # Only add non-empty features
                    features.append(feature)
            plan.feature_list = features
            print(f"Features for {plan.name}: {len(features)}")  # Debug print
        
        context = {
            'plans': plans,
            'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        }
        
        return render(request, 'main_app/pricing.html', context)
    
    except Exception as e:
        print(f"Error in pricing view: {str(e)}")  # Debug print
        import traceback
        print(traceback.format_exc())  # Print full traceback
        # Return an error message to the user
        return render(request, 'main_app/pricing.html', {
            'plans': [],
            'error_message': f'An error occurred while loading the pricing plans: {str(e)}'
        })
