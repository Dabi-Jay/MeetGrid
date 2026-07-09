from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import EventForm
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST


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
            event.created_by = request.user 
            event.save()
            return redirect("events_page") 
    else:
        form = EventForm()
        
    return render(request, "events/create_event.html", {"form": form})


def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def toggle_join_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
    else:
        event.attendees.add(request.user)
        
    return redirect(request.META.get('HTTP_REFERER', 'event_detail'))


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

@login_required
def profile_view(request):
    active_tab = request.GET.get('tab', 'attending')
    
    if active_tab == 'hosting':
        events = Event.objects.filter(created_by=request.user)
        tab_title = "Hosted Events"
    else:
        events = Event.objects.filter(attendees=request.user)
        tab_title = "Attending Events"
        
    context = {
        'events': events,
        'active_tab': active_tab,
        'tab_title': tab_title,
        'event_count': events.count()
    }
    return render(request, 'registration/profile.html', context)


@login_required
def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.created_by != request.user:
        return HttpResponseForbidden("You do not have permission to edit this event.")
        
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            
            return redirect(f"{reverse('profile')}?tab=hosting")
    else:
        form = EventForm(instance=event)
        
    context = {
        'form': form,
        'event': event,
        'is_edit': True 
    }
    return render(request, 'events/create_event.html', context)


@login_required
def delete_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.created_by != request.user:
        return HttpResponseForbidden("You do not have permission to delete this event.")
        
    event.delete()
    
    return redirect(f"{reverse('profile')}?tab=hosting")