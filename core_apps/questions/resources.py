from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export import fields, resources

from .models import Question, Language


class QuestionResource(resources.ModelResource):
    language = fields.Field(
        attribute='related_field',
        widget=ForeignKeyWidget(Language, 'name'),  # Customize lookup field
    )

    class Meta:
        model = Question
        fields = ('id', 'text', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                  'correct_answer', 'is_used', 'is_correct')

        import_id_fields = ['id']  # Field used to match existing objects during import
        skip_unchanged = True
