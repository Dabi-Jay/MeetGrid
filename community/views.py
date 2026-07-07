from django.shortcuts import render, redirect
from .models import Event
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import EventForm


def home_view(request):
    return render(request, 'home/home.html') 


def events_view(request):
    events = Event.objects.all()
    
    context = {
        "events": events,
        "event_count": events.count()
    }
    return render(request, 'events/events_page.html', context) 


@login_required
def create_event_view(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user # Automatically logs who made it
            event.save()
            return redirect("events_page") # Bounces right back to the feed to view it!
    else:
        form = EventForm()
        
    return render(request, "events/create_event.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("events_page") 
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})