from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Language, Specificity, Level, Year, Subject, System, Topic, Question, ExamJourney, QuestionAnswer


class QuestionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('text', 'language', 'specificity', 'level')
    search_fields = ('text', 'language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                     'correct_answer', 'is_used', 'is_correct')
    list_filter = ('language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                   'correct_answer', 'is_used', 'is_correct')
    ordering = ('text', 'language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                'correct_answer', 'is_used', 'is_correct')

    def get_years(self, obj):
        return ", ".join([str(year) for year in obj.years.all()])

    def get_subjects(self, obj):
        return ", ".join([str(subject) for subject in obj.subjects.all()])

    def get_systems(self, obj):
        return ", ".join([str(system) for system in obj.systems.all()])

    def get_topics(self, obj):
        return ", ".join([str(topic) for topic in obj.topics.all()])

    def get_correct_answer(self, obj):
        return str(obj.correct_answer)


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
