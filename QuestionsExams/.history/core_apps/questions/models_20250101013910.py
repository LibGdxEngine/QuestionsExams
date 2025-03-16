from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Specificity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class University(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Year(models.Model):
    year = models.IntegerField()

    def __str__(self):
        return str(self.year)

    @staticmethod
    def filter_years(language_id, specificity_id, level_id):
        return Year.objects.filter(
            question__language_id=language_id,
            question__specificity_id=specificity_id,
            question__level_id=level_id,
        ).distinct()


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @staticmethod
    def filter_subjects(language_id, specificity_id, level_id):
        return Subject.objects.filter(
            question__language_id=language_id,
            question__specificity_id=specificity_id,
            question__level_id=level_id,
        ).distinct()


class System(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @staticmethod
    def filter_systems(language_id, specificity_id, level_id):
        return System.objects.filter(
            question__language_id=language_id,
            question__specificity_id=specificity_id,
            question__level_id=level_id,
        ).distinct()


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @staticmethod
    def filter_topics(language_id, specificity_id, level_id):
        return Topic.objects.filter(
            question__language_id=language_id,
            question__specificity_id=specificity_id,
            question__level_id=level_id,
        ).distinct()


class QuestionAnswer(models.Model):
    question = models.ForeignKey(
        "Question",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="q_answers",
    )
    answer_text = models.CharField(
        max_length=300, blank=True, default=""
    )  # Optional text part of the answer

    def __str__(self):
        return self.answer_text or "Answer with Images"


class AnswerImage(models.Model):
    question_answer = models.ForeignKey(
        QuestionAnswer, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="answer_images/")

    def __str__(self):
        return f"Image for {self.question_answer}"


class Question(models.Model):
    text = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    specificity = models.ForeignKey(Specificity, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    years = models.ManyToManyField(Year)
    subjects = models.ManyToManyField(Subject)
    systems = models.ManyToManyField(System)
    topics = models.ManyToManyField(Topic)
    hint = models.CharField(max_length=300, blank=True, default="")
    video_hint = models.URLField(blank=True, default="")
    # answers = models.ManyToManyField(QuestionAnswer, related_name='questions')
    correct_answer = models.ForeignKey(
        QuestionAnswer,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="correct_questions",
    )
    is_used = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamJourney(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=20, choices=(("exam", "Exam"), ("study", "Study"))
    )
    questions = models.ManyToManyField(Question)
    current_question = models.IntegerField(
        null=True, blank=True
    )  # Index of current question
    progress = models.JSONField(default=dict)  # Store answers and state per question
    time_left = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.type}"


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note by {self.user} on {self.question}"


class Report(models.Model):
    REPORT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("resolved", "Resolved"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=REPORT_STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report by {self.user} on {self.question}"


class UserQuestionStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Status of {self.user} on {self.question}"


class ExcelUpload(models.Model):
    file = models.FileField(upload_to="excel_uploads/")
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Excel Upload {self.id} - {self.uploaded_at}"


class TempQuestion(models.Model):
    excel_upload = models.ForeignKey(
        ExcelUpload, on_delete=models.CASCADE, related_name="temp_questions"
    )
    text = models.TextField()
    language = models.CharField(max_length=100, null=True, blank=True)
    specificity = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=100, null=True, blank=True)
    years = models.CharField(max_length=255, null=True, blank=True)
    subjects = models.CharField(max_length=255, null=True, blank=True)
    systems = models.CharField(max_length=255, null=True, blank=True)
    topics = models.CharField(max_length=255, null=True, blank=True)
    hint = models.TextField(null=True, blank=True)
    video_hint = models.CharField(max_length=255, null=True, blank=True)


class TempAnswer(models.Model):
    question = models.ForeignKey(
        TempQuestion, on_delete=models.CASCADE, related_name="temp_answers"
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Answer(models.Model):
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
