from django.utils import timezone

import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from core_apps.questions.models import QuestionAnswer, Question, Language, Specificity, Level, Year, Subject, System, \
    Topic, ExamJourney
from core_apps.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_retrieve_languages(normal_user):
    Language.objects.create(name='English')
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:language-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'English'
    assert len(response.data) == 1


@pytest.mark.django_db
def test_retrieve_specificities(normal_user):
    Specificity.objects.create(name='Some Specificity')
    Specificity.objects.create(name='Some Specificity 2')
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:specificity-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Some Specificity'
    assert len(response.data) == 2


@pytest.mark.django_db
def test_retrieve_levels(normal_user):
    Level.objects.create(name='Some Level')
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:level-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Some Level'


@pytest.mark.django_db
def test_retrieve_years(normal_user):
    Year.objects.create(year=2024)
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:year-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['year'] == 2024


@pytest.mark.django_db
def test_retrieve_subjects(normal_user):
    Subject.objects.create(name='Some Subject')
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:subject-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Some Subject'


@pytest.mark.django_db
def test_retrieve_systems(normal_user):
    System.objects.create(name='Some System')
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:system-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Some System'


@pytest.mark.django_db
def test_retrieve_topics(normal_user):
    Topic.objects.create(name='Some Topic')
    client = APIClient()
    client.force_authenticate(user=normal_user)
    url = reverse('questions:topic-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Some Topic'


@pytest.mark.django_db
def test_retrieve_exam_journeys(normal_user):
    # Create an ExamJourney
    exam_journey = ExamJourney.objects.create(user=normal_user, type='exam')

    # Authenticate the client
    client = APIClient()
    client.force_authenticate(user=normal_user)

    # Define the URL for retrieving ExamJourney objects
    url = reverse('questions:examjourney-list')  # replace 'your_app_name' with your actual app name

    # Make a GET request to retrieve ExamJourney objects
    response = client.get(url)

    # Check the response status code
    assert response.status_code == status.HTTP_200_OK

    # Check if the created ExamJourney is in the response data
    assert any(journey['id'] == exam_journey.id for journey in response.data)


User = get_user_model()


@pytest.mark.django_db
class TestFavoriteListViews(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_with_favorite_list()

        self.client.force_authenticate(user=self.user)

        # Create a question
        self.question = Question.objects.create(
            text='What is 2 + 2?',
            language=Language.objects.create(name='English'),
            specificity=Specificity.objects.create(name='Specificity'),
            level=Level.objects.create(name='Level'),
            correct_answer=QuestionAnswer.objects.create(answer_text='Paris')
        )

    def test_add_question_to_favorite_list(self):
        # Define the URL for adding a question to the favorite list
        url = reverse('questions:favoritelist-add-question', kwargs={'pk': self.user.favorite_lists.first().id})

        # Make a POST request to add the question to the favorite list
        response = self.client.post(url, {'question_id': self.question.id}, format='json')

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the user instance to get the updated favorite list
        self.user.refresh_from_db()

        # Check if the question is added to the favorite list
        self.assertIn(self.question, self.user.favorite_lists.first().questions.all())

    def test_remove_question_from_favorite_list(self):
        # Add the question to the favorite list
        self.user.favorite_lists.first().questions.add(self.question)
        # Define the URL for removing a question from the favorite list
        url = reverse('questions:favoritelist-remove-question', kwargs={'pk': self.user.favorite_lists.first().id})
        # Make a POST request to remove the question from the favorite list
        response = self.client.post(url, {'question_id': self.question.id}, format='json')

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the user instance to get the updated favorite list
        self.user.refresh_from_db()

        # Check if the question is removed from the favorite list
        self.assertNotIn(self.question, self.user.favorite_lists.first().questions.all())


class TestQuestionViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(first_name='testuser', last_name='last', email='test@example.com',
                                             password='password')
        # Log the user in
        self.client.force_authenticate(user=self.user)

    def test_retrieve_questions_list(self):
        # Create some questions
        Question.objects.create(
            text='What is the capital of France?',
            language=Language.objects.create(name='English'),
            specificity=Specificity.objects.create(name='Specificity'),
            level=Level.objects.create(name='Level'),
            correct_answer=QuestionAnswer.objects.create(answer_text='Paris')
        )

        url = reverse('questions:question-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'What is the capital of France?')


class ExamJourneyTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name='testuser', last_name="last", email="email@test.com",
                                             password='testpass')
        self.language = Language.objects.create(name='English')
        self.specificity = Specificity.objects.create(name='General')
        self.level = Level.objects.create(name='Beginner')
        self.year = Year.objects.create(year=2022)
        self.subject = Subject.objects.create(name='Math')
        self.system = System.objects.create(name='Metric')
        self.topic = Topic.objects.create(name='Algebra')
        self.question_answer = QuestionAnswer.objects.create(answer_text='Answer 1')
        self.question = Question.objects.create(
            text='What is 2 + 2?',
            language=self.language,
            specificity=self.specificity,
            level=self.level,
            correct_answer=self.question_answer,
            is_used=False,
            is_correct=False
        )

    def test_create_new_exam_journey(self):
        exam_journey = ExamJourney.objects.create(
            user=self.user,
            type='exam'
        )
        # Associate the Question with the ExamJourney
        exam_journey.questions.add(self.question)

        # Retrieve the ExamJourney from the database to refresh the instance
        exam_journey.refresh_from_db()

        # Check the associations and other attributes
        self.assertEqual(exam_journey.user, self.user)
        self.assertEqual(exam_journey.type, 'exam')
        self.assertEqual(exam_journey.current_question, None)
        self.assertEqual(exam_journey.progress, {})
        self.assertEqual(exam_journey.time_left, None)
        # Check if the Question is associated with the ExamJourney
        self.assertIn(self.question, exam_journey.questions.all())

    def test_make_progress_in_questions(self):
        exam_journey = ExamJourney.objects.create(
            user=self.user,
            type='exam'
        )
        exam_journey.questions.add(self.question)

        # Answer the question
        progress = {'0': {'answer': 'Answer 1', 'is_correct': True}}
        exam_journey.progress = progress
        exam_journey.save()

        # Verify progress
        self.assertEqual(exam_journey.progress['0']['answer'], 'Answer 1')
        self.assertEqual(exam_journey.progress['0']['is_correct'], True)

    def test_time_left_attribute(self):
        # Create an ExamJourney
        exam_journey = ExamJourney.objects.create(
            user=self.user,
            type='exam'
        )

        # Set a time duration for time_left
        time_duration = timezone.timedelta(minutes=30)
        exam_journey.time_left = time_duration
        exam_journey.save()

        # Fetch the ExamJourney object from the database to ensure the time_left is saved
        saved_exam_journey = ExamJourney.objects.get(id=exam_journey.id)

        # Check if time_left is correctly saved and retrieved
        self.assertEqual(saved_exam_journey.time_left, time_duration)

    def test_query_exam_journey(self):
        # Create a Question
        question = Question.objects.create(
            text='What is 2 + 2?',
            language=self.language,
            specificity=self.specificity,
            level=self.level,
            correct_answer=self.question_answer,
            is_used=False,
            is_correct=False
        )

        # Create an ExamJourney with the question
        exam_journey = ExamJourney.objects.create(
            user=self.user,
            type='exam'
        )
        exam_journey.questions.add(question)

        # Query ExamJourney based on Question attributes
        queried_exam_journey = ExamJourney.objects.filter(
            user=self.user,
            type='exam',
            questions__text='What is 2 + 2?',
            questions__language=self.language,
            questions__specificity=self.specificity,
            questions__level=self.level,
            questions__correct_answer=self.question_answer,
            questions__is_used=False,
            questions__is_correct=False
        ).first()

        # Check if queried_exam_journey is not None
        self.assertIsNotNone(queried_exam_journey)

        # Check if the queried ExamJourney is the same as the created ExamJourney
        self.assertEqual(queried_exam_journey.id, exam_journey.id)
