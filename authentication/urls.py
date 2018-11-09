from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view),
    path('register/', views.register),
    path('logout/', views.logout_view)
]
