from django.contrib import admin
from .models import Language, Specificity, Level, Year, Subject, System, Topic, Question, ExamJourney,QuestionAnswer

# Register your models here.
admin.site.register(Language)
admin.site.register(Specificity)
admin.site.register(Level)
admin.site.register(Year)
admin.site.register(Subject)
admin.site.register(System)
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(QuestionAnswer)
admin.site.register(ExamJourney)
