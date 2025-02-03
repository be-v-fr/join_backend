from django.contrib import admin
from .models import AccountActivation, PasswordReset, AppUser

admin.site.register(AccountActivation)
admin.site.register(PasswordReset)
admin.site.register(AppUser)
