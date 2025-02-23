from django.urls import path
from .views import ExamJourneyListCreateViewV2, ExamJourneyDetailViewV2, ExamJourneyUpdateView

urlpatterns = [
    path('exam-journeys/', ExamJourneyListCreateViewV2.as_view(), name='exam-journey-list'),
    path('exam-journeys/<int:pk>/', ExamJourneyDetailViewV2.as_view(), name='exam-journey-detail'),
    path('exam-journeys/<int:pk>/update/', ExamJourneyUpdateView.as_view(), name='exam-journey-update'),
]