from django.urls import path
from .views import ExamJourneyListCreateViewV2

urlpatterns = [
    path('exam-journeys/<int:pk>/', ExamJourneyListCreateViewV2.as_view(), name='exam-journey-detail'),
]