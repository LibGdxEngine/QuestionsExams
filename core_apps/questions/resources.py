from import_export import resources, fields
from .models import Question


class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question
        fields = ('id', 'text', 'language', 'specificity', 'level', 'years', 'subjects', 'systems', 'topics', 'answers',
                  'correct_answer', 'is_used', 'is_correct')
        import_id_fields = ['id']  # Field used to match existing objects during import
        skip_unchanged = True
