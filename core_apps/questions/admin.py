from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Language, Specificity, Level, Year, Subject, System, Topic, Question, ExamJourney, QuestionAnswer, \
    Report, University
from .resources import QuestionResource


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ['text', 'language', 'specificity', 'level']
    search_fields = ['text', 'language__name', 'specificity__name', 'level__name']
    list_filter = ['language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics']
    filter_horizontal = ['years', 'subjects', 'systems', 'topics']


admin.site.register(Language)
admin.site.register(University)
admin.site.register(Specificity)
admin.site.register(Level)
admin.site.register(Year)
admin.site.register(Subject)
admin.site.register(System)
admin.site.register(Topic)
admin.site.register(QuestionAnswer)
admin.site.register(ExamJourney)
admin.site.register(Report)
