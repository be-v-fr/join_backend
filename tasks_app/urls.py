from django.urls import path
from .views import TasksView, SubtasksView, tasks_stream, subtasks_stream

urlpatterns = [
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TasksView.as_view(), name='task'),
    path('tasks/stream/', tasks_stream, name='tasks_stream'),
    path('subtasks/', SubtasksView.as_view(), name='subtasks'),
    path('subtasks/<int:pk>/', SubtasksView.as_view(), name='subtask'),
    path('subtasks/stream/', subtasks_stream, name='subtasks_stream'),
]