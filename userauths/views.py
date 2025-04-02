from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
# from .models import User  # Import your User model from models.py
# from django.contrib.auth.models import User
from userauths.models import User
from django.contrib.auth.hashers import make_password
import sqlite3
import random, string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# from userauths.models import ResetCode
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.urls import resolve
from django.utils.text import slugify
from django.db import IntegrityError
from django.contrib import messages
import logging
from userauths.models import ResetCode
# Create your views here.


# Define the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_unique_slug(name):
    slug = slugify(name)
    unique_slug = slug
    counter = 1
    while User.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{slug}-{counter}'
        counter += 1
    return unique_slug




def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        account_type = request.POST.get('account_type', 'default')

        if not username or not email or not password:
            return JsonResponse({'status': 'All fields are required.'}, status=400)
        
        username = generate_unique_slug(username)

        if password != confirm_password:
            return JsonResponse({'status': 'Passwords do not match.'}, status=400)

        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'status': 'Username already exists.'}, status=400)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'status': 'Email already exists.'}, status=400)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, f'User {username} created successfully!')
            login(request, user)
            return JsonResponse({'status': 'User created successfully.'}, status=201)
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return JsonResponse({'status': 'An error occurred. Please try again later.'}, status=500)

    return render(request, 'auth/register.html')



def login_view(request):
    users = User.objects.all()
   
    if request.user.is_authenticated:
        return redirect('/')  # Redirect if already logged in

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # First, try to authenticate using the username
        user = authenticate(request, username=email, password=password)

        # If not found, assume the input is an email and try to get the corresponding username
        if not user:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, email=user_obj.email, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            return JsonResponse({'status': 'Login successful.'})
        else:
            return JsonResponse({'status': 'Invalid email or password.'})

    return render(request, 'auth/login.html', {'users':users})



# Function to generate a six-digit code
def generate_six_digit():
    return random.randint(100000, 999999)

# Function to check if email exists and handle password reset request
def check_mail(request):
    if request.method == 'POST':
        # Get email from POST data
        email = request.POST.get('email')

        # Check if email exists in the User model
        if email and User.objects.filter(email=email).exists():
            # Get the user data associated with the email
            userdata = User.objects.get(email=email)

            # Generate a reset code
            code = generate_six_digit()

            # Delete Previous Code
            ResetCode.objects.filter(email=email).delete()

            # Create a reset code entry in the ResetCode model
            ResetCode.objects.create(
                code=code,
                username=email,  # Storing email as the username
                email=email
            )

            # Send verification email
            send_veri_email(email, code)

            return JsonResponse({'status': 'Email Exists, Verification code sent.','user':email})

        # If the email does not exist in the User model
        return JsonResponse({'status': 'Email Does Not Exist','user':email})

    return render(request, 'auth/forget.html')


# Function to send the verification email
def send_veri_email(email, code):
    context = {
        'email': email,
        'code': code,
    }
    html_content = render_to_string('email/sendverification.html', context)
    text_content = strip_tags(html_content)

    from_email = 'info@ainhub.com'  # Replace with your email address
    to_emails = [email,'info@ainhub.com']  # The email address to send the verification code to

    # Send the email
    msg = EmailMultiAlternatives(
        subject='Email Verification Code',
        body=text_content,
        from_email=from_email,
        to=to_emails,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def reset_password(request, email):
    if request.method == 'POST':
        # Get email and password from POST data
        email_from_post = request.POST.get('email')
        password = request.POST.get('password')
        code = request.POST.get('code')

        # Debugging statement to check emails
        print('email from POST:', email_from_post, '| email from link:', email)

        # Validate if the email exists and matches the route parameter
        if email_from_post != email:
            return JsonResponse({'status': 'Invalid email provided.'}, status=400)

        if not User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'User not found.'}, status=404)
        
        # Check if the provided email and code exist in the ResetCode model
        if not ResetCode.objects.filter(email=email, code=code).exists():
            return JsonResponse({'status': 'Code not found.'}, status=404)

        try:
            # Fetch the user and update the password
            user = User.objects.get(email=email)
            user.password = make_password(password)  # Hash the new password
            user.save()

            # Delete Previous Code
            ResetCode.objects.filter(email=email).delete()

            user = authenticate(request, username=user.username, password=password)  # Adjust if using custom user model
            if user:
                login(request, user)
            return JsonResponse({'status': 'Password reset successfully.'})
        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({'status': 'Error occurred.', 'error': str(e)}, status=500)

    # Render the password reset form for GET requests
    return render(request, 'auth/reset.html', {'email': email})




def logout_view(request):
    logout(request)
    return render(request, 'auth/login.html')


def edit_user(request, id):

    return render(request, 'auth/edituser.html')