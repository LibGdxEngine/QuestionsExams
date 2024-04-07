from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'languages', LanguageViewSet)
router.register(r'specificities', SpecificityViewSet)
router.register(r'levels', LevelViewSet)
router.register(r'years', YearViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'systems', SystemViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'question-answers', QuestionAnswerViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'exam-journeys', ExamJourneyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
