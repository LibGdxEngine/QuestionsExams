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


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = '__all__'


class FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteList
        fields = ['id', 'user', 'name', 'questions']


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.PrimaryKeyRelatedField(queryset=QuestionAnswer.objects.all(), many=True)
    correct_answer = serializers.PrimaryKeyRelatedField(queryset=QuestionAnswer.objects.all())

    class Meta:
        model = Question
        fields = '__all__'

    def to_internal_value(self, data):
        data = data.copy()
        answers = data.pop('answers', None)
        correct_answer = data.pop('correct_answer', None)

        if answers is not None:
            data['answers'] = [answer.id for answer in answers]
        if correct_answer is not None:
            data['correct_answer'] = correct_answer.id

        return super().to_internal_value(data)


class ExamJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamJourney
        fields = '__all__'
