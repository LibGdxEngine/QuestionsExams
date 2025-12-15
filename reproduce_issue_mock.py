
import sys
import json
from datetime import datetime

# Mock Django modules to allow standalone execution without Django environment
try:
    from rest_framework import serializers
except ImportError:
    # Minimal mock for DRF serializers
    class serializers:
        class ModelSerializer:
            def __init__(self, instance=None, data=None, many=False, context=None):
                self.instance = instance
                self.data = self.to_representation(instance)
            
            def to_representation(self, instance):
                return {}
        
        class SerializerMethodField:
            def __init__(self): pass
        
        class Field:
            pass

# Mock function to simulate get_progress logic exactly as in the user's file
def get_progress_logic(progress_dict):
    processed_progress = {}

    for key, value in progress_dict.items():
        question_id = None
        
        if "question_id" in value:
            try:
                question_id = int(value["question_id"])
            except (ValueError, TypeError):
                pass
        
        if question_id is None:
            try:
                question_id = int(key)
            except (ValueError, TypeError):
                pass
        
        if question_id is None:
             continue

        str_key = str(question_id)
        
        processed_progress[str_key] = {
            "id": question_id,
            "question_id": question_id,
            "question_text": value.get("question_text", ""),
            "answer": value.get("answer", ""),
            "is_correct": value.get("is_correct", False),
            "correct_answer": value.get("correct_answer", ""),
            "is_disabled": True, 
        }

    return processed_progress

def test_progress_conversion():
    print("Testing get_progress logic...")
    
    # Mock input data (progress stored in DB)
    input_progress = {
        "123": {
            "question_id": 123,
            "question_text": "Sample Question",
            "answer": "A",
            "is_correct": True,
            "correct_answer": "A"
        }
    }
    
    output = get_progress_logic(input_progress)
    
    print(f"Input Type: {type(input_progress)}")
    print(f"Output Type: {type(output)}")
    print(f"Output Data: {json.dumps(output, indent=2)}")
    
    if isinstance(output, dict):
        print("\n[SUCCESS] The logic returns a DICT.")
    else:
        print("\n[FAIL] The logic returns a LIST!")

if __name__ == "__main__":
    test_progress_conversion()
