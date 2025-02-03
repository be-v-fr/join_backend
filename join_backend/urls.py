from django.contrib import admin
from django.urls import include, path

import users_app.urls
import contacts_app.urls
import tasks_app.urls

API_BASE_URL = 'api/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(API_BASE_URL + 'auth/', include(users_app.urls)),
    path(API_BASE_URL + 'contacts/', include(contacts_app.urls)),
    path(API_BASE_URL + 'tasks/', include(tasks_app.urls)),
]