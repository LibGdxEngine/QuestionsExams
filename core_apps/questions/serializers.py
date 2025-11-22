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
            # Use the dict key as question_id (it should be the question ID as string)
            # Fall back to question_id from value, then to text lookup for backward compatibility
            question_id = None
            question = None
            
            # Try to use the dict key as question_id (preferred)
            try:
                question_id = int(key)
                question = Question.objects.filter(id=question_id).first()
            except (ValueError, TypeError):
                pass
            
            # If not found, try question_id from value
            if question is None and "question_id" in value:
                try:
                    question_id = int(value["question_id"])
                    question = Question.objects.filter(id=question_id).first()
                except (ValueError, TypeError):
                    pass
            
            # Fall back to text lookup for backward compatibility (deprecated)
            if question is None and "question_text" in value:
                question = Question.objects.filter(text=value["question_text"]).first()
                if question:
                    question_id = question.id
            
            # If still no question found, use None
            if question_id is None:
                question_id = None

            progress_list.append(
                {
                    "id": question_id,  # Question ID
                    "question_id": question_id,  # Also include as question_id for consistency
                    "question_text": value.get("question_text", ""),  # Keep for display
                    "answer": value.get("answer", ""),
                    "is_correct": value.get("is_correct", False),
                    "correct_answer": value.get("correct_answer", ""),
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

        # Collect all question IDs and texts for bulk fetching
        question_ids_to_fetch = set()
        question_texts_to_fetch = []
        question_text_map = {}  # Map question_text -> (key, question_data)
        
        # First pass: collect all identifiers
        for question_id, question_data in data.items():
            if not isinstance(question_data, dict):
                raise serializers.ValidationError(f"Invalid data for question {question_id}.")

            # Ensure required fields are present
            if "answer" not in question_data:
                raise serializers.ValidationError(f"Missing required field 'answer' for question {question_id}.")

            # Collect question IDs
            if "question_id" in question_data:
                try:
                    question_ids_to_fetch.add(int(question_data["question_id"]))
                except (ValueError, TypeError):
                    pass
            
            # Try using dict key as question_id
            try:
                question_ids_to_fetch.add(int(question_id))
            except (ValueError, TypeError):
                pass
            
            # Collect question texts for fallback lookup
            if "question_text" in question_data:
                question_texts_to_fetch.append(question_data["question_text"])
                question_text_map[question_data["question_text"]] = (question_id, question_data)

        # Bulk fetch all questions by ID (preferred method)
        questions_by_id = {}
        if question_ids_to_fetch:
            questions = Question.objects.filter(
                id__in=question_ids_to_fetch
            ).select_related('correct_answer').prefetch_related('q_answers')
            questions_by_id = {q.id: q for q in questions}
        
        # Bulk fetch questions by text (fallback for backward compatibility)
        questions_by_text = {}
        if question_texts_to_fetch:
            questions = Question.objects.filter(
                text__in=question_texts_to_fetch
            ).select_related('correct_answer').prefetch_related('q_answers')
            # Use first() logic - if multiple exist, take the first one
            for q in questions:
                if q.text not in questions_by_text:
                    questions_by_text[q.text] = q

        # Second pass: process each question using bulk-fetched data
        processed_progress = {}
        for question_id, question_data in data.items():
            question = None
            used_id_lookup = False
            
            # Try to get question by ID from question_data (preferred)
            if "question_id" in question_data:
                try:
                    q_id = int(question_data["question_id"])
                    question = questions_by_id.get(q_id)
                    if question:
                        used_id_lookup = True
                except (ValueError, TypeError):
                    pass
            
            # Try using the dict key as question_id
            if question is None:
                try:
                    q_id = int(question_id)
                    question = questions_by_id.get(q_id)
                    if question:
                        used_id_lookup = True
                except (ValueError, TypeError):
                    pass
            
            # Fall back to text lookup for backward compatibility (deprecated)
            if question is None:
                if "question_text" in question_data:
                    question = questions_by_text.get(question_data["question_text"])
                    if question is None:
                        raise serializers.ValidationError(
                            f"Question not found. Please provide 'question_id' instead of 'question_text' for question {question_id}."
                        )
                else:
                    raise serializers.ValidationError(
                        f"Missing required field. Please provide either 'question_id' or 'question_text' for question {question_id}."
                    )

            # Ensure question_id is stored in the data for future lookups
            if not used_id_lookup or "question_id" not in question_data:
                question_data["question_id"] = question.id
            
            # Keep question_text for display purposes if provided, otherwise add it
            if "question_text" not in question_data:
                question_data["question_text"] = question.text

            # Find the answer - use prefetched q_answers
            answer_text = question_data["answer"]
            selected_answer = None
            
            # Check prefetched answers
            for answer in question.q_answers.all():
                if answer.answer_text == answer_text:
                    selected_answer = answer
                    break
            
            if selected_answer is None:
                raise serializers.ValidationError(
                    f"Answer '{answer_text}' not found for question {question.id}."
                )

            # Check if the answer is correct
            if question.correct_answer:
                is_correct = question.correct_answer == selected_answer
                question_data["is_correct"] = is_correct
                question_data["correct_answer"] = question.correct_answer.answer_text
            else:
                question_data["is_correct"] = False
                question_data["correct_answer"] = ""
            
            processed_progress[str(question.id)] = question_data

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
