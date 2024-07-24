import random
from faker import Faker
from django.core.management.base import BaseCommand

from core_apps.questions.models import Language, Specificity, Level, Year, Subject, System, Topic, Question, QuestionAnswer


class Command(BaseCommand):
    help = 'Generate random questions'

    def handle(self, *args, **kwargs):
        faker = Faker()

        # Get all available options for each attribute
        languages = Language.objects.all()
        specificities = Specificity.objects.all()
        levels = Level.objects.all()
        years = Year.objects.all()
        subjects = Subject.objects.all()
        systems = System.objects.all()
        topics = Topic.objects.all()
        question_answers = QuestionAnswer.objects.all()

        num_years_to_choose = random.randint(1, len(years))
        num_answers_to_choose = random.randint(1, len(question_answers))
        # Define the number of questions to generate
        num_questions = 50

        for _ in range(num_questions):
            # Randomly select attributes for the question
            language = random.choice(languages[:1])
            specificity = random.choice(specificities[:1])
            level = random.choice(levels[:1])
            chosen_years = random.sample(list(years), num_years_to_choose)
            subject = random.choice(subjects[:1])
            system = random.choice(systems[:1])
            topic = random.choice(topics[:1])
            text = faker.sentence()
            chosen_answers = random.choice(list(question_answers))
            correct_answer = random.choice(chosen_answers)

            # Create the question
            question = Question.objects.create(
                language=language,
                specificity=specificity,
                level=level,
                text=text,
                correct_answer=correct_answer
            )
            question.years.clear()
            question.years.set(chosen_years)
            question.subjects.clear()
            question.subjects.set([subject])
            question.systems.clear()
            question.systems.set([system])
            question.topics.clear()
            question.topics.set([topic])
            question.answers.clear()
            question.answers.set(chosen_answers)

            self.stdout.write(self.style.SUCCESS(f'Question "{text}" created successfully'))
