from celery import shared_task
from .models import ExcelUpload, TempQuestion, TempAnswer
import pandas as pd


@shared_task
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
                answer_list = [a.strip() for a in answers.split(",") if a.strip()]
                for i, answer in enumerate(answer_list):
                    TempAnswer.objects.create(
                        question=question,
                        text=answer,
                        is_correct=(str(i) == str(correct_answer)),
                    )

        return {"success": True, "upload_id": excel_upload_id}
    except Exception as e:
        return {"success": False, "error": str(e)}
