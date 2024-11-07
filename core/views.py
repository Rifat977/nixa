from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
import random

from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from django.contrib.auth import authenticate, login, logout



def index(request):
    return render(request, 'root/index.html')

def services(request):
    return render(request, 'root/services.html')

def service_details(request):
    return render(request, 'root/service-details.html')

def testimonial(request):
    testimonials = Testimonial.objects.all()

    styles = [f'style-{i}' for i in range(1, 8)]

    for index, testimonial in enumerate(testimonials):
        testimonial.style_class = styles[index % len(styles)]

    context = {
        'testimonials' : testimonials
    }
    return render(request, 'root/testimonial.html', context)

def faq(request):
    return render(request, 'root/faq.html')

def about(request):
    return render(request, 'root/about-us.html')

def contact(request):
    return render(request, 'root/contact.html')

def blog(request):
    return render(request, 'root/blog.html')

def blog_details(request):
    return render(request, 'root/blog-details.html')

def user_login(request):

    if request.user.is_authenticated:
            return redirect('core:index')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Debugging prints
        print(f"Email: {email}")
        print(f"Password: {password}")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("core:index")
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, "root/login.html")


def registration(request):

    if request.user.is_authenticated:
            return redirect('core:index')

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        passport_number = request.POST.get("passport_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        print(password)
        print(confirm_password)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("core:registration")

        first_name, last_name = (full_name.split(" ", 1) + [""])[:2]

        if Account.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("core:registration")

        try:
            user = Account.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                passport_number=passport_number,
                password=make_password(password),
                is_active=True, 
            )
            messages.success(request, "Registration successful! Please log in.")
            return redirect("core:login")
        except ValidationError as e:
            messages.error(request, f"Error: {e}")
            return redirect("core:registration")
    else:
        return render(request, 'root/registration.html')


def user_logout(request):
    logout(request)
    
    return redirect('core:index') 


def videos(request):
    videoss = Video.objects.all()
    context =  {
        'videos' : videoss
    }
    return render(request, 'root/videos.html', context)

def gallery(request):
    galleries = GalleryImage.objects.all()
    context = {
        'galleries' : galleries
    }
    return render(request, 'root/our-gallery.html', context)

def university(request):
    universities = University.objects.all()
    context = {
        'universities' : universities
    }
    return render(request, 'root/university.html', context)

def university_details(request, id):
    university = University.objects.get(id=id)
    programs = Program.objects.all()
    context = {
        'university' : university,
        'programs' : programs,
    }
    return render(request, 'root/university-details.html', context)

from django.http import JsonResponse

def get_subjects(request, program_id, u_id):
    subjects = Subject.objects.filter(program_id=program_id, university=u_id)
    subject_list = [{
                    'id': subject.id,
                    'name': subject.name,
                    'fee': subject.fee,
                    'university': subject.university.name,
                    'program': subject.program.name,
                    'start_date': subject.start_date,
                    'course_type': subject.course_type,
                    'course_period': subject.course_period,
                    } for subject in subjects]
    # Return the list wrapped in a 'subjects' key
    return JsonResponse({'subjects': subject_list}, safe=False)

import logging

# Set up logging
logger = logging.getLogger(__name__)
from django.contrib import messages


@require_http_methods(["GET", "POST"])
def application(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        reference_code = request.POST.get('reference_code')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        passport_number = request.POST.get('passport_number')
        date_of_birth = request.POST.get('date_of_birth')
        highest_qualification = request.POST.get('highest_qualification')
        year_of_passing = request.POST.get('year_of_passing')
        english_certificate = request.POST.get('english_language_certificate')
        program_id = request.POST.get('program')
        university_id = request.POST.get('university')
        subject_id = request.POST.get('subject')
        certificate_upload = request.FILES.get('certificate_upload')
        passport_information_page = request.FILES.get('passport_information_page')

        # Get related models
        try:
            program = get_object_or_404(Program, id=program_id)
            university = get_object_or_404(University, id=university_id)
            subject = get_object_or_404(Subject, id=subject_id)
        except Exception as e:
            logger.error(f"Error fetching related models: {e}")
            messages.error(request, "Invalid selection for program, university, or subject.")
            return render(request, 'root/application.html', {
                'programs': Program.objects.all(),
                'universities': University.objects.all(),
                'error': 'Please select a valid program, university, and subject.'
            })

        # Basic validation
        if not (name and phone and email and gender and passport_number and date_of_birth):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'root/application.html', {
                'programs': Program.objects.all(),
                'universities': University.objects.all(),
            })

        # Try to save the application
        try:
            application = Application(
                name=name,
                reference_code=reference_code,
                phone=phone,
                email=email,
                gender=gender,
                passport_number=passport_number,
                date_of_birth=date_of_birth,
                highest_qualification=highest_qualification,
                year_of_passing=year_of_passing,
                english_language_certificate=english_certificate,
                program=program,
                university=university,
                subject=subject,
                certificate_upload=certificate_upload,
                passport_information_page=passport_information_page,
            )
            application.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('core:application_success')  # Redirect to success page
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            messages.error(request, f"An error occurred while submitting your application. Please try again.")
            return render(request, 'root/application.html', {
                'programs': Program.objects.all(),
                'universities': University.objects.all(),
            })
    
    # GET request to render the form with dropdown options
    return render(request, 'root/application.html', {
        'programs': Program.objects.all(),
        'universities': University.objects.all(),
    })


def application_success(request):
    return render(request, 'root/success.html')


# def get_subjects(request, program_id, university_id):
#     program = get_object_or_404(Program, id=program_id)
#     university = get_object_or_404(University, id=university_id)

#     subjects = Subject.objects.filter(program=program, university=university)
#     subject_data = [
#         {
#             'id': subject.id,
#             'name': subject.name,
#             'fee': subject.fee
#         } for subject in subjects
#     ]
#     return JsonResponse({'subjects': subject_data})
