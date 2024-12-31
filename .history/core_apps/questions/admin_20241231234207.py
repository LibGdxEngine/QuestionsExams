from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Language,
    Specificity,
    Level,
    Year,
    Subject,
    System,
    Topic,
    Question,
    ExamJourney,
    QuestionAnswer,
    Report,
    University,
    UserQuestionStatus,
    AnswerImage,
)
from .resources import QuestionResource
from django.utils.html import format_html


# Inline Model for AnswerImage
class AnswerImageInline(admin.TabularInline):
    model = AnswerImage
    extra = 1  # Number of empty image fields to show by default
    can_delete = True  # Allow deletion of images
    fields = ["image"]  # Ensure the image field is displayed


# Inline Model for QuestionAnswer
class QuestionAnswerInline(admin.TabularInline):
    model = QuestionAnswer
    extra = 1  # Number of empty answer fields to show by default
    min_num = 1  # Ensure at least one answer is required
    can_delete = True  # Allow deletion of answers
    inlines = [AnswerImageInline]  # Include the AnswerImage inline
    fields = ["answer_text", "get_image_preview"]
    readonly_fields = ["get_image_preview"]

    # Add a method to display images
    def get_image_preview(self, obj):
        if obj.images.exists():
            return format_html(
                "".join(
                    [
                        f'<img src="{image.image.url}" width="50" height="50" style="margin: 2px;" />'
                        for image in obj.images.all()
                    ]
                )
            )
        return "No Images"

    get_image_preview.short_description = "Images"


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ["text", "language", "specificity", "level"]
    search_fields = ["text", "language__name", "specificity__name", "level__name"]
    list_filter = [
        "language",
        "specificity",
        "level",
        "years",
        "subjects",
        "systems",
        "topics",
    ]
    filter_horizontal = ["years", "subjects", "systems", "topics"]
    exclude = ["is_used", "is_correct"]
    inlines = [QuestionAnswerInline]  # Include the QuestionAnswer inline
    change_form_template = "admin/questions/question/change_form.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "correct_answer":
            if request.resolver_match.kwargs.get("object_id"):
                question_id = request.resolver_match.kwargs.get("object_id")
                kwargs["queryset"] = QuestionAnswer.objects.filter(
                    question__id=question_id
                )
            else:
                kwargs["queryset"] = (
                    QuestionAnswer.objects.none()
                )  # No options if there's no question instance
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        """
        Override save_related to ensure that the correct_answer field is set
        after the answers have been created.
        """
        super().save_related(request, form, formsets, change)
        if form.instance.pk:
            form.instance.correct_answer = form.cleaned_data.get("correct_answer")
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
admin.site.register(AnswerImage)
