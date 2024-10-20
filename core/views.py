from django.shortcuts import render
from .models import *

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

def application(request):
    return render(request, 'root/application.html')