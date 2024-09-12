"""
URL configuration for join_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.asView(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from api.views import LoginView, RegisterView, SubtasksView, TasksView, UsersView, ContactsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login', LoginView.as_view()),
    path('api/register', RegisterView.as_view()),
    path('api/tasks', TasksView.as_view()),
    path('api/subtasks', SubtasksView.as_view()),
    path('api/users', UsersView.as_view()),
    path('api/contacts', ContactsView.as_view()),
]