from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Language, Specificity, Level, Year, Subject, System, Topic, Question, ExamJourney, QuestionAnswer


class QuestionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('text', 'language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                    'correct_answer', 'is_used', 'is_correct')
    search_fields = ('text', 'language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                     'correct_answer', 'is_used', 'is_correct')
    list_filter = ('language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                   'correct_answer', 'is_used', 'is_correct')
    ordering = ('text', 'language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                'correct_answer', 'is_used', 'is_correct')


admin.site.register(Language)
admin.site.register(Specificity)
admin.site.register(Level)
admin.site.register(Year)
admin.site.register(Subject)
admin.site.register(System)
admin.site.register(Topic)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionAnswer)
admin.site.register(ExamJourney)
