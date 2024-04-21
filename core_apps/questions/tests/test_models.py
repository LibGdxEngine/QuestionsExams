import pytest
from django.test import TestCase

from django.contrib.auth import get_user_model

from core_apps.questions.models import Language, Specificity, Level, Year, Subject, System, Topic, QuestionAnswer, \
    Question, ExamJourney

User = get_user_model()


class ModelTestCase(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.language = Language.objects.create(name='English')
        self.specificity = Specificity.objects.create(name='Specificity 1')
        self.level = Level.objects.create(name='Level 1')
        self.year = Year.objects.create(year=2022)
        self.subject = Subject.objects.create(name='Subject 1')
        self.system = System.objects.create(name='System 1')
        self.topic = Topic.objects.create(name='Topic 1')
        self.answer = QuestionAnswer.objects.create(answer='Answer 1')
        self.question = Question.objects.create(
            text='Question 1',
            language=self.language,
            specificity=self.specificity,
            level=self.level,
            correct_answer=self.answer
        )
        self.question.years.add(self.year)
        self.question.subjects.add(self.subject)
        self.question.systems.add(self.system)
        self.question.topics.add(self.topic)
        self.exam_journey = ExamJourney.objects.create(
            user=User.objects.create(first_name='test_user', last_name="last", email="email@test.com",
                                     password="test1234"),  # Create a user here if needed
            type='exam',
            current_question=1
        )
        self.exam_journey.questions.add(self.question)

    def test_models(self):
        # Retrieve objects from the database
        language = Language.objects.get(name='English')
        specificity = Specificity.objects.get(name='Specificity 1')
        level = Level.objects.get(name='Level 1')
        year = Year.objects.get(year=2022)
        subject = Subject.objects.get(name='Subject 1')
        system = System.objects.get(name='System 1')
        topic = Topic.objects.get(name='Topic 1')
        answer = QuestionAnswer.objects.get(answer='Answer 1')
        question = Question.objects.get(text='Question 1')

        # Test Language model
        self.assertEqual(str(language), 'English')

        # Test Specificity model
        self.assertEqual(str(specificity), 'Specificity 1')

        # Test Level model
        self.assertEqual(str(level), 'Level 1')

        # Test Year model
        self.assertEqual(year.year, 2022)

        # Test Subject model
        self.assertEqual(str(subject), 'Subject 1')

        # Test System model
        self.assertEqual(str(system), 'System 1')

        # Test Topic model
        self.assertEqual(str(topic), 'Topic 1')

        # Test QuestionAnswer model
        self.assertEqual(str(answer), 'Answer 1')

        # Test Question model
        self.assertEqual(str(question), 'Question 1')
