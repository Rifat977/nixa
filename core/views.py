from django.shortcuts import render

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
    return render(request, 'root/university.html')