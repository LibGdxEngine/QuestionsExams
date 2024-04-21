from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework import filters


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]


class SpecificityViewSet(viewsets.ModelViewSet):
    queryset = Specificity.objects.all()
    serializer_class = SpecificitySerializer
    permission_classes = [IsAuthenticated]


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


class YearViewSet(viewsets.ModelViewSet):
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [IsAuthenticated]


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]


class QuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer
    permission_classes = [IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class ExamJourneyViewSet(viewsets.ModelViewSet):
    queryset = ExamJourney.objects.all()
    serializer_class = ExamJourneySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'type',
        'questions__text',
        'questions__language__name',
        'questions__specificity__name',
        'questions__level__name',
        'questions__correct_answer__answer'
    ]

    def get_queryset(self):
        # Filter ExamJourney objects by the logged-in user
        return ExamJourney.objects.filter(user=self.request.user)


class FavoriteListViewSet(viewsets.ModelViewSet):
    queryset = FavoriteList.objects.all()
    serializer_class = FavoriteListSerializer

    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        favorite_list = FavoriteList.objects.get(id=pk)
        question_id = request.data.get('question_id')
        question = Question.objects.get(pk=question_id)
        favorite_list.questions.add(question)
        return Response({'status': 'Question added to favorite list successfully'})

    @action(detail=True, methods=['post'])
    def remove_question(self, request, pk=None):
        favorite_list = FavoriteList.objects.get(id=pk)
        question_id = request.data.get('question_id')
        question = Question.objects.get(id=question_id)
        favorite_list.questions.remove(question)
        return Response({'status': 'Question removed from favorite list successfully'})