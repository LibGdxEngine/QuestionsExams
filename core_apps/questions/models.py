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
