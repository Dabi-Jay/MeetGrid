from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

# Create your models here.
class Event(models.Model):
    class Category(models.TextChoices):
        SPORTS = "SPORT", "Sports"
        TECH = "TECH", "Tech"
        EDUCATION = "EDU", "Education"
        TOWN_PLANNING = "PLAN", "Town Planning"


    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=5, choices= Category.choices, default=Category.TOWN_PLANNING)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    attendees = models.ManyToManyField(User, related_name="attending_events", blank=True)
    @property
    def is_past(self):
        """Returns True if the event date and time have passed."""
        event_datetime = datetime.datetime.combine(self.date, self.time)
        if timezone.is_aware(timezone.now()):
            event_datetime = timezone.make_aware(event_datetime, timezone.get_current_timezone())
        return event_datetime < timezone.now()

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return self.title