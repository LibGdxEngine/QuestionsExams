
from core_apps.questions.serializers import ExamJourneyDetailsSerializerV2
from core_apps.questions.models import ExamJourney

class MockExamJourney:
    def __init__(self, progress):
        self.progress = progress
        self.question_order = [60011]
        self.id = 123
        self.type = 'exam'
        self.created_at = '2024-01-01T00:00:00Z'
        self.time_left = 100
        # Mock questions manager
        self.questions = MockManager()
    
class MockManager:
    def count(self): return 1
    def first(self): return None
    def all(self): return []

def test_legacy_data():
    # Scenario: DB has progress keyed by Index "0", but value contains question_id
    progress_data = {
        "0": {
            "question_id": 60011,
            "question_text": "Sample",
            "answer": "A",
            "is_correct": False,
            "correct_answer": "B"
        }
    }
    
    journey = MockExamJourney(progress_data)
    serializer = ExamJourneyDetailsSerializerV2(journey)
    
    import sys
    # We only care about get_progress output
    output = serializer.get_progress(journey)
    sys.stderr.write("--- Serializer Output ---\n")
    sys.stderr.write(str(output) + "\n")
    
    if isinstance(output, dict) and "60011" in output:
        sys.stderr.write("[SUCCESS] Output is a DICT and Found key '60011' (Question ID)\n")
    elif isinstance(output, list):
        sys.stderr.write("[FAIL] Output is a LIST. Fix is NOT working or code is old.\n")
    elif "0" in output:
        sys.stderr.write("[FAIL] Found key '0' (Index). Frontend will fail lookup.\n")
    else:
        sys.stderr.write(f"[FAIL] Unexpected output: {output}\n")

test_legacy_data()
