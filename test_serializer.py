from core_apps.questions.serializers import ExamJourneyDetailsSerializerV2
import json

class MockObj:
    def __init__(self):
        # Emulate the dict structure stored in DB that presumably causes the issue or is normal
        self.progress = {"0": {"question_id": 123, "answer": "A", "is_correct": True}}
        self.question_order = []

obj = MockObj()
serializer = ExamJourneyDetailsSerializerV2(obj)
try:
    progress = serializer.get_progress(obj)
    print("PROGRESS_DATA_TYPE:", type(progress))
    print("PROGRESS_DATA:", progress)
except Exception as e:
    print("ERROR:", e)
