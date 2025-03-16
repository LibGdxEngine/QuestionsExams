# myapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_confirmation_email(user_data):
    user_id = user_data['pkid']
    user_email = user_data['email']
    token = user_data['token']
    subject = 'Email Confirmation'
    message = f'Click the link to activate your account: http://127.0.0.1:8000/auth/activate/{user_id}/{token}'
    send_mail(subject, message, 'your_email@example.com', [user_email])
