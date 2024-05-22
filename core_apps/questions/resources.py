from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields, resources

from .models import Question, Language, Specificity, Level, QuestionAnswer, Year, Subject, System, Topic


class QuestionResource(resources.ModelResource):
    language = fields.Field(
        column_name='language',
        attribute='language',
        widget=ForeignKeyWidget(Language, 'name'))  # Assuming Language model has a 'name' field
    specificity = fields.Field(
        column_name='specificity',
        attribute='specificity',
        widget=ForeignKeyWidget(Specificity, 'name'))  # Assuming Specificity model has a 'name' field
    level = fields.Field(
        column_name='level',
        attribute='level',
        widget=ForeignKeyWidget(Level, 'name'))  # Assuming Level model has a 'name' field
    years = fields.Field(
        column_name='years',
        attribute='years',
        widget=ManyToManyWidget(Year, field='year'))  # Assuming Year model has a 'name' field
    subjects = fields.Field(
        column_name='subjects',
        attribute='subjects',
        widget=ManyToManyWidget(Subject, field='name'))  # Assuming Subject model has a 'name' field
    systems = fields.Field(
        column_name='systems',
        attribute='systems',
        widget=ManyToManyWidget(System, field='name'))  # Assuming System model has a 'name' field
    topics = fields.Field(
        column_name='topics',
        attribute='topics',
        widget=ManyToManyWidget(Topic, field='name'))  # Assuming Topic model has a 'name' field
    answers = fields.Field(
        column_name='answers',
        attribute='answers',
        widget=ManyToManyWidget(QuestionAnswer, field='answer'))  # Assuming QuestionAnswer model has a 'text' field
    correct_answer = fields.Field(
        column_name='correct_answer',
        attribute='correct_answer',
        widget=ForeignKeyWidget(QuestionAnswer, 'answer'))  # Assuming QuestionAnswer model has a 'text' field

    class Meta:
        model = Question
        exclude = ('is_used', 'is_correct')

