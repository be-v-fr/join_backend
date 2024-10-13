from django.contrib import admin
from api.models import AppUser, PasswordReset, Task, Subtask, CustomContact 

admin.site.register(AppUser)
admin.site.register(PasswordReset)
admin.site.register(Task)
admin.site.register(Subtask)
admin.site.register(CustomContact)