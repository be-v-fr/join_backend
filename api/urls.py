from django.urls import include, path
from api.views import *


urlpatterns = [
    path('login', LoginView.as_view()),
    path('login/guest', GuestLoginView.as_view()),
    path('register', RegisterView.as_view()),
    path('tasks', TasksView.as_view()),
    path('tasks/<int:pk>', TasksView.as_view()),
    path('tasks/stream/', tasks_stream, name='tasks_stream'),
    path('subtasks', SubtasksView.as_view()),
    path('subtasks/<int:pk>', SubtasksView.as_view()),
    path('subtasks/stream/', subtasks_stream, name='subtasks_stream'),
    path('users', UsersView.as_view()),
    path('users/current', CurrentUserView.as_view()),
    path('users/stream/', users_stream, name='users_stream'),
    path('contacts', ContactsView.as_view()),
    path('contacts/<int:pk>', ContactsView.as_view()),
]