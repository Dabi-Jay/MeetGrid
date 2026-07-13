from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import EventForm
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages


def home_view(request):
    return render(request, 'home/home.html') 


def events_view(request):
    events = Event.objects.all().order_by('date')
    
    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_timeframe = request.GET.get('timeframe', 'anytime').strip()

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | 
            Q(location__icontains=search_query)
        )

    if selected_category and selected_category != 'all':
        events = events.filter(category=selected_category)

    today = timezone.now().date()
    if selected_timeframe == 'today':
        events = events.filter(date=today)
    elif selected_timeframe == 'this_week':
        next_week = today + timedelta(days=7)
        events = events.filter(date__range=[today, next_week])

    context = {
        'events': events,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_timeframe': selected_timeframe,
        'event_count': events.count(),
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
            messages.success(request, f"Event '{event.title}' has been successfully created!")
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
        messages.success(request, f"You have left the event: '{event.title}'.")
    else:
        event.attendees.add(request.user)
        messages.success(request, f"Success! You are now registered for '{event.title}'.")
        
    return redirect(request.META.get('HTTP_REFERER', 'event_detail'))


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MeetGrid, {user.username}! Your account was created successfully.")
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
        messages.error(request, "You do not have permission to edit this event.")
        return HttpResponseForbidden("You do not have permission to edit this event.")
        
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Changes to '{event.title}' have been saved.")
            
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
        messages.error(request, "You do not have permission to delete this event.")
        return HttpResponseForbidden("You do not have permission to delete this event.")
        
    event.delete()
    messages.success(request, f"The event '{event.title}' was permanently deleted.")
    
    return redirect(f"{reverse('profile')}?tab=hosting")