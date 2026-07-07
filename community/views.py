from django.shortcuts import render, redirect
from .models import Event
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def home_view(request):
    events = Event.objects.all()

    context = {
        "events": events,
        "event_count": events.count()
    }
    return render(request, 'home/home.html', context)


def register_view (request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})

