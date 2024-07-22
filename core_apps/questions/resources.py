from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields, resources
from .models import Question, Language, Specificity, Level, QuestionAnswer, Year, Subject, System, Topic
from django.db.utils import IntegrityError
from django.db import transaction


class AnswersManyToManyWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []
        item_names = [item.strip() for item in value.split(',')]
        items = []
        with transaction.atomic():
            for item_name in item_names:
                obj, created = self.model.objects.get_or_create(**{self.field: item_name})
                if not created:
                    original_name = item_name
                    counter = 1
                    while not created:
                        try:
                            modified_name = f"{original_name}_{counter}"
                            obj, created = self.model.objects.get_or_create(**{self.field: modified_name})
                            counter += 1
                        except IntegrityError:
                            counter += 1
                items.append(obj.pk)
        return self.model.objects.filter(pk__in=items)

    def get_queryset(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()
        item_names = [item.strip() for item in value.split(',')]
        items = []
        for item_name in item_names:
            obj, created = self.model.objects.get_or_create(**{self.field: item_name})
            items.append(obj.pk)
        return self.model.objects.filter(pk__in=items)

    def import_field(self, field, data, instance, *args, **kwargs):
        value = self.clean(data.get(self.column_name, None), row=data)
        if value:
            item_names = [item.strip() for item in value.split(',')]
            items = []
            with transaction.atomic():
                for item_name in item_names:
                    obj, created = self.model.objects.get_or_create(**{self.field: item_name})
                    if not created:
                        original_name = item_name
                        counter = 1
                        while not created:
                            try:
                                modified_name = f"{original_name}_{counter}"
                                obj, created = self.model.objects.get_or_create(**{self.field: modified_name})
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
            item_names = [item.strip() for item in value.split(',')]
            items = []
            with transaction.atomic():
                for item_name in item_names:
                    obj, created = self.model.objects.get_or_create(**{self.field: item_name})
                    if not created:
                        original_name = item_name
                        counter = 1
                        while not created:
                            try:
                                modified_name = f"{original_name}_{counter}"
                                obj, created = self.model.objects.get_or_create(**{self.field: modified_name})
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
            return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
        except self.model.DoesNotExist:
            obj, created = self.model.objects.get_or_create(**{self.field: value})
            return obj

    def import_field(self, field, data, instance, *args, **kwargs):

        value = self.clean(data.get(self.column_name, None), row=data)
        print(value)
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
        widget=SingleValueForeignKeyWidget(Language, 'name'))
    specificity = fields.Field(
        column_name='specificity',
        attribute='specificity',
        widget=SingleValueForeignKeyWidget(Specificity, 'name'))
    level = fields.Field(
        column_name='level',
        attribute='level',
        widget=SingleValueForeignKeyWidget(Level, 'name'))
    years = fields.Field(
        column_name='years',
        attribute='years',
        widget=AnswersManyToManyWidget(Year, field='year'))
    subjects = fields.Field(
        column_name='subjects',
        attribute='subjects',
        widget=AnswersManyToManyWidget(Subject, field='name'))
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
        widget=AnswersManyToManyWidget(QuestionAnswer, field='answer'))
    correct_answer = fields.Field(
        column_name='correct_answer',
        attribute='correct_answer',
        widget=SingleValueForeignKeyWidget(QuestionAnswer, 'answer'))

    class Meta:
        model = Question
        exclude = ('is_used', 'is_correct')
