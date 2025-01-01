from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EcoActivity, SustainabilityGoal

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class EcoActivityForm(forms.ModelForm):
    class Meta:
        model = EcoActivity
        fields = ['category', 'description', 'value', 'unit', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class SustainabilityGoalForm(forms.ModelForm):
    class Meta:
        model = SustainabilityGoal
        fields = ['title', 'description', 'target_value', 'current_value', 'unit', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        target_value = cleaned_data.get('target_value')
        current_value = cleaned_data.get('current_value')
        
        if target_value and current_value and current_value > target_value:
            raise forms.ValidationError("Current value cannot be greater than target value.")
