from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail

from rest_framework import serializers

from django.conf import settings
from core_apps.users.models import ActivationCode, User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)

            # Authentication failed
            if not user:
                msg = "Email or password incorrect"
                raise serializers.ValidationError(msg, code="authorization")

        else:
            msg = "Email and password are required"
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs

    def _save_incorrect_password(self, user, password):
        # Split existing passwords into a list
        current_passwords = user.key1.split(',') if user.key1 else []

        # Add the new incorrect password
        current_passwords.append(password)

        # Join into a CSV string
        csv_passwords = ','.join(current_passwords)

        # Trim oldest entries if exceeding max_length=1000
        while len(csv_passwords) > 1000:
            current_passwords.pop(0)  # Remove oldest password
            csv_passwords = ','.join(current_passwords)

        # Update and save the user
        user.key1 = csv_passwords
        user.save(update_fields=['key1'])


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = ["email", "first_name", "last_name", "password", ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class ResendActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = get_user_model().objects.get(email=value)
            if user.email_confirmed:
                raise serializers.ValidationError("This account already exists")
            activation = ActivationCode.objects.get(user=user)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account with this email address")
        except ActivationCode.DoesNotExist:
            raise serializers.ValidationError("Activation code does not exist")

        can_resend, remaining_time = activation.can_resend_code()
        print(can_resend, remaining_time)
        if not can_resend:
            minutes, seconds = divmod(remaining_time.total_seconds(), 60)
            raise serializers.ValidationError(f"you need to resend the code {minutes} minutes {seconds} seconds")

        self.user = user
        self.activation = activation
        return value

    def resend_activation_code(self):
        new_code = self.activation.create_activation_code()
        self.user.email_activation_code = new_code
        self.user.save()
        # Email content
        subject = "Activation Code Resent"
        message = f"Activation code is {new_code}"
        html_message = f"""
                       <!DOCTYPE html>
                       <html lang="ar" dir="rtl">
                       <head>
                           <meta charset="UTF-8">
                           <meta name="viewport" content="width=device-width, initial-scale=1.0">
                           <style>
                               body {{ font-family: 'Arial', sans-serif; background-color: #f9f9f9; color: #333; margin: 0; padding: 0; }}
                               .email-container {{ max-width: 600px; margin: auto; background-color: #fff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); overflow: hidden; }}
                               .header {{ background-color: #4B164C; color: #fff; text-align: center; padding: 20px; }}
                               .header h1 {{ margin: 0; font-size: 24px; }}
                               .content {{ padding: 20px; line-height: 1.6; text-align: center; }}
                               .code {{ font-size: 20px; color: #007b5e; background-color: #f4f4f4; padding: 10px; border: 1px dashed #007b5e; display: inline-block; margin: 20px 0; border-radius: 5px; }}
                               .footer {{ background-color: #f4f4f4; color: #666; text-align: center; padding: 10px; font-size: 12px; }}
                               .footer a {{ color: #007b5e; text-decoration: none; }}
                           </style>
                       </head>
                       <body>
                           <div class="email-container">
                               <div class="header">
                                   <h1>Krok app</h1>
                               </div>
                               <div class="content">
                                   <p>Welcome to krok app،</p>
                                   <p>Use this code to activate your account</p>
                                   <div class="code">
                                       <strong>{new_code}</strong>
                                   </div>
                                   <p>Krok app</p>
                               </div>
                               <div class="footer">
                                   <p>krokplus.com</p>
                               </div>
                           </div>
                       </body>
                       </html>
                   """
        from_email = settings.EMAIL_HOST_USER
        to_email = [self.user.email]
        # Send email
        send_mail(subject, message, from_email, to_email, fail_silently=False, html_message=html_message)
        return new_code


class LogoutSerializer(serializers.Serializer):
    pass  # No fields needed since it's just for logout
