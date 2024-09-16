from django.urls import path

from api.views import LoginView, RegisterView, SubtasksView, TasksView, UsersView, CurrentUserView, ContactsView

urlpatterns = [
    path('login', LoginView.as_view()),
    path('register', RegisterView.as_view()),
    path('tasks', TasksView.as_view()),
    path('tasks/<int:pk>', TasksView.as_view()),
    path('subtasks', SubtasksView.as_view()),
    path('subtasks/<int:pk>', SubtasksView.as_view()),
    path('users', UsersView.as_view()),
    path('users/current', CurrentUserView.as_view()),
    path('contacts', ContactsView.as_view()),
    path('contacts/<int:pk>', ContactsView.as_view()),
]