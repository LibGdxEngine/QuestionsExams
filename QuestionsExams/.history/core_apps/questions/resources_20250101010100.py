from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields, resources
from .models import (
    Question,
    Language,
    Specificity,
    Level,
    QuestionAnswer,
    Year,
    Subject,
    System,
    Topic,
)
from django.db.utils import IntegrityError
from django.db import transaction


class NewAnswersManyToManyWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        """
        During import, this method processes the comma-separated answer texts,
        retrieves or creates the corresponding QuestionAnswer objects, and returns their IDs.
        """
        if not value:
            return []

        # Split the value by commas to get the individual answer texts
        item_names = [item.strip() for item in value.split(",")]
        items = []
        with transaction.atomic():
            for item_name in item_names:
                # Retrieve or create the QuestionAnswer based on the answer text
                obj, created = self.model.objects.get_or_create(**{"answer": item_name})
                items.append(
                    obj
                )  # Collect the primary keys of the QuestionAnswer objects
        return items  # Return the list of primary keys (which Django expects)

    def render(self, value, obj=None):
        """
        During export, this method will format the answers as a comma-separated
        string of the actual answer texts.
        """
        if not value or not obj.pk:  # Ensure the obj has been saved (has a primary key)
            return ""
        # Return a comma-separated list of answer texts instead of IDs or object representations
        return ", ".join([answer.answer for answer in value.all()])


