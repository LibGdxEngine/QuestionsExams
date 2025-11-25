import random
import time
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from rest_framework import status, authentication, generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .serializers import *
from rest_framework import filters
from django.views.decorators.csrf import csrf_exempt
from .models import (
    QuestionAnswer,
    AnswerImage,
    TempQuestion,
    Question,
    TempAnswer,
    ExcelUpload,
)
import logging
from django.db.models import Count
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .tasks import process_excel_file, save_questions_task
from django.contrib.auth import get_user_model

User = get_user_model()


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

    def get_queryset(self):
        queryset = super().get_queryset()
        language_id = self.request.query_params.get("language")
        specificity_id = self.request.query_params.get("specificity")
        level_id = self.request.query_params.get("level")

        if language_id and specificity_id and level_id:
            queryset = queryset.filter(
                question__language_id=language_id,
                question__specificity_id=specificity_id,
                question__level_id=level_id,
            ).distinct()
        elif language_id or specificity_id or level_id:
            raise ValidationError(
                "Please provide all three query parameters: language, specificity, and level."
            )

        return queryset


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        language_id = self.request.query_params.get("language")
        specificity_id = self.request.query_params.get("specificity")
        level_id = self.request.query_params.get("level")

        if language_id and specificity_id and level_id:
            queryset = queryset.filter(
                question__language_id=language_id,
                question__specificity_id=specificity_id,
                question__level_id=level_id,
            ).distinct()
        elif language_id or specificity_id or level_id:
            raise ValidationError(
                "Please provide all three query parameters: language, specificity, and level."
            )

        return queryset


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        language_id = self.request.query_params.get("language")
        specificity_id = self.request.query_params.get("specificity")
        level_id = self.request.query_params.get("level")

        if language_id and specificity_id and level_id:
            queryset = queryset.filter(
                question__language_id=language_id,
                question__specificity_id=specificity_id,
                question__level_id=level_id,
            ).distinct()
        elif language_id or specificity_id or level_id:
            raise ValidationError(
                "Please provide all three query parameters: language, specificity, and level."
            )

        return queryset


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        language_id = self.request.query_params.get("language")
        specificity_id = self.request.query_params.get("specificity")
        level_id = self.request.query_params.get("level")

        if language_id and specificity_id and level_id:
            queryset = queryset.filter(
                question__language_id=language_id,
                question__specificity_id=specificity_id,
                question__level_id=level_id,
            ).distinct()
        elif language_id or specificity_id or level_id:
            raise ValidationError(
                "Please provide all three query parameters: language, specificity, and level."
            )

        return queryset


class QuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ExamsPagination(PageNumberPagination):
    page_size = 20


class ExamJourneyListCreateViewV2(ListAPIView):
    serializer_class = ExamJourneyListSerializerV2
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    pagination_class = ExamsPagination
    search_fields = [
        "type",
        "questions__text",
        "questions__language__name",
        "questions__specificity__name",
        "questions__level__name",
        "questions__correct_answer__answer",
    ]

    def get_queryset(self):
        # Filter ExamJourney objects by the logged-in user
        return ExamJourney.objects.filter(user=self.request.user)


class ExamJourneyUpdateView(UpdateAPIView):
    queryset = ExamJourney.objects.all()
    serializer_class = ExamJourneyUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ExamJourneyDetailViewV2(RetrieveUpdateDestroyAPIView):
    serializer_class = ExamJourneyDetailsSerializerV2
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Filter ExamJourney objects by the logged-in user
        return ExamJourney.objects.filter(user=self.request.user)


class ExamJourneyViewSet(viewsets.ModelViewSet):
    queryset = ExamJourney.objects.all()
    serializer_class = ExamJourneySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "type",
        "questions__text",
        "questions__language__name",
        "questions__specificity__name",
        "questions__level__name",
        "questions__correct_answer__answer",
    ]

    def get_queryset(self):
        # Filter ExamJourney objects by the logged-in user
        return ExamJourney.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Randomize the order of questions
        questions = data["questions"]
        random.shuffle(questions)
        data["questions"] = questions

        return Response(data)


class CreateExamJourneyAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        question_filter_serializer = QuestionFilterSerializer(data=request.data)
        
        if not question_filter_serializer.is_valid():
            return Response(
                question_filter_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare filters
        filters = Q()
        validated_data = question_filter_serializer.validated_data
        
        filter_mapping = {
            "language": "language_id",
            "specificity": "specificity_id", 
            "level": "level_id",
            "years": "years__id__in",
            "subjects": "subjects__id__in",
            "systems": "systems__id__in",
            "topics": "topics__id__in"
        }
        
        for key, filter_key in filter_mapping.items():
            if key in validated_data:
                filters &= Q(**{filter_key: validated_data[key]})
        
        # Fetch and validate questions
        number_of_questions = validated_data["number_of_questions"]
        selected_questions = list(Question.objects.filter(filters).distinct())
        
        if len(selected_questions) < number_of_questions:
            return Response(
                {"error": "Not enough questions available for the given filters"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Randomly select questions
        questions = random.sample(selected_questions, number_of_questions)
        
        # Prepare exam journey data
        journey_type = validated_data["type"]
        exam_journey_data = {
            "user": request.user.pk,
            "type": journey_type,
            "current_question": 0,
            "progress": {},
            "time_left": None,
            # Add question order during creation
            "question_order": [q.id for q in questions]
        }
        
        # Create exam journey with serializer
        exam_journey_serializer = ExamJourneySerializer(data=exam_journey_data)
        
        if not exam_journey_serializer.is_valid():
            return Response(
                exam_journey_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save exam journey
        exam_journey = exam_journey_serializer.save()
        
        # Add questions to the exam journey AFTER saving
        exam_journey.questions.set(questions)
        
        # Return the created exam journey using the detailed serializer
        return Response(
            ExamJourneyDetailsSerializerV2(exam_journey).data,
            status=status.HTTP_201_CREATED
        )
logger = logging.getLogger("core_apps.questions")


class UpdateExamJourneyAPIView(APIView):
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
    ]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def patch(self, request, pk, *args, **kwargs):
        exam_journey = get_object_or_404(ExamJourney, pk=pk, user=request.user)
        serializer = ExamJourneyUpdateSerializer(
            exam_journey, data=request.data, partial=True, context={"request": request}
        )
        print(exam_journey)
        if serializer.is_valid():
            progress_data = request.data.get("progress", {})
            # Prefer current_question_id, fall back to current_question_text for backward compatibility
            current_question_id = request.data.get("current_question_id")
            current_question_text = request.data.get("current_question_text")
            current_question_is_correct = None
            
            # Collect all question identifiers for bulk fetching
            question_ids_to_fetch = set()
            question_texts_to_fetch = []
            
            for question_id, question_status in progress_data.items():
                # Collect question IDs
                if "question_id" in question_status:
                    try:
                        question_ids_to_fetch.add(int(question_status["question_id"]))
                    except (ValueError, TypeError):
                        pass
                
                # Try using dict key as question_id
                try:
                    question_ids_to_fetch.add(int(question_id))
                except (ValueError, TypeError):
                    pass
                
                # Collect question texts for fallback
                if "question_text" in question_status:
                    question_texts_to_fetch.append(question_status["question_text"])
            
            # Bulk fetch all questions
            questions_by_id = {}
            questions_by_text = {}
            
            if question_ids_to_fetch:
                questions = Question.objects.filter(
                    id__in=question_ids_to_fetch
                ).select_related('correct_answer').prefetch_related('q_answers')
                questions_by_id = {q.id: q for q in questions}
            
            if question_texts_to_fetch:
                questions = Question.objects.filter(
                    text__in=question_texts_to_fetch
                ).select_related('correct_answer').prefetch_related('q_answers')
                for q in questions:
                    if q.text not in questions_by_text:
                        questions_by_text[q.text] = q
            
            # Process each question using bulk-fetched data
            for question_id, question_status in progress_data.items():
                try:
                    question = None
                    
                    # Try to get question by ID from question_status (preferred)
                    if "question_id" in question_status:
                        try:
                            q_id = int(question_status["question_id"])
                            question = questions_by_id.get(q_id)
                        except (ValueError, TypeError):
                            pass
                    
                    # If not found, try using the dict key as question_id
                    if question is None:
                        try:
                            q_id = int(question_id)
                            question = questions_by_id.get(q_id)
                        except (ValueError, TypeError):
                            pass
                    
                    # Fall back to text lookup for backward compatibility (deprecated)
                    if question is None:
                        if "question_text" in question_status:
                            question = questions_by_text.get(question_status["question_text"])
                            if question is None:
                                return Response(
                                    {
                                        "error": f'Question not found. Please provide "question_id" instead of "question_text" for question {question_id}.'
                                    },
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                        else:
                            return Response(
                                {
                                    "error": f'Missing question identifier. Please provide either "question_id" or "question_text" for question {question_id}.'
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    # If this is the current question, store its is_correct value
                    # Prefer ID comparison, fall back to text comparison for backward compatibility
                    is_current_question = False
                    if current_question_id is not None:
                        try:
                            current_id_int = int(current_question_id)
                            is_current_question = (question.id == current_id_int)
                        except (ValueError, TypeError):
                            pass
                    
                    if not is_current_question and current_question_text is not None:
                        # Fall back to text comparison for backward compatibility
                        question_text = question_status.get("question_text", question.text)
                        is_current_question = (question_text == current_question_text)
                    
                    if is_current_question:
                        # Get the answer index or text - use prefetched answers
                        answer_index = question_status.get("answer")
                        if isinstance(answer_index, int):
                            # If answer is an index
                            try:
                                answers_list = list(question.q_answers.all())
                                selected_answer = answers_list[answer_index]
                                current_question_is_correct = (selected_answer == question.correct_answer)
                            except (IndexError, AttributeError):
                                current_question_is_correct = False
                        else:
                            # If answer is text - use prefetched answers
                            selected_answer = None
                            for answer in question.q_answers.all():
                                if answer.answer_text == answer_index:
                                    selected_answer = answer
                                    break
                       
                            
                            if selected_answer:
                                current_question_is_correct = (selected_answer == question.correct_answer)
                            else:
                                current_question_is_correct = False

                except Exception as e:
                    return Response(
                        {"error": f"Error processing question: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            updated_instance = serializer.save()

            data = serializer.data
            if current_question_is_correct is not None:
                data["is_correct"] = current_question_is_correct
            else:
                logger.warning("current_question_is_correct is None")
                data["is_correct"] = None

            return Response(data, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=["post"])
    def add_question(self, request, pk=None):
        favorite_list = FavoriteList.objects.get(pkid=pk)
        question_id = get_object_or_404(request.data, "question_id")
        question = Question.objects.get(pk=question_id)
        favorite_list.questions.add(question)
        return Response({"status": "Question added to favorite list successfully"})

    @action(detail=True, methods=["post"])
    def remove_question(self, request, pk=None):
        favorite_list = FavoriteList.objects.get(pkid=pk)
        question_id = get_object_or_404(request.data, "question_id")
        question = Question.objects.get(id=question_id)
        favorite_list.questions.remove(question)
        return Response({"status": "Question removed from favorite list successfully"})


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
        
        # Apply basic filters (language, specificity, level, etc.)
        language = request.GET.get("language")
        if language:
            filters &= Q(language__id=language)
            
        specificity = request.GET.get("specificity")
        if specificity:
            filters &= Q(specificity__id=specificity)
            
        level = request.GET.get("level")
        if level:
            filters &= Q(level__id=level)
            
        years = request.GET.getlist("years")
        if years:
            try:
                years = [year for year in years[0].split(",")]
                filters &= Q(years__id__in=years)
            except ValueError:
                return Response(
                    {"error": "Invalid years format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
        subjects = request.GET.getlist("subjects")
        if subjects:
            subjects = [subject for subject in subjects[0].split(",")]
            filters &= Q(subjects__id__in=subjects)
            
        systems = request.GET.getlist("systems")
        if systems:
            systems = [system for system in systems[0].split(",")]
            filters &= Q(systems__id__in=systems)
            
        topics = request.GET.getlist("topics")
        if topics:
            topics = [topic for topic in topics[0].split(",")]
            filters &= Q(topics__id__in=topics)
            
        # Handle the new checkbox-based filtering
        user = request.user
        
        # Check if we should apply status filters
        apply_status_filters = request.GET.get("apply_status_filters") == "true"
        
        if apply_status_filters:
            # Get status filter values
            filter_used = request.GET.get("filter_used") == "true"
            filter_unused = request.GET.get("filter_unused") == "true"
            filter_correct = request.GET.get("filter_correct") == "true"
            filter_incorrect = request.GET.get("filter_incorrect") == "true"
            
             # Build a subquery for questions that have status objects
            questions_with_status = Question.objects.filter(userquestionstatus__user=user).distinct()
            
            # Handle used/unused filtering
            if filter_used and not filter_unused:
                # Only questions marked as used
                filters &= Q(userquestionstatus__user=user, userquestionstatus__is_used=True)
            elif filter_unused and not filter_used:
                # Questions explicitly marked as unused OR questions with no status at all
                filters &= ~Q(pk__in=questions_with_status.filter(userquestionstatus__is_used=True))
            elif filter_used and filter_unused:
                # Both checked means no filtering on is_used
                pass
            
            # Handle correct/incorrect filtering  
            if filter_correct and not filter_incorrect:
                # Only questions marked as correct
                filters &= Q(userquestionstatus__user=user, userquestionstatus__is_correct=True)
            elif filter_incorrect and not filter_correct:
                # Questions explicitly marked as incorrect OR questions with no status at all
                filters &= Q(userquestionstatus__user=user, userquestionstatus__is_correct=False)
            elif filter_correct and filter_incorrect:
                # Both checked means no filtering on is_correct
                pass
        
        count = Question.objects.filter(filters).distinct().count()
        return Response({"count": count}, status=status.HTTP_200_OK)

class QuestionSearchAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        search_term = self.request.GET.get("q", "").strip()
        if not search_term:
            return Question.objects.none()

        base_qs = (
            Question.objects
            .annotate(answer_count=Count("q_answers"))  # Count related answers
            .filter(correct_answer__isnull=False, answer_count__gt=0)  # Only include valid ones
        )

        return (
            base_qs.filter(
                Q(text__icontains=search_term)
                | Q(q_answers__answer_text__icontains=search_term)
                | Q(correct_answer__answer_text__icontains=search_term)
            )
            .distinct()
            .select_related("language", "specificity", "level", "correct_answer")
            .prefetch_related("years", "subjects", "systems", "topics", "q_answers")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search_term = request.GET.get("q", "").strip()
        results = []

        for question in queryset:
            match_source = []
            if search_term.lower() in question.text.lower():
                match_source.append("question_text")

            matched_answers = []
            all_answers = []
            for answer in question.q_answers.all():
                if search_term.lower() in answer.answer_text.lower():
                    answer_type = (
                        "correct_answer"
                        if answer == question.correct_answer
                        else "answer"
                    )
                    matched_answers.append(
                        {
                            "id": answer.id,
                            "text": answer.answer_text,
                            "type": answer_type,
                        }
                    )
                    match_source.append(answer_type)
                # Include in all answer options
                all_answers.append({"id": answer.id, "text": answer.answer_text})
            results.append(
                {
                    "id": question.id,
                    "text": question.text,
                    "match_source": list(set(match_source)),
                    "all_answers": all_answers,
                    "correct_answer": question.correct_answer.answer_text if question.correct_answer else None,
                    "matched_answers": matched_answers,
                    "language": question.language.name,
                    "specificity": question.specificity.name,
                    "level": question.level.name,
                    "years": [year.year for year in question.years.all()],
                    "subjects": [subject.name for subject in question.subjects.all()],
                    "systems": [system.name for system in question.systems.all()],
                    "topics": [topic.name for topic in question.topics.all()],
                }
            )

        return Response({"results": results})


class ReportView(CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the user from the request
        serializer.save(user=self.request.user)


@csrf_exempt
def add_answer(request):
    if request.method == "POST":
        logger.debug("POST data: %s", request.POST)
        answer_text = request.POST.get("answer_text")
        image = request.FILES.get("image")
        question_id = request.POST.get("question_id")
        try:
            question = Question.objects.get(id=question_id)
            question_answer = QuestionAnswer.objects.create(
                question=question, answer_text=answer_text, image=image
            )
            logger.debug("Answer added successfully for question ID %s", question_id)
            return JsonResponse(
                {"success": True, "message": "Answer added successfully!"}
            )
        except Question.DoesNotExist:
            logger.error("Question with ID %s not found", question_id)
            return JsonResponse({"success": False, "message": "Question not found."})
    logger.error("Invalid request method: %s", request.method)
    return JsonResponse({"success": False, "message": "Invalid request method."})


def upload_excel(request):
    if request.method == "POST" and request.FILES["file"]:
        excel_file = request.FILES["file"]
        excel_upload = ExcelUpload.objects.create(file=excel_file)

        # Trigger the Celery task
        process_excel_file.delay(excel_upload.id)

        return JsonResponse(
            {
                "success": True,
                "redirect_url": reverse(
                    "questions:upload_summary", args=[excel_upload.id]
                ),
            }
        )

    return render(request, "upload_excel.html")


def upload_summary(request, upload_id):
    excel_upload = get_object_or_404(ExcelUpload, id=upload_id)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if excel_upload.status != "complete":
            return JsonResponse({"upload_complete": False})
        else:
            return JsonResponse({"upload_complete": True})

    # Ensure that only questions related to this ExcelUpload are counted
    questions = excel_upload.temp_questions.all()
    total_questions = questions.count()
    total_answers = TempAnswer.objects.filter(
        question__excel_upload=excel_upload
    ).count()
    questions_without_answers = (
        questions.annotate(answer_count=Count("temp_answers"))
        .filter(answer_count=0)
        .count()
    )
    questions_with_correct_answers = (
        questions.filter(temp_answers__is_correct=True).distinct().count()
    )

    language_stats = dict(
        questions.values("language")
        .annotate(count=Count("id"))
        .values_list("language", "count")
    )
    specificity_stats = dict(
        questions.values("specificity")
        .annotate(count=Count("id"))
        .values_list("specificity", "count")
    )
    level_stats = dict(
        questions.values("level")
        .annotate(count=Count("id"))
        .values_list("level", "count")
    )
    year_stats = dict(
        questions.values("years")
        .annotate(count=Count("id"))
        .values_list("years", "count")
    )
    subject_stats = dict(
        questions.values("subjects")
        .annotate(count=Count("id"))
        .values_list("subjects", "count")
    )

    context = {
        "excel_upload": excel_upload,
        "total_questions": total_questions,
        "total_answers": total_answers,
        "questions_without_answers": questions_without_answers,
        "questions_with_correct_answers": questions_with_correct_answers,
        "unique_languages": list(language_stats.keys()),
        "unique_specificities": list(specificity_stats.keys()),
        "unique_levels": list(level_stats.keys()),
        "unique_years": list(year_stats.keys()),
        "unique_subjects": list(subject_stats.keys()),
        "language_stats": language_stats,
        "specificity_stats": specificity_stats,
        "level_stats": level_stats,
        "year_stats": year_stats,
        "subject_stats": subject_stats,
    }

    return render(request, "upload_summary.html", context)


def preview_questions(request, upload_id):
    excel_upload = get_object_or_404(ExcelUpload, id=upload_id)
    questions = excel_upload.temp_questions.all()

    # Get filter values
    selected_language = request.GET.get("language")
    selected_specificity = request.GET.get("specificity")
    selected_level = request.GET.get("level")
    has_answers = request.GET.get("has_answers")
    has_correct = request.GET.get("has_correct")

    # Apply filters, handling None/nan values
    if selected_language:
        questions = (
            questions.exclude(language__isnull=True)
            .exclude(language="nan")
            .filter(language=selected_language)
        )
    if selected_specificity:
        questions = (
            questions.exclude(specificity__isnull=True)
            .exclude(specificity="nan")
            .filter(specificity=selected_specificity)
        )
    if selected_level:
        questions = (
            questions.exclude(level__isnull=True)
            .exclude(level="nan")
            .filter(level=selected_level)
        )
    if has_answers == "yes":
        questions = questions.filter(temp_answers__isnull=False).distinct()
    elif has_answers == "no":
        questions = questions.filter(temp_answers__isnull=True)
    if has_correct == "yes":
        questions = questions.filter(temp_answers__is_correct=True).distinct()
    elif has_correct == "no":
        questions = questions.exclude(temp_answers__is_correct=True)

    # Get unique values for filters, excluding None and 'nan'
    languages = (
        questions.exclude(language__isnull=True)
        .exclude(language="nan")
        .values_list("language", flat=True)
        .distinct()
    )
    specificities = (
        questions.exclude(specificity__isnull=True)
        .exclude(specificity="nan")
        .values_list("specificity", flat=True)
        .distinct()
    )
    levels = (
        questions.exclude(level__isnull=True)
        .exclude(level="nan")
        .values_list("level", flat=True)
        .distinct()
    )

    # Page size handling
    page_size_options = [10, 25, 50, 100]
    page_size = int(request.GET.get("page_size", 10))
    if page_size not in page_size_options:
        page_size = 10

    # Pagination
    paginator = Paginator(questions, page_size)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    # Calculate page range with ellipsis
    show_adjacent = 2
    page_range = get_page_range(paginator, int(page_obj.number), show_adjacent)
    print(questions)
    # Count questions with non-null/non-nan values
    context = {
        "excel_upload": excel_upload,
        "questions": page_obj,
        "page_obj": page_obj,
        "page_range": page_range,
        "page_size": page_size,
        "page_size_options": page_size_options,
        "total_questions": questions.distinct().count(),
        # Filter options
        "languages": languages,
        "specificities": specificities,
        "levels": levels,
        "selected_language": selected_language,
        "selected_specificity": selected_specificity,
        "selected_level": selected_level,
        "has_answers": has_answers,
        "has_correct": has_correct,
        # Question counts excluding nan values
        "questions_with_answers_count": questions.filter(temp_answers__isnull=False)
        .distinct()
        .count(),
        "questions_with_language_count": questions.exclude(language__isnull=True)
        .exclude(language="nan")
        .count(),
        "questions_with_year_count": questions.exclude(years__isnull=True)
        .exclude(years="nan")
        .count(),
        "questions_with_specificity_count": questions.exclude(specificity__isnull=True)
        .exclude(specificity="nan")
        .count(),
        "questions_with_level_count": questions.exclude(level__isnull=True)
        .exclude(level="nan")
        .count(),
        "questions_with_system_count": questions.exclude(systems__isnull=True)
        .exclude(systems="nan")
        .count(),
        "questions_with_topic_count": questions.exclude(topics__isnull=True)
        .exclude(topics="nan")
        .count(),
    }

    return render(request, "preview_questions.html", context)


def get_page_range(paginator, current_page, adjacent_pages=2):
    """Helper function to calculate page range with ellipsis"""
    total_pages = paginator.num_pages

    # If total pages is small enough, show all pages
    if total_pages <= adjacent_pages * 2 + 5:
        return range(1, total_pages + 1)

    # Calculate range with ellipsis
    pages = []

    # Always include first page
    pages.append(1)

    # Calculate left range
    if current_page - adjacent_pages > 2:
        pages.append("...")
        start_range = current_page - adjacent_pages
    else:
        start_range = 2

    # Calculate right range
    if current_page + adjacent_pages < total_pages - 1:
        end_range = current_page + adjacent_pages + 1
        needs_end_ellipsis = True
    else:
        end_range = total_pages
        needs_end_ellipsis = False

    # Add the range around current page
    pages.extend(range(start_range, end_range))

    # Add end ellipsis if needed
    if needs_end_ellipsis:
        pages.append("...")
        pages.append(total_pages)
    elif end_range == total_pages - 1:
        pages.append(total_pages)

    return pages


def get_page_range(paginator, current_page, show_adjacent=2):
    """Helper function to calculate page range with ellipsis"""
    total_pages = paginator.num_pages

    # Always show first and last page
    page_range = []

    # Add first page
    page_range.append(1)

    # Add pages around current page
    for page_num in range(
        max(2, current_page - show_adjacent),
        min(total_pages, current_page + show_adjacent + 1),
    ):
        if page_range[-1] != page_num - 1:
            page_range.append("...")
        page_range.append(page_num)

    # Add last page
    if total_pages > 1 and page_range[-1] != total_pages:
        if page_range[-1] != total_pages - 1:
            page_range.append("...")
        page_range.append(total_pages)

    return page_range


def confirm_question(request, question_id):
    if request.method == "POST":
        temp_question = TempQuestion.objects.get(id=question_id)
        # Update temp_question with any changes from the form
        temp_question.text = request.POST.get("text")
        temp_question.language = request.POST.get("language")
        temp_question.specificity = request.POST.get("specificity")
        temp_question.level = request.POST.get("level")
        temp_question.is_confirmed = True
        temp_question.save()

        # Transfer to main model
        question = Question.objects.create(
            text=temp_question.text,
            language=temp_question.language,
            specificity=temp_question.specificity,
            level=temp_question.level,
        )

        # Handle answers
        for temp_answer in temp_question.temp_answers.all():
            temp_answer.text = request.POST.get(f"answer_{temp_answer.id}")
            temp_answer.is_correct = f"is_correct_{temp_answer.id}" in request.POST
            temp_answer.save()

            # Create QuestionAnswer with image
            question_answer = QuestionAnswer.objects.create(
                question=question,
                answer_text=temp_answer.text,
            )

            # Transfer image if exists
            if temp_answer.image:
                question_answer.image = temp_answer.image
                question_answer.save()

            # Set as correct answer if applicable
            if temp_answer.is_correct:
                question.correct_answer = question_answer
                question.save()

        # Delete the temp records
        temp_question.delete()

        return JsonResponse(
            {"success": True, "message": "Question and answers confirmed and saved."}
        )

    return JsonResponse({"success": False, "message": "Invalid request method."})


@csrf_exempt
def update_temp_question(request, question_id):
    if request.method == "POST":
        try:
            question = TempQuestion.objects.get(id=question_id)

            # Update question fields
            question.text = request.POST.get("text", question.text)
            question.language = request.POST.get("language", question.language)
            question.specificity = request.POST.get("specificity", question.specificity)
            question.level = request.POST.get("level", question.level)
            question.years = request.POST.get("years", question.years)
            question.hint = request.POST.get("hint", question.hint)
            question.video_hint = request.POST.get("video_hint", question.video_hint)
            question.save()

            # Update existing answers
            correct_answer = request.POST.get("correct_answer")

            # Handle existing answers
            for answer in question.temp_answers.all():
                answer_text = request.POST.get(f"answer_{answer.id}")
                answer_image = request.FILES.get(f"image_{answer.id}")

                if answer_text:
                    answer.text = answer_text
                    if answer_image:
                        answer.image = answer_image
                    answer.is_correct = str(answer.id) == correct_answer
                    answer.save()

            # Handle new answers
            for key in request.POST.keys():
                if key.startswith("new_answer_"):
                    new_answer_text = request.POST.get(key)
                    new_answer_image = request.FILES.get(
                        f"new_image_{key.split('_')[-1]}"
                    )

                    if new_answer_text.strip():  # Only create if there's actual text
                        new_answer = TempAnswer.objects.create(
                            question=question,
                            text=new_answer_text,
                            image=new_answer_image,
                            is_correct=(
                                correct_answer == key.replace("new_answer_", "new_")
                            ),
                        )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@csrf_exempt
def get_temp_question(request, question_id):
    try:
        question = TempQuestion.objects.get(id=question_id)
        answers = question.temp_answers.all()

        question_data = {
            "text": question.text,
            "language": question.language,
            "specificity": question.specificity,
            "level": question.level,
            "years": question.years,
            "hint": question.hint,
            "video_hint": question.video_hint,
        }

        answers_data = [
            {"id": answer.id, "text": answer.text, "is_correct": answer.is_correct}
            for answer in answers
        ]

        return JsonResponse(
            {"success": True, "question": question_data, "answers": answers_data}
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@csrf_exempt
def save_questions(request):
    if request.method == "POST":
        # Extract options from request
        with_answers = request.POST.get("withAnswers") == "on"
        with_language = request.POST.get("withLanguage") == "on"
        with_year = request.POST.get("withYear") == "on"
        with_specificity = request.POST.get("withSpecificity") == "on"
        with_level = request.POST.get("withLevel") == "on"
        with_system = request.POST.get("withSystem") == "on"
        with_topic = request.POST.get("withTopic") == "on"

        # Filter questions based on options
        questions = TempQuestion.objects.all()
        logger.debug(f"Total questions before filtering: {questions.count()}")

        if with_answers:
            questions = questions.filter(temp_answers__isnull=False).distinct()
        if with_language:
            questions = questions.filter(language__isnull=False).distinct()
        if with_year:
            questions = questions.filter(years__isnull=False).distinct()
        if with_specificity:
            questions = questions.filter(specificity__isnull=False).distinct()
        if with_level:
            questions = questions.filter(level__isnull=False).distinct()
        if with_system:
            questions = questions.filter(systems__isnull=False).distinct()
        if with_topic:
            questions = questions.filter(topics__isnull=False).distinct()

        logger.debug(f"Total questions after filtering: {questions.count()}")

        # Collect IDs of questions to be processed
        temp_question_ids = list(questions.values_list("id", flat=True))

        # Trigger the Celery task
        save_questions_task.delay(temp_question_ids)

        return JsonResponse(
            {
                "success": True,
                "message": "Questions are being saved in the background. {}",
                "total_questions": len(temp_question_ids),
            }
        )

    return JsonResponse({"success": False, "message": "Invalid request method."})


def reset_database(request):
    # Delete all data except for User
    Language.objects.all().delete()
    Specificity.objects.all().delete()
    Level.objects.all().delete()
    University.objects.all().delete()
    Year.objects.all().delete()
    Subject.objects.all().delete()
    System.objects.all().delete()
    Topic.objects.all().delete()
    QuestionAnswer.objects.all().delete()
    AnswerImage.objects.all().delete()
    Question.objects.all().delete()
    ExamJourney.objects.all().delete()
    Note.objects.all().delete()
    Report.objects.all().delete()
    UserQuestionStatus.objects.all().delete()
    ExcelUpload.objects.all().delete()
    TempQuestion.objects.all().delete()
    TempAnswer.objects.all().delete()
    Answer.objects.all().delete()

    # Redirect to a success page or home page
    return redirect("home")  # Change 'home' to your desired redirect URL name


def check_upload_status(request, upload_id):
    excel_upload = get_object_or_404(ExcelUpload, id=upload_id)
    return JsonResponse({"upload_complete": excel_upload.processed})


class HomePageAPIView(APIView):
    def get(self, request):
        home_page = HomePage.objects.first()  # Get the single homepage config
        faqs = FAQ.objects.all()  # Get all FAQs

        data = {
            "video_url": home_page.video_url if home_page else None,
            "faqs": FAQSerializer(faqs, many=True).data,
        }
        return Response(data)
