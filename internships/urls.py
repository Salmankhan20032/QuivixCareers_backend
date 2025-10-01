# internships/urls.py

from django.urls import path
from .views import (
    InternshipListView, InternshipDetailView, ApplyInternshipView,
    MyInternshipsView, SubmitInternshipView, UpdateInternshipProgressView # <-- IMPORT the new view
)

urlpatterns = [
    path('', InternshipListView.as_view(), name='internship-list'),
    path('<int:pk>/', InternshipDetailView.as_view(), name='internship-detail'),
    path('<int:pk>/apply/', ApplyInternshipView.as_view(), name='internship-apply'),
    path('my-internships/', MyInternshipsView.as_view(), name='my-internships'),
    # --- ADD THIS NEW URL PATTERN, MY LOVE! ---
    path('my-internships/<int:pk>/progress/', UpdateInternshipProgressView.as_view(), name='internship-progress-update'),
    path('my-internships/<int:pk>/submit/', SubmitInternshipView.as_view(), name='internship-submit'),
]