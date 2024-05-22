from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, authentication
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .serializers import ExamJourneySerializer, QuestionFilterSerializer
from .serializers import *
from rest_framework import filters

from ..articles import permissions


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SpecificityViewSet(viewsets.ModelViewSet):
    queryset = Specificity.objects.all()
    serializer_class = SpecificitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class YearViewSet(viewsets.ModelViewSet):
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ExamJourneyViewSet(viewsets.ModelViewSet):
    queryset = ExamJourney.objects.all()
    serializer_class = ExamJourneySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
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


class CreateExamJourneyAPIView(APIView):
    permission_classes = [permissions.ReadOnly]
    def post(self, request, *args, **kwargs):
        question_filter_serializer = QuestionFilterSerializer(data=request.data)

        if question_filter_serializer.is_valid():
            filters = {}
            if 'language' in question_filter_serializer.validated_data:
                filters['language_id'] = question_filter_serializer.validated_data['language']
            if 'specificity' in question_filter_serializer.validated_data:
                filters['specificity_id'] = question_filter_serializer.validated_data['specificity']
            if 'level' in question_filter_serializer.validated_data:
                filters['level_id'] = question_filter_serializer.validated_data['level']
            if 'years' in question_filter_serializer.validated_data:
                filters['years__id__in'] = question_filter_serializer.validated_data['years']
            if 'subjects' in question_filter_serializer.validated_data:
                filters['subjects__id__in'] = question_filter_serializer.validated_data['subjects']
            if 'systems' in question_filter_serializer.validated_data:
                filters['systems__id__in'] = question_filter_serializer.validated_data['systems']
            if 'topics' in question_filter_serializer.validated_data:
                filters['topics__id__in'] = question_filter_serializer.validated_data['topics']

            number_of_questions = question_filter_serializer.validated_data['number_of_questions']
            questions = Question.objects.filter(**filters)[:number_of_questions]

            if questions.count() < number_of_questions:
                return Response({'error': 'Not enough questions available for the given filters'},
                                status=status.HTTP_400_BAD_REQUEST)
            exam_journey_data = {
                'user': request.user.pk,  # Assuming you have user authentication
                'type': 'exam',  # Or 'study', based on your requirement
                'questions': [question.id for question in questions],
                'current_question': 0,
                'progress': {},
                'time_left': None,
            }

            exam_journey_serializer = ExamJourneySerializer(data=exam_journey_data)
            if exam_journey_serializer.is_valid():
                exam_journey = exam_journey_serializer.save()
                exam_journey.questions.set(questions)
                return Response(ExamJourneySerializer(exam_journey).data, status=status.HTTP_201_CREATED)

            return Response(exam_journey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(question_filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateExamJourneyAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsOwnerOrReadOnly]

    def patch(self, request, pk, *args, **kwargs):
        exam_journey = get_object_or_404(ExamJourney, pk=pk, user=request.user)
        serializer = ExamJourneyUpdateSerializer(exam_journey, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FavoriteListViewSet(viewsets.ModelViewSet):
    queryset = FavoriteList.objects.all()
    serializer_class = FavoriteListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
