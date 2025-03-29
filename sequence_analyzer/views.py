from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, SequenceSubmissionForm
from .models import SequenceSubmission

# Create your views here.

def home(request):
    return render(request, 'sequence_analyzer/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'sequence_analyzer/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'sequence_analyzer/dashboard.html')

@login_required
def submit_sequence(request):
    if request.method == 'POST':
        form = SequenceSubmissionForm(request.user, request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            messages.success(request, "Sequence submitted successfully!")
            return redirect('view_submissions')
    else:
        form = SequenceSubmissionForm(request.user)
    return render(request, 'sequence_analyzer/submit_sequence.html', {'form': form})

@login_required
def view_submissions(request):
    submissions = SequenceSubmission.objects.filter(user=request.user)
    return render(request, 'sequence_analyzer/view_submissions.html', {'submissions': submissions})
