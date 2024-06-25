from django.db import models
from django.contrib.auth import get_user_model

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


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class System(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class QuestionAnswer(models.Model):
    answer = models.CharField(max_length=300)

    def __str__(self):
        return self.answer


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
    answers = models.ManyToManyField(QuestionAnswer, related_name='questions')
    correct_answer = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamJourney(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=(('exam', 'Exam'), ('study', 'Study')))
    questions = models.ManyToManyField(Question)
    current_question = models.IntegerField(null=True, blank=True)  # Index of current question
    progress = models.JSONField(default=dict)  # Store answers and state per question
    time_left = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.type}'


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Note by {self.user} on {self.question}'


class Report(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Report by {self.user} on {self.question}'
