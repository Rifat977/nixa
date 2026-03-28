import json
import logging
from datetime import datetime

from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from .models import (
    Account, Application, Blog, ContactMessage, Consultation, Destination,
    Event, EventBooking, FAQ, GalleryImage, NewsletterSubscriber, Program,
    Scholarship, Subject, Testimonial, University, Video, Offer, SiteSettings,
)

logger = logging.getLogger(__name__)



def index(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-is_pinned', '-published_at')[:6]
    # Featured universities for homepage (stacked 5x3 logo grid inside slider)
    featured_universities = list(University.objects.filter(is_featured=True))
    university_slides = []
    # Each slide contains up to 15 universities arranged as 5 columns x 3 rows
    chunk_size = 15
    for i in range(0, len(featured_universities), chunk_size):
        chunk = featured_universities[i:i + chunk_size]
        columns = []
        for col_index in range(5):
            start = col_index * 3
            col_items = chunk[start:start + 3]
            if col_items:
                columns.append(col_items)
        if columns:
            university_slides.append(columns)
    videos = list(Video.objects.filter(is_active=True))
    # Chunk into slides of 4 for homepage carousel
    video_slides = [videos[i:i + 4] for i in range(0, len(videos), 4)]
    testimonials = list(Testimonial.objects.filter(is_active=True))
    testimonial_slides = [testimonials[i:i + 3] for i in range(0, len(testimonials), 3)]
    featured_offer = Offer.objects.filter(is_active=True).order_by('order', '-created_at').first()
    context = {
        'blogs': blogs,
        'universities': featured_universities,
        'university_slides': university_slides,
        'testimonials': testimonials,
        'testimonial_slides': testimonial_slides,
        'featured_offer': featured_offer,
        'videos': videos,
        'video_slides': video_slides,
        'faqs': FAQ.objects.filter(is_active=True)[:12],
        'destinations': Destination.objects.filter(is_active=True).order_by('order', 'name'),
    }
    return render(request, 'root/index.html', context)

def services(request):
    return render(request, 'root/services.html')

def service_details(request):
    return render(request, 'root/service-details.html')

def faq(request):
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'root/faq.html', {'faqs': faqs})

def about(request):
    return render(request, 'root/about-us.html')

@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            messages.error(request, "Please fill in your name, email, and message.")
            return render(request, 'root/contact.html', {
                'form_data': {'name': name, 'email': email, 'subject': subject, 'phone': phone, 'message': message}
            })

        ContactMessage.objects.create(
            name=name, email=email, subject=subject, phone=phone, message=message
        )
        messages.success(request, "Your message has been sent! We'll get back to you shortly.")
        return redirect('core:contact')

    return render(request, 'root/contact.html')


def _consultation_form_context(form_data=None):
    ctx = {"destinations": Destination.objects.filter(is_active=True).order_by('order', 'name')}
    if form_data:
        ctx["form_data"] = form_data
    return ctx


