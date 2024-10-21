from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError


# Create your views here.
def index(request):
    return render(request, 'root/index.html')

def services(request):
    return render(request, 'root/services.html')

def service_details(request):
    return render(request, 'root/service-details.html')

def testimonial(request):
    return render(request, 'root/testimonial.html')

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

def videos(request):
    return render(request, 'root/videos.html')

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
        ssc_year = request.POST.get('ssc_year')
        ssc_result = request.POST.get('ssc_result')
        hsc_year = request.POST.get('hsc_year')
        hsc_result = request.POST.get('hsc_result')
        bachelor_year = request.POST.get('bachelor_year')
        bachelor_result = request.POST.get('bachelor_result')
        level_of_study = request.POST.get('level_of_study')
        english_certificate = request.POST.get('english_language_certificate')
        program_id = request.POST.get('program')
        university_id = request.POST.get('university')
        subject_id = request.POST.get('subject')
        certificate_upload = request.FILES.get('certificate_upload')
        passport_information_page = request.FILES.get('passport_information_page')

        # Get related models
        program = get_object_or_404(Program, id=program_id)
        university = get_object_or_404(University, id=university_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Perform validation (basic example)
        if not name or not phone or not email or not gender or not passport_number or not date_of_birth:
            return render(request, 'root/application.html', {
                'error': 'Please fill all required fields.',
                'programs': Program.objects.all(),
                'universities': University.objects.all(),
            })

        # Save the application
        try:
            application = Application(
                name=name,
                reference_code=reference_code,
                phone=phone,
                email=email,
                gender=gender,
                passport_number=passport_number,
                date_of_birth=date_of_birth,
                ssc_year=ssc_year,
                ssc_result=ssc_result,
                hsc_year=hsc_year,
                hsc_result=hsc_result,
                bachelor_year=bachelor_year if bachelor_year else None,
                bachelor_result=bachelor_result if bachelor_result else None,
                level_of_study=level_of_study,
                english_language_certificate=english_certificate,
                program=program,
                university=university,
                subject=subject,
                certificate_upload=certificate_upload,
                passport_information_page=passport_information_page
            )

            application.save()

            # # Redirect to success page after saving
            return redirect('core:application_success') 

        except ValidationError as e:
            # Handle validation errors (if any)
            return render(request, 'root/application.html', {
                'error': f"Error: {e.message}",
                'programs': Program.objects.all(),
                'universities': University.objects.all(),
            })

    # Handle form rendering (GET)
    programs = Program.objects.all()
    universities = University.objects.all()
    return render(request, 'root/application.html', {
        'programs': programs,
        'universities': universities,
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
