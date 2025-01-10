from rest_framework import serializers
from .models import *
from ..profiles.models import FavoriteList


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"


class SpecificitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specificity
        fields = "__all__"


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = "__all__"


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ["id", "answer_text", "image"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ["id", "answer_text", "image"]

    def to_internal_value(self, data):
        data = data.copy()
        answers = data.pop("answers", None)
        correct_answer = data.pop("correct_answer", None)

        if answers is not None:
            data["answers"] = [answer.id for answer in answers]
        if correct_answer is not None:
            data["correct_answer"] = correct_answer.id

        return super().to_internal_value(data)


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True, source="q_answers")
    language = LanguageSerializer(read_only=True)
    specificity = LanguageSerializer(read_only=True)
    level = LevelSerializer(read_only=True)

    class Meta:
        model = Question
        exclude = ["correct_answer"]  # Exclude correct_answer from fields


class FavoriteListSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteList
        fields = ["id", "pkid", "user", "name", "questions"]
        extra_kwargs = {
            "user": {
                "read_only": True
            }  # Make user read-only so it is not required in input data
        }


class ExamJourneySerializerV2(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = ExamJourney
        fields = "__all__"

    def get_progress(self, obj):
        # Assuming that you want to transform the dictionary into a list of values
        # Modify this logic depending on the structure of your progress dictionary
        progress_dict = obj.progress
        progress_list = []

        # Convert dict to a list
        for key, value in progress_dict.items():
            # You can append as key-value pairs or just the values
            progress_list.append(
                {
                    "question_text": value["question_text"],
                    "answer": value["answer"],
                    "is_correct": value["is_correct"],
                    "correct_answer": value["correct_answer"],
                }
            )

        return progress_list


class ExamJourneySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = ExamJourney
        fields = "__all__"

    def get_progress(self, obj):
        progress_dict = obj.progress or {}
        progress_list = []

        for key, value in progress_dict.items():
            # Get the question object to access its ID
            question = Question.objects.filter(text=value["question_text"]).first()
            question_id = question.id if question else None

            progress_list.append(
                {
                    "id": question_id,  # Add question ID
                    "question_text": value["question_text"],
                    "answer": value["answer"],
                    "is_correct": value["is_correct"],
                    "correct_answer": value["correct_answer"],
                    "is_disabled": True,
                }
            )

        return progress_list


class ExamJourneyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamJourney
        fields = ["time_left", "progress", "current_question"]

    def update(self, instance, validated_data):
        # Update time_left if provided
        instance.time_left = validated_data.get("time_left", instance.time_left)
        # Update current_question if provided
        instance.current_question = validated_data.get(
            "current_question", instance.current_question
        )

        # Get the progress from validated_data or from the instance if not present
        progress = validated_data.get("progress", instance.progress)
        # Loop through the progress data and update it with 'is_correct'
        for question_text, question_status in progress.items():
            question = Question.objects.get(text=question_status["question_text"])
            user_question_status, created = UserQuestionStatus.objects.get_or_create(
                user=self.context["request"].user, question=question, is_used=True
            )
            if not created:
                user_question_status.is_correct = (
                    question.q_answers.all()[question_status["answer"]]
                    == question.correct_answer
                )
                user_question_status.save()
            # Add the 'is_correct' to the progress dict
            progress[question_text]["is_correct"] = user_question_status.is_correct
            progress[question_text]["correct_answer"] = question.correct_answer.answer
        # Save the updated progress back to the instance
        instance.progress = progress
        print(instance.current_question)
        print(instance.time_left)
        instance.save()
        return instance


class QuestionFilterSerializer(serializers.Serializer):
    language = serializers.IntegerField(required=False)
    specificity = serializers.IntegerField(required=False)
    level = serializers.IntegerField(required=False)
    years = serializers.ListField(child=serializers.IntegerField(), required=False)
    subjects = serializers.ListField(child=serializers.IntegerField(), required=False)
    systems = serializers.ListField(child=serializers.IntegerField(), required=False)
    topics = serializers.ListField(child=serializers.IntegerField(), required=False)
    number_of_questions = serializers.IntegerField()
    type = serializers.ChoiceField(
        choices=ExamJourney._meta.get_field("type").choices, required=True
    )
    is_used = serializers.BooleanField(required=False)
    is_correct = serializers.BooleanField(required=False)


class NoteSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    correct_answer = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            "id",
            "user",
            "question",
            "correct_answer",
            "note_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def get_correct_answer(self, obj):
        # Get the correct answer from the related Question
        if obj.question.correct_answer:
            return (
                obj.question.correct_answer.answer
            )  # or customize it further if you need more details
        return None

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        # Use the parent's representation
        ret = super().to_representation(instance)
        # Replace 'question' field with the serialized data from QuestionSerializer
        ret["question"] = QuestionSerializer(instance.question).data
        return ret


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "user",
            "question",
            "reason",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at", "user"]

    def validate(self, data):
        user = self.context["request"].user
        question = data.get("question")

        if Report.objects.filter(user=user, question=question).exists():
            raise serializers.ValidationError(
                "You have already reported this question."
            )

        return data

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
