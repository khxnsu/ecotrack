from django.core.management.base import BaseCommand
from main_app.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Sets up initial subscription plans'

    def handle(self, *args, **options):
        plans = [
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

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'price': plan_data['price'],
                    'billing_cycle': plan_data['billing_cycle'],
                    'features': plan_data['features'].strip(),
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {plan.name} plan')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan {plan.name} already exists')
                )