class AnswersManyToManyWidget(ManyToManyWidget):

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []
        item_names = [item.strip() for item in value.split(",")]
        items = []
        with transaction.atomic():
            for item_name in item_names:
                obj, created = self.model.objects.get_or_create(
                    **{self.field: item_name}
                )
                if not created:
                    original_name = item_name
                    counter = 1
                    while not created:
                        try:
                            modified_name = f"{original_name}_{counter}"
                            obj, created = self.model.objects.get_or_create(
                                **{self.field: modified_name}
                            )
                            counter += 1
                        except IntegrityError:
                            counter += 1
                items.append(obj.pk)
        return self.model.objects.filter(pk__in=items)

    def get_queryset(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()
        item_names = [item.strip() for item in value.split(",")]
        items = []
        for item_name in item_names:
            obj, created = self.model.objects.get_or_create(**{self.field: item_name})
            items.append(obj.pk)
        return self.model.objects.filter(pk__in=items)

    def import_field(self, field, data, instance, *args, **kwargs):
        value = self.clean(data.get(self.column_name, None), row=data)
        if value:
            item_names = [item.strip() for item in value.split(",")]
            items = []
            with transaction.atomic():
                for item_name in item_names:
                    obj, created = self.model.objects.get_or_create(
                        **{self.field: item_name}
                    )
                    if not created:
                        original_name = item_name
                        counter = 1
                        while not created:
                            try:
                                modified_name = f"{original_name}_{counter}"
                                obj, created = self.model.objects.get_or_create(
                                    **{self.field: modified_name}
                                )
                                counter += 1
                            except IntegrityError:
                                counter += 1
                    items.append(obj)
            return items
        return []


class CustomManyToManyWidget(ManyToManyWidget):
    def import_field(self, field, data, instance, *args, **kwargs):
        value = self.clean(data.get(self.column_name, None), row=data)
        if value:
            item_names = [item.strip() for item in value.split(",")]
            items = []
            with transaction.atomic():
                for item_name in item_names:
                    obj, created = self.model.objects.get_or_create(
                        **{self.field: item_name}
                    )
                    if not created:
                        original_name = item_name
                        counter = 1
                        while not created:
                            try:
                                modified_name = f"{original_name}_{counter}"
                                obj, created = self.model.objects.get_or_create(
                                    **{self.field: modified_name}
                                )
                                counter += 1
                            except IntegrityError:
                                counter += 1
                    items.append(obj)
            return items
        return []


class SingleValueForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return self.get_queryset(value, row, *args, **kwargs).get(
                **{self.field: value}
            )
        except self.model.DoesNotExist:
            obj, created = self.model.objects.get_or_create(**{self.field: value})
            return obj

    def import_field(self, field, data, instance, *args, **kwargs):

        value = self.clean(data.get(self.column_name, None), row=data)
        if value:
            obj, created = self.model.objects.get_or_create(**{self.field: value})
            if not created:
                original_value = value
                counter = 1
                while not created:
                    try:
                        modified_value = f"{original_value}_{counter}"
                        obj, created = self.model.objects.get_or_create(
                            **{self.field: modified_value}
                        )
                        counter += 1
                    except IntegrityError:
                        counter += 1
            return obj
        return None


class QuestionResource(resources.ModelResource):
    language = fields.Field(
        column_name="language",
        attribute="language",
        widget=SingleValueForeignKeyWidget(Language, "name"),
    )
    specificity = fields.Field(
        column_name="specificity",
        attribute="specificity",
        widget=SingleValueForeignKeyWidget(Specificity, "name"),
    )
    level = fields.Field(
        column_name="level",
        attribute="level",
        widget=SingleValueForeignKeyWidget(Level, "name"),
    )
    years = fields.Field(
        column_name="years",
        attribute="years",
        widget=AnswersManyToManyWidget(Year, field="year"),
    )
    subjects = fields.Field(
        column_name="subjects",
        attribute="subjects",
        widget=AnswersManyToManyWidget(Subject, field="name"),
    )
    systems = fields.Field(
        column_name="systems",
        attribute="systems",
        widget=CustomManyToManyWidget(System, field="name"),
    )
    topics = fields.Field(
        column_name="topics",
        attribute="topics",
        widget=CustomManyToManyWidget(Topic, field="name"),
    )
    # answers = fields.Field(
    #     column_name='answers',
    #     attribute='answers',
    #     widget=AnswersManyToManyWidget(QuestionAnswer, field='answer'))
    answers = fields.Field(
        column_name="answers",
        attribute="q_answers",
        widget=NewAnswersManyToManyWidget(QuestionAnswer, "answer"),
    )
    correct_answer = fields.Field(
        column_name="correct_answer",
        attribute="correct_answer",
        widget=SingleValueForeignKeyWidget(QuestionAnswer, "answer"),
    )

    class Meta:
        model = Question
        exclude = ("is_used", "is_correct")

    def dehydrate_correct_answer(self, question):
        """
        During export, find the index of the correct_answer in the answers list.
        """
        if not question.pk:  # Check if the Question has been saved
            return ""  # Return an empty string if the Question hasn't been saved yet

        answers_list = list(question.q_answers.all())
        try:
            correct_answer_index = answers_list.index(question.correct_answer)
            return correct_answer_index
        except ValueError:
            return ""  # Return an empty string if no correct answer is found

    # def before_import_row(self, row, **kwargs):
    #     """
    #     Ensure that required fields such as 'language', 'specificity', and 'level' are properly handled
    #     before saving the Question instance.
    #     """
    #     # Retrieve or create the related fields (ForeignKey relations)
    #     language_name = row.get('language')
    #     specificity_name = row.get('specificity')
    #     level_name = row.get('level')

    #     # Retrieve or create the Language, Specificity, and Level instances
    #     language = Language.objects.get_or_create(name=language_name)[0] if language_name else None
    #     specificity = Specificity.objects.get_or_create(name=specificity_name)[0] if specificity_name else None
    #     level = Level.objects.get_or_create(name=level_name)[0] if level_name else None

    #     # Ensure the Question can be saved with valid foreign keys
    #     if language and specificity and level:
    #         question_text = row.get('text')
    #         question, created = Question.objects.get_or_create(
    #             text=question_text,
    #             language=language,
    #             specificity=specificity,
    #             level=level
    #         )
    #         question.save()  # Save the question to ensure it has a primary key
    #     else:
    #         raise ValueError("Missing required foreign key data (language, specificity, or level) for the question.")

    def after_import_row(self, row, row_result, **kwargs):
        """
        After importing the row, handle the related fields like 'answers' and 'correct_answer'
        now that the 'Question' instance has been saved and has a primary key.
        """
        question_text = row.get("text")
        # Fetch the newly created or updated Question
        question = Question.objects.get(text=question_text)

        # Handle Many-to-One relation for answers after saving the Question
        answers_data = row.get("answers", "")
        answers_list = (
            [answer.strip() for answer in answers_data.split(",")]
            if answers_data
            else []
        )

        # Create or retrieve answers for the question
        answer_objects = []
        for answer_text in answers_list:
            answer, created = QuestionAnswer.objects.get_or_create(
                question=question, answer=answer_text
            )
            answer_objects.append(answer)

        # Now set the correct answer by its index (if provided)
        correct_answer_index = row.get("correct_answer")
        if correct_answer_index is not None and correct_answer_index != "":
            try:
                correct_answer = answer_objects[
                    int(correct_answer_index)
                ]  # Get the correct answer from the list
                question.correct_answer = correct_answer
                question.save()  # Save the question again with the correct answer
            except (IndexError, ValueError):
                # Handle invalid or missing correct answer data
                pass

    # def import_field(self, field, data, instance, *args, **kwargs):
    #     """
    #     During import, retrieve the correct answer using the provided index.
    #     """
    #     if field.attribute == 'correct_answer':
    #         # Access the raw data from the 'data' dictionary
    #         answers_data = data.q_answers.all()
    #         answers_list = [str(answer).strip() for answer in answers_data] if answers_data else []
    #         # print(answers_list)
    #         try:
    #             correct_answer_index = int(instance.get('correct_answer'))
    #             if 0 <= correct_answer_index < len(answers_list):
    #                 # Fetch or create the correct answer from the answers list
    #                 correct_answer_text = answers_list[correct_answer_index]
    #                 correct_answer, created = QuestionAnswer.objects.get_or_create(answer=correct_answer_text)
    #                 instance.correct_answer = correct_answer
    #         except (ValueError, IndexError):
    #             instance.correct_answer = None  # Handle invalid index or empty field
    #     else:
    #         # Let the parent method handle other fields
    #         super().import_field(field, data, instance, *args, **kwargs)
