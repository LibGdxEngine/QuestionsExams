from rest_framework import serializers
from .models import *


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


class QuestionSerializer(serializers.ModelSerializer):
    answers = QuestionAnswerSerializer(many=True)
    correct_answer = QuestionAnswerSerializer()

    class Meta:
        model = Question
        fields = '__all__'


class ExamJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamJourney
        fields = '__all__'
