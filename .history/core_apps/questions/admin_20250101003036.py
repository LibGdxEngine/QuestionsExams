from django.contrib import admin
from django.shortcuts import render
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
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# Inline Model for AnswerImage
class AnswerImageInline(admin.TabularInline):
    model = AnswerImage
    extra = 1
    fields = ["image", "image_preview"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: auto;" />', obj.image.url
            )
        return "No Image"


# Inline Model for QuestionAnswer
class QuestionAnswerInline(admin.TabularInline):
    model = QuestionAnswer
    extra = 1
    min_num = 1
    can_delete = True
    fields = ["answer_text"]
    readonly_fields = ["edit_button", "get_image_preview"]

    def edit_button(self, obj):
        return format_html(
            "<button type=\"button\" onclick=\"window.open('/admin/questions/edit-answer/{}/', 'Edit Answer', 'width=600,height=400');\">Edit</button>",
            obj.id,
        )

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
    inlines = [QuestionAnswerInline]
    change_form_template = "admin/questions/question/change_form_custom.html"

    def get_formsets_with_inlines(self, request, obj=None):
        # Override to prevent default inline rendering
        return []

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

    def add_answer_button(self, obj):
        return mark_safe(
            "<button type=\"button\" onclick=\"window.open('/admin/questions/add-answer-popup/?question_id={}', 'Add Answer', 'width=600,height=400');\">Add Answer</button>".format(
                obj.id
            )
        )

    add_answer_button.short_description = "Add Answer"

    def edit_images_button(self, obj):
        return mark_safe(
            "<button type=\"button\" onclick=\"window.open('/admin/questions/edit-images/{}/', 'Edit Images', 'width=600,height=400');\">Edit Images</button>".format(
                obj.id
            )
        )

    edit_images_button.short_description = "Edit Images"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "add-answer-popup/",
                self.admin_site.admin_view(self.add_answer_view),
                name="add_answer_popup",
            ),
            path(
                "add-answer/",
                self.admin_site.admin_view(self.add_answer),
                name="add_answer",
            ),
            path(
                "edit-answer/<int:answer_id>/",
                self.admin_site.admin_view(self.edit_answer_view),
                name="edit_answer",
            ),
            path(
                "delete-answer/<int:answer_id>/",
                self.admin_site.admin_view(self.delete_answer_view),
                name="delete_answer",
            ),
        ]
        return custom_urls + urls

    def add_answer_view(self, request):
        question_id = request.GET.get("question_id")
        return render(
            request,
            "admin/questions/question/add_answer_popup.html",
            {"question_id": question_id},
        )

    def edit_images_view(self, request, question_id):
        # Implement the logic to edit images for a specific question
        pass

    @method_decorator(csrf_exempt)
    def add_answer(self, request):
        if request.method == "POST":
            answer_text = request.POST.get("answer_text")
            images = request.FILES.getlist("images")
            question_id = request.POST.get("question_id")
            try:
                question = Question.objects.get(id=question_id)
                question_answer = QuestionAnswer.objects.create(
                    question=question, answer_text=answer_text
                )
                for image in images:
                    AnswerImage.objects.create(
                        question_answer=question_answer, image=image
                    )
                return JsonResponse(
                    {"success": True, "message": "Answer added successfully!"}
                )
            except Question.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Question not found."}
                )
        return JsonResponse({"success": False, "message": "Invalid request method."})

    def edit_answer_view(self, request, answer_id):
        # Implement logic to edit the QuestionAnswer instance
        question_answer = QuestionAnswer.objects.get(id=answer_id)
        if request.method == "POST":
            # Handle form submission for editing
            question_answer.answer_text = request.POST.get(
                "answer_text", question_answer.answer_text
            )
            question_answer.save()
            return JsonResponse(
                {"success": True, "message": "Answer updated successfully!"}
            )
        return render(
            request,
            "admin/questions/question/edit_answer_popup.html",
            {"question_answer": question_answer},
        )

    def delete_answer_view(self, request, answer_id):
        try:
            question_answer = QuestionAnswer.objects.get(id=answer_id)
            question_answer.delete()
            return JsonResponse(
                {"success": True, "message": "Answer deleted successfully!"}
            )
        except QuestionAnswer.DoesNotExist:
            return JsonResponse({"success": False, "message": "Answer not found."})

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:  # Ensure the object exists
            formset = QuestionAnswerInline(self.model, self.admin_site).get_formset(request, obj)(instance=obj)
            extra_context['inline_admin_formset'] = formset
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


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
