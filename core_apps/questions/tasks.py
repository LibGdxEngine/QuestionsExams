from celery import shared_task
from .models import (
    ExcelUpload,
    TempQuestion,
    TempAnswer,
    Question,
    Language,
    Specificity,
    Level,
    Year,
    Subject,
    System,
    Topic,
    Answer,
    QuestionAnswer,
)
import pandas as pd


# @shared_task
def process_excel_file(excel_upload_id):
    try:
        excel_upload = ExcelUpload.objects.get(id=excel_upload_id)
        df = pd.read_excel(excel_upload.file)

        for index, row in df.iterrows():
            question_data = {
                "excel_upload": excel_upload,
                "text": str(row.get("text", "")),
                "language": str(row.get("language", "")),
                "specificity": str(row.get("specificity", "")),
                "level": str(row.get("level", "")),
                "years": str(row.get("years", "")),
                "subjects": str(row.get("subjects", "")),
                "systems": str(row.get("systems", "")),
                "topics": str(row.get("topics", "")),
                "hint": str(row.get("hint", "")),
                "video_hint": str(row.get("video_hint", "")),
            }
            question = TempQuestion.objects.create(**question_data)

            answers = row.get("answers", "")
            correct_answer = row.get("correct_answer", "")
            if pd.notna(answers):
                answer_list = [a.strip() for a in list(set(answers.split(","))) if a.strip()]
                for i, answer in enumerate(answer_list):
                    TempAnswer.objects.create(
                        question=question,
                        text=answer,
                        is_correct=(str(i) == str(correct_answer)),
                    )


        # Mark the upload as processed
        excel_upload.processed = True
        excel_upload.save()

        return {"success": True, "upload_id": excel_upload_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@shared_task
def save_questions_task(temp_question_ids):
    for temp_question_id in temp_question_ids:
        try:
            temp_question = TempQuestion.objects.get(id=temp_question_id)

            # Get or create Language instance
            language, _ = Language.objects.get_or_create(name=temp_question.language)

            # Get or create Specificity instance
            specificity, _ = Specificity.objects.get_or_create(
                name=temp_question.specificity
            )

            # Get or create Level instance
            level, _ = Level.objects.get_or_create(name=temp_question.level)

            # Create the Question instance
            question = Question.objects.create(
                text=temp_question.text,
                language=language,
                specificity=specificity,
                level=level,
                hint=temp_question.hint,
                video_hint=temp_question.video_hint,
            )

            # Handle ManyToMany fields
            if temp_question.years:
                for year in temp_question.years.split(","):
                    try:
                        year_instance, _ = Year.objects.get_or_create(
                            year=str(year.strip())
                        )
                        question.years.add(year_instance)
                    except ValueError as e:
                        print(f"Error converting year '{year}': {e}")

            if temp_question.subjects:
                for subject in temp_question.subjects.split(","):
                    if subject.strip():
                        subject_instance, _ = Subject.objects.get_or_create(
                            name=subject.strip()
                        )
                        question.subjects.add(subject_instance)

            if temp_question.systems:
                for system in temp_question.systems.split(","):
                    if system.strip():
                        system_instance, _ = System.objects.get_or_create(
                            name=system.strip()
                        )
                        question.systems.add(system_instance)

            if temp_question.topics:
                for topic in temp_question.topics.split(","):
                    if topic.strip():
                        topic_instance, _ = Topic.objects.get_or_create(
                            name=topic.strip()
                        )
                        question.topics.add(topic_instance)

            # Transfer answers with images
            for temp_answer in temp_question.temp_answers.all():
                question_answer = QuestionAnswer.objects.create(
                    question=question,
                    answer_text=temp_answer.text,
                )

                # Handle image transfer if exists
                if temp_answer.image:
                    question_answer.image = temp_answer.image
                    question_answer.save()

                # Set as correct answer if applicable
                if temp_answer.is_correct:
                    question.correct_answer = question_answer
                    question.save()

            # Mark the question as processed and delete it
            temp_question.delete()

        except Exception as e:
            # Log the error
            print(f"Error saving question {temp_question_id}: {e}")
