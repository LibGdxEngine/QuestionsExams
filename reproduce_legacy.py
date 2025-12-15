
import os
import sys
import django

# Add project root to path
sys.path.append("/home/ahmed/Documents/krok/backend")

# Configure Django settings using the project's settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

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
    
    # We only care about get_progress output
    output = serializer.get_progress(journey)
    print("--- Serializer Output ---")
    print(output)
    
    if isinstance(output, dict) and "60011" in output:
        print("[SUCCESS] Output is a DICT and Found key '60011' (Question ID)")
    elif isinstance(output, list):
        print("[FAIL] Output is a LIST. Fix is NOT working or code is old.")
    elif "0" in output:
        print("[FAIL] Found key '0' (Index). Frontend will fail lookup.")
    else:
        print(f"[FAIL] Unexpected output: {output}")

if __name__ == '__main__':
    test_legacy_data()
