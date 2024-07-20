from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields, resources
from .models import Question, Language, Specificity, Level, QuestionAnswer, Year, Subject, System, Topic
from django.db.utils import IntegrityError


class CustomManyToManyWidget(ManyToManyWidget):
    def import_field(self, field, data, instance, *args, **kwargs):
        value = self.clean(data.get(self.column_name, None), row=data)
        if value:
            answer_texts = [val.strip() for val in value.split(',')]
            answers = []
            for answer_text in answer_texts:
                obj, created = self.model.objects.get_or_create(**{self.field: answer_text})
                if not created:
                    original_text = answer_text
                    counter = 1
                    while not created:
                        try:
                            modified_text = f"{original_text}_{counter}"
                            obj, created = self.model.objects.get_or_create(**{self.field: modified_text})
                            counter += 1
                        except IntegrityError:
                            counter += 1
                answers.append(obj)
            return answers
        return []


class CustomForeignKeyWidget(ForeignKeyWidget):
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
                        obj, created = self.model.objects.get_or_create(**{self.field: modified_value})
                        counter += 1
                    except IntegrityError:
                        counter += 1
            return obj
        return None


class QuestionResource(resources.ModelResource):
    language = fields.Field(
        column_name='language',
        attribute='language',
        widget=CustomForeignKeyWidget(Language, 'name'))
    specificity = fields.Field(
        column_name='specificity',
        attribute='specificity',
        widget=CustomForeignKeyWidget(Specificity, 'name'))
    level = fields.Field(
        column_name='level',
        attribute='level',
        widget=CustomForeignKeyWidget(Level, 'name'))
    years = fields.Field(
        column_name='years',
        attribute='years',
        widget=CustomManyToManyWidget(Year, field='year'))
    subjects = fields.Field(
        column_name='subjects',
        attribute='subjects',
        widget=CustomManyToManyWidget(Subject, field='name'))
    systems = fields.Field(
        column_name='systems',
        attribute='systems',
        widget=CustomManyToManyWidget(System, field='name'))
    topics = fields.Field(
        column_name='topics',
        attribute='topics',
        widget=CustomManyToManyWidget(Topic, field='name'))
    answers = fields.Field(
        column_name='answers',
        attribute='answers',
        widget=CustomManyToManyWidget(QuestionAnswer, field='answer'))
    correct_answer = fields.Field(
        column_name='correct_answer',
        attribute='correct_answer',
        widget=CustomForeignKeyWidget(QuestionAnswer, 'answer'))

    class Meta:
        model = Question
        exclude = ('is_used', 'is_correct')
