from django.urls import path
from .views import TasksView, SubtasksView, tasks_stream, subtasks_stream

SUBTASKS_URL = 'subtasks/'

urlpatterns = [
    path('', TasksView.as_view(), name='tasks'),
    path('<int:pk>/', TasksView.as_view(), name='task'),
    path('stream/', tasks_stream, name='tasks_stream'),
    path(SUBTASKS_URL, SubtasksView.as_view(), name='subtasks'),
    path(SUBTASKS_URL + '<int:pk>/', SubtasksView.as_view(), name='subtask'),
    path(SUBTASKS_URL + 'stream/', subtasks_stream, name='subtasks_stream'),
]