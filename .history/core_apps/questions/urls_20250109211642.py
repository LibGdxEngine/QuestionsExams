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
    upload_excel,
    preview_questions,
    confirm_question,
    upload_summary,
    update_temp_question,
    get_temp_question,
    save_questions,
    reset_database,
    check_upload_status,
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
    path("add-answer/", add_answer, name="add_answer"),
    path("upload-excel/", upload_excel, name="upload_excel"),
    path("upload-summary/<int:upload_id>/", upload_summary, name="upload_summary"),
    path(
        "preview-questions/<int:upload_id>/",
        preview_questions,
        name="preview_questions",
    ),
    path(
        "confirm-question/<int:question_id>/", confirm_question, name="confirm_question"
    ),
    path(
        "update-temp-question/<int:question_id>/",
        update_temp_question,
        name="update_temp_question",
    ),
    path(
        "get-temp-question/<int:question_id>/",
        get_temp_question,
        name="get_temp_question",
    ),
    path("save-questions/", save_questions, name="save_questions"),
    path("reset-database/", reset_database, name="reset_database"),
    path(
        "check-upload-status/<int:upload_id>/",
        check_upload_status,
        name="check_upload_status",
    ),
]
