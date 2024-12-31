from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LanguageViewSet,
    SpecificityViewSet,
    LevelViewSet,
    YearViewSet,
    SubjectViewSet,
    SystemViewSet,
    TopicViewSet,
    QuestionAnswerViewSet,
    QuestionViewSet,
    FavoriteListViewSet,
    ExamJourneyViewSet,
    CreateExamJourneyAPIView,
    UpdateExamJourneyAPIView,
    NoteViewSet,
    QuestionSearchView,
    ReportView,
    QuestionCountView,
    UniversityViewSet,
    ExamJourneyListCreateViewV2,
    add_answer,
)

app_name = "questions"
router = DefaultRouter()
router.register(r"languages", LanguageViewSet)
router.register(r"specificities", SpecificityViewSet)
router.register(r"levels", LevelViewSet)
router.register(r"years", YearViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"systems", SystemViewSet)
router.register(r"topics", TopicViewSet)
router.register(r"question-answers", QuestionAnswerViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"favorites", FavoriteListViewSet)
router.register(r"notes", NoteViewSet)
router.register(r"university", UniversityViewSet)
# router.register(r'reports', ReportViewSet)
router.register(r"exam-journeys", ExamJourneyViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "create-exam-journey/",
        CreateExamJourneyAPIView.as_view(),
        name="create-exam-journey",
    ),
    path(
        "update-exam-journey/<int:pk>/",
        UpdateExamJourneyAPIView.as_view(),
        name="update-exam-journey",
    ),
    path("search/", QuestionSearchView.as_view(), name="search_questions"),
    path("reports/", ReportView.as_view(), name="search_questions"),
    path("count/", QuestionCountView.as_view(), name="question-count"),
    path("add-answer2/", add_answer, name="add_answer"),
]
