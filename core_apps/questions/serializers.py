from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import *
from ..profiles.models import FavoriteList
import random


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
    class Meta:
        model = Question
        exclude = ["correct_answer", "years", "subjects", "systems", "topics", "level", "specificity",
                   "language"]  # Exclude correct_answer from fields

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "answers" in data:
            random.shuffle(data["answers"])  # Shuffle the answers list
        return data

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


class ExamJourneyListSerializerV2(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    first_question = serializers.SerializerMethodField()

    class Meta:
        model = ExamJourney
        fields = ['id', 'type', 'created_at', 'time_left', 'progress', 'questions', 'first_question']

    def get_questions(self, obj):
        # Return the count of related Question objects
        return obj.questions.count()

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
                    "correct_answer": "",
                }
            )

        return progress_list

    def get_first_question(self, obj):
        """Retrieve the first question's details based on current_question index."""
        if obj.current_question is None or obj.questions.count() == 0:
            return None

        questions = list(obj.questions.all())  # Convert QuerySet to list to allow indexing
        if obj.current_question < len(questions):
            first_question = questions[obj.current_question]
            return {
                "text": first_question.text,
                "language": first_question.language.name,  # Assuming Language has a name field
                "specificity": first_question.specificity.name,  # Assuming Specificity has a name field
                "level": first_question.level.name,  # Assuming Level has a name field
                "year": first_question.years.first().year,
            }

        return None  # If index is out of range


class ExamJourneyDetailsSerializerV2(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = ExamJourney
        fields = "__all__"     
        extra_kwargs = {
            'question_order': {'required': False}
        }
          
    def get_questions(self, obj):
        # Retrieve questions in the stored order
        questions = Question.objects.filter(
            id__in=obj.question_order
        )
        
        # Maintain the specific order from question_order
        questions = sorted(
            questions, 
            key=lambda q: obj.question_order.index(q.id)
        )
        
        # Use the existing QuestionSerializer 
        serializer = QuestionSerializer(questions, many=True)
        return serializer.data
    
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
                    "correct_answer": value.get("correct_answer", ""),
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


class ProgressField(serializers.Field):
    def to_representation(self, value):
        # Convert the progress field to a dictionary for serialization
        return value

    def to_internal_value(self, data):
        # Validate and process the progress data
        if not isinstance(data, dict):
            raise serializers.ValidationError("Progress must be a dictionary.")

        processed_progress = {}
        for question_id, question_data in data.items():
            if not isinstance(question_data, dict):
                raise serializers.ValidationError(f"Invalid data for question {question_id}.")

            # Ensure required fields are present
            if "question_text" not in question_data or "answer" not in question_data:
                raise serializers.ValidationError(f"Missing required fields for question {question_id}.")

            # Retrieve the question from the database
            try:
                question = Question.objects.filter(text=question_data["question_text"]).first()

                selected_answer_text = question.q_answers.get(answer_text=question_data["answer"]).answer_text

            except Question.DoesNotExist:
                raise serializers.ValidationError(f"Question with ID {question_id} does not exist.")

            # Check if the answer is correct
            is_correct = question.correct_answer.answer_text == selected_answer_text
            question_data["is_correct"] = is_correct
            question_data["correct_answer"] = question.correct_answer.answer_text
            processed_progress[question_id] = question_data

        return processed_progress



class ExamJourneyUpdateSerializer(serializers.ModelSerializer):
    progress = ProgressField()

    class Meta:
        model = ExamJourney
        # Include fields that can be directly updated on ExamJourney
        fields = ["time_left", "current_question", "progress"]

    def update(self, instance: ExamJourney, validated_data):
        # Extract progress data if provided
        progress_data = validated_data.pop("progress", {})

        # --- Standard Field Updates ---
        # Update fields directly on the instance before saving
        instance.time_left = validated_data.get('time_left', instance.time_left)
        new_current_question_index = validated_data.get('current_question', instance.current_question)
        instance.current_question = new_current_question_index

        # --- Last Question Logic ---
        if new_current_question_index is not None:
            last_question_index = instance.questions.count() - 1

            print(f"Current Question Index Received: {new_current_question_index}")
            print(f"Last Question Index Calculated: {last_question_index}")

            # Check if the *new* current_question index indicates the last question was just answered
            if new_current_question_index >= last_question_index:
                print('Processing final question results...')

                all_journey_questions = instance.questions.all()
                statuses_to_create = []

                for question in all_journey_questions:
                    # Determine correctness from progress_data.
                    # Assumes progress_data keys are question IDs as strings.
                    # Default to False if not found in progress_data.
                  
                    is_correct = progress_data.get(str(question.id-1), {}).get("is_correct", False)
                    
                    # Prepare the UserQuestionStatus object *without saving yet*
                    status_obj = UserQuestionStatus(
                        user=instance.user,
                        question=question,
                        is_used=True, 
                        is_correct=is_correct,
                        exam_journey=instance
                    )
                    statuses_to_create.append(status_obj)

                # --- Bulk Create UserQuestionStatus ---
                if statuses_to_create:
                    # Use bulk_create for efficiency
                    UserQuestionStatus.objects.bulk_create(statuses_to_create)
                    print(f"Created {len(statuses_to_create)} UserQuestionStatus records.")
                else:
                    print("No questions found in journey to create status for.")

        instance.progress.update(progress_data)
        # Save the updated ExamJourney instance
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
                obj.question.correct_answer.answer_text
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


from .models import HomePage, FAQ


class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = ["video_url"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["faq", "answer", "faq_uk", "answer_uk"]
