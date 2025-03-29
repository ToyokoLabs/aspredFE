from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SequenceSubmission
from django.core.exceptions import ValidationError
from datetime import datetime, timezone
from django.utils.timezone import make_aware

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class SequenceSubmissionForm(forms.ModelForm):
    class Meta:
        model = SequenceSubmission
        fields = ['sequence']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user:
            # Check if user has already submitted today
            today = make_aware(datetime.now())
            today_submission = SequenceSubmission.objects.filter(
                user=self.user,
                submit_date__year=today.year,
                submit_date__month=today.month,
                submit_date__day=today.day
            ).exists()
            
            if today_submission:
                raise ValidationError("You have already submitted a sequence today. Please try again tomorrow.")
