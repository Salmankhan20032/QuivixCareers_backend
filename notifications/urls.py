# notifications/urls.py
from django.urls import path
from .views import NotificationListView, MarkAllAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('mark-all-read/', MarkAllAsReadView.as_view(), name='mark-all-read'),
]