@require_http_methods(["GET", "POST"])
def consultation(request):
    """Book a free consultation - GET shows form, POST saves booking."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        preferred_destination = request.POST.get("preferred_destination", "").strip()
        consultation_type = request.POST.get("consultation_type", "online")
        preferred_date = request.POST.get("preferred_date") or None
        preferred_time_slot = request.POST.get("preferred_time_slot", "").strip()
        message = request.POST.get("message", "").strip()

        form_data = {
            "name": name, "email": email, "phone": phone,
            "preferred_destination": preferred_destination,
            "consultation_type": consultation_type,
            "preferred_date": preferred_date,
            "preferred_time_slot": preferred_time_slot,
            "message": message,
        }

        if not (name and email and phone):
            messages.error(request, "Please fill in your name, email, and phone number.")
            return render(request, "root/consultation.html", _consultation_form_context(form_data))

        preferred_date_obj = None
        if preferred_date:
            try:
                preferred_date_obj = datetime.strptime(preferred_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                preferred_date_obj = None

        valid_time_slots = [choice[0] for choice in Consultation.TIME_SLOT_CHOICES]
        if preferred_time_slot and preferred_time_slot not in valid_time_slots:
            preferred_time_slot = None

        Consultation.objects.create(
            name=name,
            email=email,
            phone=phone,
            preferred_destination=preferred_destination or None,
            consultation_type=consultation_type,
            preferred_date=preferred_date_obj,
            preferred_time_slot=preferred_time_slot or None,
            message=message or None,
        )
        messages.success(request, "Your consultation has been booked! Our team will contact you within 24 hours to confirm your slot.")
        return redirect("core:consultation_success")

    return render(request, "root/consultation.html", _consultation_form_context())


def consultation_success(request):
    """Thank you page after booking consultation."""
    return render(request, "root/consultation-success.html")


def blog(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-is_pinned', '-published_at')
    context = {
        'blogs':blogs
    }
    return render(request, 'root/blog.html', context)

def blog_details(request, pk):
    blog = get_object_or_404(Blog, id=pk)
    return render(request, 'root/blog-details.html', {'blog': blog})

def user_login(request):

    if request.user.is_authenticated:
            return redirect('core:index')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
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

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("core:registration")

        if not (full_name and full_name.strip()):
            messages.error(request, "Please enter your full name.")
            return redirect("core:registration")

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, " ".join(e.messages) if e.messages else "Please choose a stronger password.")
            return redirect("core:registration")

        first_name, last_name = (full_name.strip().split(" ", 1) + [""])[:2]

        if Account.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("core:registration")

        try:
            user = Account.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                passport_number=passport_number or None,
                password=make_password(password),
                is_active=True,
            )
            messages.success(request, "Registration successful! Please log in.")
            return redirect("core:login")
        except IntegrityError:
            messages.error(request, "An account with this email already exists.")
            return redirect("core:registration")
        except ValidationError:
            logger.exception("Registration validation error")
            messages.error(request, "Registration failed. Please check your input and try again.")
            return redirect("core:registration")
    else:
        return render(request, 'root/registration.html')


def user_logout(request):
    logout(request)
    
    return redirect('core:index') 


def gallery(request):
    galleries = GalleryImage.objects.all()
    context = {
        'galleries' : galleries
    }
    return render(request, 'root/our-gallery.html', context)

def university(request):
    # Group universities by country (only countries that have universities)
    universities_by_country = {}
    for u in University.objects.all().order_by('country', 'name'):
        country = (u.country or '').strip() or 'Other'
        if country not in universities_by_country:
            universities_by_country[country] = []
        universities_by_country[country].append(u)
    # Sort countries alphabetically, "Other" last
    sorted_countries = sorted(universities_by_country.keys(), key=lambda c: (c == 'Other', c))
    context = {
        'universities_by_country': [(country, universities_by_country[country]) for country in sorted_countries],
    }
    return render(request, 'root/university.html', context)

def university_details(request, id):
    university = get_object_or_404(University, id=id)
    programs = Program.objects.filter(subjects__university=university).distinct().order_by('name')
    return render(request, 'root/university-details.html', {
        'university': university,
        'programs': programs,
    })


def get_subjects(request, program_id, u_id):
    subjects = Subject.objects.filter(program_id=program_id, university=u_id).select_related('university', 'program')
    subject_list = [{
                    'id': subject.id,
                    'name': subject.name,
                    'fee': subject.fee,
                    'university': subject.university.name,
                    'program': subject.program.name,
                    'intake': subject.intake,
                    'course_type': subject.course_type,
                    'course_period': subject.course_period,
                    } for subject in subjects]
    return JsonResponse({'subjects': subject_list}, safe=False)


def _application_form_context(programs=None, universities=None, form_data=None):
    """Build context for application form with optional repopulation."""
    if programs is None:
        programs = Program.objects.all()
    if universities is None:
        universities = University.objects.all()
    ctx = {'programs': programs, 'universities': universities}
    if form_data:
        ctx['form_data'] = form_data
        # When repopulating, provide subjects for selected program+university so subject dropdown can be restored
        pid, uid = form_data.get('program'), form_data.get('university')
        if pid and uid:
            try:
                ctx['repopulate_subjects'] = list(
                    Subject.objects.filter(program_id=pid, university_id=uid)
                    .select_related('university', 'program')
                    .values('id', 'name', 'fee')
                )
                ctx['selected_subject_id'] = form_data.get('subject')
            except (ValueError, TypeError):
                pass
    return ctx


@require_http_methods(["GET", "POST"])
def application(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        reference_code = (request.POST.get('reference_code') or '').strip() or None
        phone = (request.POST.get('phone') or '').strip()
        email = (request.POST.get('email') or '').strip()
        gender = (request.POST.get('gender') or '').strip()
        passport_number = (request.POST.get('passport_number') or '').strip()
        date_of_birth_str = (request.POST.get('date_of_birth') or '').strip()
        highest_qualification = (request.POST.get('highest_qualification') or '').strip()
        year_of_passing = (request.POST.get('year_of_passing') or '').strip()
        english_certificate_raw = (request.POST.get('english_language_certificate') or '').strip().lower()
        english_language_certificate = english_certificate_raw in ('true', '1', 'yes')
        program_id = request.POST.get('program')
        university_id = request.POST.get('university')
        subject_id = request.POST.get('subject')
        certificate_upload = request.FILES.get('certificate_upload')
        passport_information_page = request.FILES.get('passport_information_page')

        form_data = {
            'name': name, 'reference_code': reference_code, 'phone': phone, 'email': email,
            'gender': gender, 'passport_number': passport_number, 'date_of_birth': date_of_birth_str,
            'highest_qualification': highest_qualification, 'year_of_passing': year_of_passing,
            'english_language_certificate': english_language_certificate,
            'program': program_id, 'university': university_id, 'subject': subject_id,
        }

        # Resolve program, university, subject (404 -> invalid selection)
        try:
            if not program_id or not university_id or not subject_id:
                raise Http404("Missing selection")
            program = get_object_or_404(Program, id=program_id)
            university = get_object_or_404(University, id=university_id)
            subject = get_object_or_404(Subject, id=subject_id)
        except Http404:
            messages.error(request, "Invalid selection for program, university, or subject.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))

        # Subject must belong to the chosen program and university
        if subject.program_id != program.id or subject.university_id != university.id:
            messages.error(request, "The selected subject does not match the chosen program and university.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))

        # Required file uploads
        if not certificate_upload:
            messages.error(request, "Please upload your certificate.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))
        if not passport_information_page:
            messages.error(request, "Please upload your passport information page.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))

        # Parse date of birth
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        if not date_of_birth:
            messages.error(request, "Please enter a valid date of birth.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))

        # Required fields
        if not (name and phone and email and gender and passport_number):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))

        try:
            app = Application(
                name=name,
                reference_code=reference_code,
                phone=phone,
                email=email,
                gender=gender,
                passport_number=passport_number,
                date_of_birth=date_of_birth,
                highest_qualification=highest_qualification,
                year_of_passing=year_of_passing,
                english_language_certificate=english_language_certificate,
                program=program,
                university=university,
                subject=subject,
                certificate_upload=certificate_upload,
                passport_information_page=passport_information_page,
            )
            app.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('core:application_success')
        except (ValidationError, IntegrityError) as e:
            logger.warning("Application save error: %s", e)
            messages.error(request, "An error occurred while submitting your application. Please check your input and try again.")
            return render(request, 'root/application.html', _application_form_context(form_data=form_data))

    return render(request, 'root/application.html', _application_form_context())


def application_success(request):
    return render(request, 'root/success.html')


def destinations(request):
    destinations_list = Destination.objects.filter(is_active=True).order_by('order', 'name')
    return render(request, 'root/destinations.html', {'destinations': destinations_list})


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    return render(request, 'root/destination-detail.html', {'destination': destination})


def scholarship(request):
    scholarships = Scholarship.objects.all()
    return render(request, 'root/scholarship.html', {'scholarships': scholarships})


def events(request):
    events_list = Event.objects.filter(is_active=True, is_upcoming=True).order_by('event_date')
    event_type = request.GET.get('type', '').strip()
    if event_type:
        events_list = events_list.filter(event_type=event_type)
    return render(request, 'root/events.html', {
        'events': events_list,
        'current_type': event_type,
        'event_type_choices': Event.EVENT_TYPE_CHOICES,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_active=True)
    return render(request, 'root/event-detail.html', {'event': event})


@require_http_methods(["POST"])
def event_book(request, slug):
    """AJAX endpoint to book a seat for an event. Returns JSON."""
    event = get_object_or_404(Event, slug=slug, is_active=True)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    institution_name = (data.get('institution_name') or '').strip()
    district_name = (data.get('district_name') or '').strip()
    t_shirt_size = (data.get('t_shirt_size') or '').strip().lower()
    inquery = (data.get('inquery') or '').strip()
    # Keep seats for backward compatibility; default to 1 when not provided
    try:
        seats = int(data.get('seats') or 1)
        if seats < 1:
            seats = 1
    except (ValueError, TypeError):
        seats = 1

    valid_sizes = {c[0] for c in EventBooking.T_SHIRT_SIZE_CHOICES}

    if not (name and email and phone):
        return JsonResponse({'error': 'Please fill in your name, email, and phone number.'}, status=400)
    if not district_name:
        return JsonResponse({'error': 'Please enter your district name.'}, status=400)
    if t_shirt_size not in valid_sizes:
        return JsonResponse({'error': 'Please select a T-shirt size.'}, status=400)

    EventBooking.objects.create(
        event=event,
        name=name,
        email=email,
        phone=phone,
        district_name=district_name,
        t_shirt_size=t_shirt_size,
        seats=seats,
        institution_name=institution_name or None,
        inquery=inquery or None,
    )
    return JsonResponse({'success': True, 'message': f'Your seat{"s have" if seats > 1 else " has"} been booked for {event.title}!'})


def search(request):
    query = request.GET.get('q', '')
    results = {'universities': [], 'blogs': [], 'events': []}
    if query:
        results['universities'] = University.objects.filter(name__icontains=query)[:5]
        results['blogs'] = Blog.objects.filter(is_published=True).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:5]
        results['events'] = Event.objects.filter(is_active=True, is_upcoming=True).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
    return render(request, 'root/search.html', {'query': query, 'results': results})


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    if not email:
        messages.error(request, 'Please enter a valid email address.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    try:
        NewsletterSubscriber.objects.create(email=email)
        messages.success(request, 'Thank you for subscribing!')
    except IntegrityError:
        messages.info(request, 'You are already subscribed.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def robots_txt(request):
    """
    Serve robots.txt, optionally driven by SiteSettings.

    Priority:
    1. If SiteSettings.robots_txt_content is set, serve it as-is.
    2. Else, serve a simple default that allows all and, if a sitemap URL
       is configured, adds a Sitemap directive.
    """
    settings_obj = SiteSettings.get_settings()
    content = (settings_obj.robots_txt_content or "").strip()
    if not content:
        lines = ["User-agent: *", "Disallow:"]
        if settings_obj.sitemap_url:
            lines.append(f"Sitemap: {settings_obj.sitemap_url}")
        content = "\n".join(lines) + "\n"
    return HttpResponse(content, content_type="text/plain")
