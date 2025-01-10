import random
import time
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from rest_framework import status, authentication
from rest_framework.generics import CreateAPIView, ListAPIView
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
import pandas as pd
from django.db.models import Count
from collections import Counter
from django.urls import reverse
from django.core.paginator import Paginator
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


class ExamJourneyListCreateViewV2(ListAPIView):
    serializer_class = ExamJourneySerializerV2
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

        if question_filter_serializer.is_valid():
            filters = Q()

            # Apply filters based on the input data
            if "language" in question_filter_serializer.validated_data:
                filters &= Q(
                    language_id=question_filter_serializer.validated_data["language"]
                )
            if "specificity" in question_filter_serializer.validated_data:
                filters &= Q(
                    specificity_id=question_filter_serializer.validated_data[
                        "specificity"
                    ]
                )
            if "level" in question_filter_serializer.validated_data:
                filters &= Q(
                    level_id=question_filter_serializer.validated_data["level"]
                )
            if "years" in question_filter_serializer.validated_data:
                filters &= Q(
                    years__id__in=question_filter_serializer.validated_data["years"]
                )
            if "subjects" in question_filter_serializer.validated_data:
                filters &= Q(
                    subjects__id__in=question_filter_serializer.validated_data[
                        "subjects"
                    ]
                )
            if "systems" in question_filter_serializer.validated_data:
                filters &= Q(
                    systems__id__in=question_filter_serializer.validated_data["systems"]
                )
            if "topics" in question_filter_serializer.validated_data:
                filters &= Q(
                    topics__id__in=question_filter_serializer.validated_data["topics"]
                )

            # Filter based on is_used and is_correct fields
            user = request.user
            is_used = question_filter_serializer.validated_data.get("is_used")
            if is_used is not None:
                filters &= Q(
                    userquestionstatus__user=user, userquestionstatus__is_used=is_used
                )

            # Filter based on is_correct only if explicitly provided
            is_correct = question_filter_serializer.validated_data.get("is_correct")
            if is_correct is not None:
                filters &= Q(
                    userquestionstatus__user=user,
                    userquestionstatus__is_correct=is_correct,
                )

            number_of_questions = question_filter_serializer.validated_data[
                "number_of_questions"
            ]
            selected_questions = list(Question.objects.filter(filters).distinct())
            questions = selected_questions[:number_of_questions]

            if len(questions) < number_of_questions:
                return Response(
                    {"error": "Not enough questions available for the given filters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Randomize the order of the questions
            random.seed(time.time())
            # Use random.sample to create a new shuffled list
            shuffled_questions = random.sample(questions, len(questions))

            # Extract the type field from the validated data
            journey_type = question_filter_serializer.validated_data["type"]

            exam_journey_data = {
                "user": request.user.pk,
                "type": journey_type,
                "questions": [question.id for question in shuffled_questions],
                "current_question": 0,
                "progress": {},
                "time_left": None,
            }

            exam_journey_serializer = ExamJourneySerializer(data=exam_journey_data)
            if exam_journey_serializer.is_valid():
                exam_journey = exam_journey_serializer.save()
                exam_journey.questions.set(questions)
                return Response(
                    ExamJourneySerializer(exam_journey).data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                exam_journey_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            question_filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST
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

        if serializer.is_valid():
            progress_data = request.data.get("progress", {})
            current_question_text = request.data.get("current_question_text")
            current_question_is_correct = None

            logger.info(f"Current question text: {current_question_text}")
            logger.info(f"Progress data: {progress_data}")

            for question_id, question_status in progress_data.items():
                try:
                    question = Question.objects.get(
                        text=question_status["question_text"]
                    )
                    user_question_status, created = (
                        UserQuestionStatus.objects.get_or_create(
                            user=request.user,
                            question=question,
                            defaults={"is_used": True},
                        )
                    )

                    user_question_status.is_used = True
                    user_question_status.is_correct = (
                        question.q_answers.all()[question_status["answer"]]
                        == question.correct_answer
                    )
                    user_question_status.save()

                    logger.info(
                        f"Question: {question_status['question_text']}, Is correct: {user_question_status.is_correct}"
                    )

                    # If this is the current question, store its is_correct value
                    if question_status["question_text"] == current_question_text:
                        current_question_is_correct = user_question_status.is_correct
                        logger.info(
                            f"Current question is_correct: {current_question_is_correct}"
                        )

                except Question.DoesNotExist:
                    logger.error(
                        f'Question with text "{question_status["question_text"]}" not found.'
                    )
                    return Response(
                        {
                            "error": f'Question with text "{question_status["question_text"]}" not found.'
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing question {question_status['question_text']}: {str(e)}"
                    )
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

            logger.info(f"Final response data: {data}")

            return Response(data, status=status.HTTP_200_OK)

        logger.error(f"Serializer errors: {serializer.errors}")
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
            # Ensure all values are integers
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

        # Filtering based on user-specific question status
        user = request.user

        # Filter questions by 'is_used' for the specific user
        is_used = request.GET.get("is_used")
        if is_used in ["True", "False"]:
            is_used_filter = Q(
                userquestionstatus__user=user,
                userquestionstatus__is_used=is_used == "True",
            )
            filters &= is_used_filter

        # Filter questions by 'is_correct' for the specific user
        is_correct = request.GET.get("is_correct")
        if is_correct in ["True", "False"]:
            is_correct_filter = Q(
                userquestionstatus__user=user,
                userquestionstatus__is_correct=is_correct == "True",
            )
            filters &= is_correct_filter
        count = Question.objects.filter(filters).distinct().count()
        return Response({"count": count}, status=status.HTTP_200_OK)


class QuestionSearchView(ListView):
    model = Question
    context_object_name = "questions"
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        search_term = self.request.GET.get("q", "")
        if search_term:
            queryset = Question.objects.filter(
                Q(text__icontains=search_term)
                | Q(q_answers__answer__icontains=search_term)
            ).distinct()
        else:
            queryset = Question.objects.none()
        return queryset

    def render_to_response(self, context, **response_kwargs):
        questions = context["questions"]
        results = []
        for question in questions:
            results.append(
                {
                    "id": question.id,
                    "text": question.text,
                    "hint": question.hint,
                    "video_hint": question.video_hint,
                    "is_used": question.is_used,
                    "is_correct": question.is_correct,
                    "answers": list(question.q_answers.values("id", "answer")),
                    "correct_answer": str(question.correct_answer),
                    "language": question.language.name,
                    "specificity": question.specificity.name,
                    "level": question.level.name,
                    "years": [year.year for year in question.years.all()],
                    "subjects": [subject.name for subject in question.subjects.all()],
                    "systems": [system.name for system in question.systems.all()],
                    "topics": [topic.name for topic in question.topics.all()],
                }
            )
        return JsonResponse({"results": results})


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
    logger.debug("add_answer view called")
    if request.method == "POST":
        logger.debug("POST data: %s", request.POST)
        answer_text = request.POST.get("answer_text")
        images = request.FILES.getlist("images")
        question_id = request.POST.get("question_id")
        try:
            question = Question.objects.get(id=question_id)
            question_answer = QuestionAnswer.objects.create(
                question=question, answer_text=answer_text
            )
            for image in images:
                AnswerImage.objects.create(question_answer=question_answer, image=image)
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

    # Get filter options from request
    with_answers = request.GET.get("withAnswers") == "on"
    with_language = request.GET.get("withLanguage") == "on"
    with_year = request.GET.get("withYear") == "on"
    with_specificity = request.GET.get("withSpecificity") == "on"
    with_level = request.GET.get("withLevel") == "on"
    with_system = request.GET.get("withSystem") == "on"
    with_topic = request.GET.get("withTopic") == "on"

    # Apply filters based on checkbox selections
    if with_answers:
        questions = questions.filter(temp_answers__isnull=False)
    if with_language:
        questions = questions.filter(language__isnull=False)
    if with_year:
        questions = questions.filter(years__isnull=False)
    if with_specificity:
        questions = questions.filter(specificity__isnull=False)
    if with_level:
        questions = questions.filter(level__isnull=False)
    if with_system:
        questions = questions.filter(systems__isnull=False)
    if with_topic:
        questions = questions.filter(topics__isnull=False)

    # Pagination
    paginator = Paginator(questions, 10)  # Example page size
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "excel_upload": excel_upload,
        "questions": page_obj,
        "questions_with_answers_count": questions.filter(temp_answers__isnull=False).count(),
        "questions_with_language_count": questions.filter(language__isnull=False).count(),
        "questions_with_year_count": questions.filter(years__isnull=False).count(),
        "questions_with_specificity_count": questions.filter(specificity__isnull=False).count(),
        "questions_with_level_count": questions.filter(level__isnull=False).count(),
        "questions_with_system_count": questions.filter(systems__isnull=False).count(),
        "questions_with_topic_count": questions.filter(topics__isnull=False).count(),
        # Add other context variables as needed
    }

    return render(request, "preview_questions.html", context)


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
            temp_answer.is_correct = "is_correct_{temp_answer.id}" in request.POST
            temp_answer.save()

            TempAnswer.objects.create(
                question=question,
                text=temp_answer.text,
                is_correct=temp_answer.is_correct,
            )

        # Optionally delete the temp records
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
                if answer_text:
                    answer.text = answer_text
                    answer.is_correct = str(answer.id) == correct_answer
                    answer.save()

            # Handle new answers
            for key in request.POST.keys():
                if key.startswith("new_answer_"):
                    new_answer_text = request.POST.get(key)
                    if new_answer_text.strip():  # Only create if there's actual text
                        new_answer = TempAnswer.objects.create(
                            question=question,
                            text=new_answer_text,
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
        if with_answers:
            questions = questions.filter(temp_answers__isnull=False)
        if with_language:
            questions = questions.filter(language__isnull=False)
        if with_year:
            questions = questions.filter(years__isnull=False)
        if with_specificity:
            questions = questions.filter(specificity__isnull=False)
        if with_level:
            questions = questions.filter(level__isnull=False)
        if with_system:
            questions = questions.filter(systems__isnull=False)
        if with_topic:
            questions = questions.filter(topics__isnull=False)

        # Collect IDs of questions to be processed
        temp_question_ids = list(questions.values_list("id", flat=True))

        # Trigger the Celery task
        save_questions_task.delay(temp_question_ids)

        return JsonResponse(
            {
                "success": True,
                "message": "Questions are being saved in the background.",
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
