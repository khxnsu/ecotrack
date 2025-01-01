from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from .models import EcoActivity, SustainabilityGoal

# Custom actions for User admin
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = "Deactivate selected users"

def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_users.short_description = "Activate selected users"

def make_staff(modeladmin, request, queryset):
    queryset.update(is_staff=True)
make_staff.short_description = "Make selected users staff members"

# Customize the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 
                   'last_login', 'is_active', 'is_staff', 'get_activity_count')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    actions = [activate_users, deactivate_users, make_staff]
    
    def get_activity_count(self, obj):
        count = EcoActivity.objects.filter(user=obj).count()
        return format_html('<a href="/admin/main_app/ecoactivity/?user__id__exact={}">{} activities</a>', 
                         obj.id, count)
    get_activity_count.short_description = 'Activities'

# Custom actions for EcoActivity admin
def mark_as_verified(modeladmin, request, queryset):
    queryset.update(verified=True, verified_at=timezone.now())
mark_as_verified.short_description = "Mark selected activities as verified"

@admin.register(EcoActivity)
class EcoActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'value', 'unit', 'date', 'impact_level', 
                   'verified', 'verification_status', 'location')
    list_filter = ('category', 'verified', 'impact_level', 'date', 'user')
    search_fields = ('description', 'user__username', 'location', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['verify_activities', 'mark_high_impact', 'mark_medium_impact', 'mark_low_impact']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'category', 'description', 'value', 'unit', 'date')
        }),
        ('Impact Details', {
            'fields': ('impact_level', 'location', 'tags'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('verified', 'verified_at', 'verified_by'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def verification_status(self, obj):
        if obj.verified:
            return format_html(
                '<span style="color: green;">✓ Verified by {} on {}</span>',
                obj.verified_by.username if obj.verified_by else 'Unknown',
                obj.verified_at.strftime('%Y-%m-%d %H:%M') if obj.verified_at else 'Unknown date'
            )
        return format_html('<span style="color: red;">✗ Not verified</span>')
    verification_status.short_description = 'Verification'

    def verify_activities(self, request, queryset):
        queryset.update(
            verified=True,
            verified_at=timezone.now(),
            verified_by=request.user
        )
    verify_activities.short_description = "Mark selected activities as verified"

    def mark_high_impact(self, request, queryset):
        queryset.update(impact_level='HIGH')
    mark_high_impact.short_description = "Mark as High Impact"

    def mark_medium_impact(self, request, queryset):
        queryset.update(impact_level='MEDIUM')
    mark_medium_impact.short_description = "Mark as Medium Impact"

    def mark_low_impact(self, request, queryset):
        queryset.update(impact_level='LOW')
    mark_low_impact.short_description = "Mark as Low Impact"

# Custom actions for SustainabilityGoal admin
def mark_as_completed(modeladmin, request, queryset):
    queryset.update(status='COMPLETED')
mark_as_completed.short_description = "Mark selected goals as completed"

def mark_as_in_progress(modeladmin, request, queryset):
    queryset.update(status='IN_PROGRESS')
mark_as_in_progress.short_description = "Mark selected goals as in progress"

@admin.register(SustainabilityGoal)
class SustainabilityGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category', 'progress_display', 'deadline', 
                   'status', 'priority', 'assigned_to')
    list_filter = ('status', 'priority', 'category', 'deadline', 'user')
    search_fields = ('title', 'description', 'user__username', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at', 'last_reminder_sent')
    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled', 'send_reminders']
    date_hierarchy = 'deadline'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Goal Details', {
            'fields': ('target_value', 'current_value', 'unit', 'deadline', 'status', 'priority')
        }),
        ('Assignment & Reminders', {
            'fields': ('assigned_to', 'reminder_frequency', 'last_reminder_sent'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def progress_display(self, obj):
        progress = obj.calculate_progress()
        color = 'red'
        if progress >= 100:
            color = 'green'
        elif progress >= 50:
            color = 'orange'
        
        return format_html(
            '<div style="width:100px; height:20px; background-color:#f0f0f0; border:1px solid #ccc;">'
            '<div style="width:{}px; height:100%; background-color:{};">'
            '<div style="color: white; text-align: center;">{}</div>'
            '</div></div>',
            min(progress, 100),
            color,
            f"{progress}%"
        )
    progress_display.short_description = 'Progress'

    def mark_in_progress(self, request, queryset):
        queryset.update(status='IN_PROGRESS')
    mark_in_progress.short_description = "Mark as In Progress"

    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
    mark_completed.short_description = "Mark as Completed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
    mark_cancelled.short_description = "Mark as Cancelled"

    def send_reminders(self, request, queryset):
        # TODO: Implement reminder sending logic
        self.message_user(request, "Reminders have been queued for sending.")
    send_reminders.short_description = "Send reminders for selected goals"

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize admin site header and title
admin.site.site_header = "EcoTrack Administration"
admin.site.site_title = "EcoTrack Admin Portal"
admin.site.index_title = "Welcome to EcoTrack Admin Portal"
