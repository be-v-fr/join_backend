from django.urls import path
from .views import ContactsView

urlpatterns = [
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', ContactsView.as_view(), name='contact'),
]