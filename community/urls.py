from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.home_view, name= "home"),
    path('events/', views.events_view, name='events_page'),
    path('events/create/', views.create_event_view, name='create_event'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
]