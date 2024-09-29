from django import forms
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Language, Specificity, Level, Year, Subject, System, Topic, Question, ExamJourney, QuestionAnswer, \
    Report, University, UserQuestionStatus
from .resources import QuestionResource


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ['text', 'language', 'specificity', 'level']
    search_fields = ['text', 'language__name', 'specificity__name', 'level__name']
    list_filter = ['language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics']
    filter_horizontal = ['years', 'subjects', 'systems', 'topics']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "correct_answer":
            # Only show the QuestionAnswer options that are related to this question
            if request.resolver_match.kwargs.get('object_id'):
                question_id = request.resolver_match.kwargs.get('object_id')
                kwargs["queryset"] = QuestionAnswer.objects.filter(questions__id=question_id)
            else:
                kwargs["queryset"] = QuestionAnswer.objects.none()  # No options if there's no question instance
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        """
        Override save_related to ensure that the correct_answer field is set
        after the answers have been created.
        """
        super().save_related(request, form, formsets, change)
        # Now that answers are saved, we can update the correct_answer queryset
        if form.instance.pk:
            form.instance.correct_answer = form.cleaned_data.get('correct_answer')
            form.instance.save()


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
admin.site.register(UserQuestionStatus)
