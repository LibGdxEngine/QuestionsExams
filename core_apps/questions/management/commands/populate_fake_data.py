import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from core_apps.questions.models import (
    Language, Specificity, Level, Year, Subject, System, Topic,
    Question, QuestionAnswer, ExamJourney, User, UserQuestionStatus
)

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with fake data'

    def add_arguments(self, parser):
        parser.add_argument('--questions', type=int, default=1000, help='Number of questions to create')
        parser.add_argument('--exams', type=int, default=100, help='Number of exams to create')

    def handle(self, *args, **kwargs):
        num_questions = kwargs['questions']
        num_exams = kwargs['exams']

        # Create base data (Languages, Specificities, etc.)
        self.create_base_data()
        self.stdout.write(self.style.SUCCESS(f'create_base_data Successfully created'))
        # Create Questions and Answers
        questions = self.create_questions(num_questions)
        # questions = Question.objects.all()
        self.stdout.write(self.style.SUCCESS(f'questions Successfully created'))
        # Create Users
        users = self.create_users(2)  # Create 5 test users
        self.stdout.write(self.style.SUCCESS(f'users Successfully created'))
        # Create ExamJourneys
        self.create_exams(num_exams, users, questions)
        self.stdout.write(self.style.SUCCESS(f'Exams Successfully created'))
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_questions} questions and {num_exams} exams'))

    def create_base_data(self):
        # Create Languages
        languages = ['English', 'German', 'French']
        for lang in languages:
            Language.objects.get_or_create(name=lang)
        self.stdout.write(self.style.SUCCESS(f'languages Successfully created'))
        # Create Specificities
        specificities = ['Medicine', 'Engineering', 'Law']
        for spec in specificities:
            Specificity.objects.get_or_create(name=spec)
        self.stdout.write(self.style.SUCCESS(f'specificities Successfully created'))
        # Create Levels
        levels = ['Beginner', 'Intermediate', 'Advanced']
        for level in levels:
            Level.objects.get_or_create(name=level)

        # Create Years (2020-2023)
        for year in range(2020, 2024):
            Year.objects.get_or_create(year=year)

        # Create Subjects
        subjects = ['Anatomy', 'Civil Law', 'Thermodynamics']
        for sub in subjects:
            Subject.objects.get_or_create(name=sub)

        # Create Systems
        systems = ['Cardiovascular', 'Legal', 'Mechanical']
        for sys in systems:
            System.objects.get_or_create(name=sys)

        # Create Topics
        topics = ['Heart', 'Contract Law', 'Energy Transfer']
        for topic in topics:
            Topic.objects.get_or_create(name=topic)

    def create_questions(self, num_questions):
        languages = list(Language.objects.all())
        specificities = list(Specificity.objects.all())
        levels = list(Level.objects.all())
        years = list(Year.objects.all())
        subjects = list(Subject.objects.all())
        systems = list(System.objects.all())
        topics = list(Topic.objects.all())

        questions = []
        for _ in range(num_questions):
            question = Question.objects.create(
                text=fake.paragraph(nb_sentences=3),
                language=languages[0],
                specificity=specificities[0],
                level=levels[0],
                hint=fake.sentence(),
                video_hint=fake.url() if random.choice([True, False]) else "",
                is_used=True,
                is_correct=False
            )

            # Add M2M relationships
            question.years.add(years[0])
            question.subjects.add(subjects[0])
            question.systems.add(systems[0])
            question.topics.add(topics[0])

            # Create Answers
            answers = []
            for _ in range(3):  # Create 3 answers per question
                answer = QuestionAnswer.objects.create(
                    question=question,
                    answer_text=fake.sentence(),
                )
                answers.append(answer)

            # Assign a correct answer
            question.correct_answer = random.choice(answers)
            question.save()
            self.stdout.write(self.style.SUCCESS(f'question {_} Successfully created'))
            questions.append(question)
        return questions

    def create_users(self, num_users):
        users = []
        for _ in range(num_users):
            user = User.objects.create_user(
                first_name="fake1",
                last_name="fake2",
                email=fake.email(),
                password='testpass123',
                is_active=True
            )
            users.append(user)
        return users

    def create_exams(self, num_exams, users, questions):
        exam_types = ['exam', 'study']
        for _ in range(num_exams):
            exam = ExamJourney.objects.create(
                user=random.choice(users),
                type=random.choice(exam_types),
                current_question=random.randint(0, 20),
                progress={},  # Customize as needed
                time_left=timezone.timedelta(minutes=random.randint(30, 180))
            )
            self.stdout.write(self.style.SUCCESS(f'exam Successfully created'))
            # Add questions to exam
            selected_questions = random.sample(list(questions), k=random.randint(10, 30))
            exam.questions.add(*selected_questions)

            # Create UserQuestionStatus entries
            for q in selected_questions:
                UserQuestionStatus.objects.create(
                    user=exam.user,
                    question=q,
                    is_used=random.choice([True, False]),
                    is_correct=random.choice([True, False])
                )
