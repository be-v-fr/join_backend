from django.contrib import admin

from api.models import Task, Subtask 

# Register your models here.
admin.site.register(Task)
admin.site.register(Subtask)