import random

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from rest_framework import status, authentication
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .serializers import *
from rest_framework import filters


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


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
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
    permission_classes = [IsAuthenticatedOrReadOnly]

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
            selected_questions = Question.objects.filter(**filters)
            questions = selected_questions[:number_of_questions]

            if questions.count() < number_of_questions:
                return Response({'error': 'Not enough questions available for the given filters'},
                                status=status.HTTP_400_BAD_REQUEST)
            # Extract the type field from the validated data
            journey_type = question_filter_serializer.validated_data['type']

            exam_journey_data = {
                'user': request.user.pk,  # Assuming you have user authentication
                'type': journey_type,  # Use the extracted type value
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
    permission_classes = [IsAuthenticatedOrReadOnly]

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

    def perform_create(self, serializer):
        # Set the user field to the logged-in user
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Filter ExamJourney objects by the logged-in user
        return FavoriteList.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        favorite_list = FavoriteList.objects.get(pkid=pk)
        question_id = get_object_or_404(request.data, 'question_id')
        question = Question.objects.get(pk=question_id)
        favorite_list.questions.add(question)
        return Response({'status': 'Question added to favorite list successfully'})

    @action(detail=True, methods=['post'])
    def remove_question(self, request, pk=None):
        favorite_list = FavoriteList.objects.get(pkid=pk)
        question_id = get_object_or_404(request.data, 'question_id')
        question = Question.objects.get(id=question_id)
        favorite_list.questions.remove(question)
        return Response({'status': 'Question removed from favorite list successfully'})


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionCountView(APIView):
    def get(self, request, *args, **kwargs):
        filters = Q()

        language = request.GET.get('language')
        if language:
            filters &= Q(language__id=language)

        specificity = request.GET.get('specificity')
        if specificity:
            filters &= Q(specificity__id=specificity)

        level = request.GET.get('level')
        if level:
            filters &= Q(level__id=level)

        years = request.GET.getlist('years')
        if years:
            filters &= Q(years__id__in=years)

        subjects = request.GET.getlist('subjects')
        if subjects:
            filters &= Q(subjects__id__in=subjects)

        systems = request.GET.getlist('systems')
        if systems:
            filters &= Q(systems__id__in=systems)

        topics = request.GET.getlist('topics')
        if topics:
            filters &= Q(topics__id__in=topics)

        is_used = request.GET.get('is_used')
        if is_used is not None:
            filters &= Q(is_used=is_used)

        is_correct = request.GET.get('is_correct')
        if is_correct is not None:
            filters &= Q(is_correct=is_correct)

        count = Question.objects.filter(filters).distinct().count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class QuestionSearchView(ListView):
    model = Question
    context_object_name = 'questions'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        search_term = self.request.GET.get('q', '')
        if search_term:
            queryset = Question.objects.filter(
                Q(text__icontains=search_term) |
                Q(answers__answer__icontains=search_term)
            ).distinct()
        else:
            queryset = Question.objects.none()
        return queryset

    def render_to_response(self, context, **response_kwargs):
        questions = context['questions']
        results = []
        for question in questions:
            results.append({
                'id': question.id,
                'text': question.text,
                'hint': question.hint,
                'video_hint': question.video_hint,
                'is_used': question.is_used,
                'is_correct': question.is_correct,
                'answers': list(question.answers.values('id', 'answer')),
                'correct_answer': str(question.correct_answer),
                'language': question.language.name,
                'specificity': question.specificity.name,
                'level': question.level.name,
                'years': [year.year for year in question.years.all()],
                'subjects': [subject.name for subject in question.subjects.all()],
                'systems': [system.name for system in question.systems.all()],
                'topics': [topic.name for topic in question.topics.all()],

            })
        return JsonResponse({'results': results})


class ReportView(CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the user from the request
        serializer.save(user=self.request.user)
