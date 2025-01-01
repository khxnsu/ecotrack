import stripe
from django.conf import settings
from django.urls import reverse
from datetime import datetime, timedelta

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

def create_stripe_checkout_session(request, plan):
    """Create a Stripe Checkout Session for subscription"""
    if not stripe.api_key:
        raise ValueError("Stripe API key not configured")

    success_url = request.build_absolute_uri(
        reverse('main_app:subscription_success')
    )
    cancel_url = request.build_absolute_uri(
        reverse('main_app:pricing')
    )
    
    # Create or get Stripe Product and Price
    stripe_product = stripe.Product.create(
        name=plan.name,
        description=plan.features
    )
    
    stripe_price = stripe.Price.create(
        product=stripe_product.id,
        unit_amount=int(plan.price * 100),  # Convert to cents
        currency='usd',
        recurring={
            'interval': plan.billing_cycle
        }
    )
    
    # Create Checkout Session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': stripe_price.id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=cancel_url,
        customer_email=request.user.email,
        client_reference_id=str(request.user.id),
        metadata={
            'plan_id': plan.id
        }
    )
    
    return checkout_session

def handle_subscription_created(event):
    """Handle the subscription.created webhook event"""
    if not stripe.api_key:
        return
        
    subscription = event.data.object
    user_id = int(subscription.client_reference_id)
    
    # Get the subscription end date
    if subscription.status == 'active':
        current_period_end = datetime.fromtimestamp(subscription.current_period_end)
    else:
        current_period_end = datetime.now() + timedelta(days=30)
    
    # Update or create UserSubscription
    from .models import UserSubscription, SubscriptionPlan, User
    user = User.objects.get(id=user_id)
    plan = SubscriptionPlan.objects.get(id=subscription.metadata.plan_id)
    
    UserSubscription.objects.update_or_create(
        user=user,
        defaults={
            'plan': plan,
            'end_date': current_period_end,
            'is_active': True,
            'stripe_subscription_id': subscription.id
        }
    )

def handle_subscription_deleted(event):
    """Handle the subscription.deleted webhook event"""
    if not stripe.api_key:
        return
        
    subscription = event.data.object
    
    from .models import UserSubscription
    try:
        user_sub = UserSubscription.objects.get(stripe_subscription_id=subscription.id)
        user_sub.is_active = False
        user_sub.save()
    except UserSubscription.DoesNotExist:
        pass
