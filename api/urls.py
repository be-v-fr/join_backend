from django.urls import path
from api.views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/guest/', GuestLoginView.as_view(), name='login_guest'),
    path('register/', RegisterView.as_view(), name='register'),
    path('resetPassword/', ResetPassword.as_view(), name='reset_password'),
    path('resetPassword/request/', RequestPasswordReset.as_view(), name='request_password_reset'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TasksView.as_view(), name='task'),
    path('tasks/stream/', tasks_stream, name='tasks_stream'),
    path('subtasks/', SubtasksView.as_view(), name='subtasks'),
    path('subtasks/<int:pk>/', SubtasksView.as_view(), name='subtask'),
    path('subtasks/stream/', subtasks_stream, name='subtasks_stream'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/current/', CurrentUserView.as_view(), name='users_current'),
    path('users/stream/', users_stream, name='users_stream'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', ContactsView.as_view(), name='contact'),
]