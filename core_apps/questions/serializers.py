from rest_framework import serializers
from .models import *
from ..profiles.models import FavoriteList


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class SpecificitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specificity
        fields = '__all__'


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ['id', 'answer']

    def to_internal_value(self, data):
        data = data.copy()
        answers = data.pop('answers', None)
        correct_answer = data.pop('correct_answer', None)

        if answers is not None:
            data['answers'] = [answer.id for answer in answers]
        if correct_answer is not None:
            data['correct_answer'] = correct_answer.id

        return super().to_internal_value(data)


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    correct_answer = AnswerSerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    specificity = LanguageSerializer(read_only=True)
    level = LevelSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class FavoriteListSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteList
        fields = ['id', 'pkid', 'user', 'name', 'questions']
        extra_kwargs = {
            'user': {'read_only': True}  # Make user read-only so it is not required in input data
        }


class ExamJourneySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ExamJourney
        fields = '__all__'


class ExamJourneyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamJourney
        fields = ['time_left', 'progress', 'current_question']


class QuestionFilterSerializer(serializers.Serializer):
    language = serializers.IntegerField(required=False)
    specificity = serializers.IntegerField(required=False)
    level = serializers.IntegerField(required=False)
    years = serializers.ListField(child=serializers.IntegerField(), required=False)
    subjects = serializers.ListField(child=serializers.IntegerField(), required=False)
    systems = serializers.ListField(child=serializers.IntegerField(), required=False)
    topics = serializers.ListField(child=serializers.IntegerField(), required=False)
    number_of_questions = serializers.IntegerField()
    type = serializers.ChoiceField(choices=ExamJourney._meta.get_field('type').choices, required=True)
    is_used = serializers.BooleanField(required=False)
    is_correct = serializers.BooleanField(required=False)

class NoteSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Note
        fields = ['id', 'user', 'question', 'note_text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        # Use the parent's representation
        ret = super().to_representation(instance)
        # Replace 'question' field with the serialized data from QuestionSerializer
        ret['question'] = QuestionSerializer(instance.question).data
        return ret


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'user', 'question', 'reason', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'user']

    def validate(self, data):
        user = self.context['request'].user
        question = data.get('question')

        if Report.objects.filter(user=user, question=question).exists():
            raise serializers.ValidationError("You have already reported this question.")

        return data

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
