from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Language, Specificity, Level, Year, Subject, System, Topic, Question, ExamJourney, QuestionAnswer
from .resources import QuestionResource


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource


admin.site.register(Language)
admin.site.register(Specificity)
admin.site.register(Level)
admin.site.register(Year)
admin.site.register(Subject)
admin.site.register(System)
admin.site.register(Topic)
admin.site.register(QuestionAnswer)
admin.site.register(ExamJourney)
