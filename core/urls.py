from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path('', views.index, name="index"),
    path('services/', views.services, name="services"),
    path('service-details/', views.service_details, name="service_details"),
    path('testimonial/', views.testimonial, name="testimonial"),
    path('faq/', views.faq, name="faq"),
    path('about-us/', views.about, name="about"),
    path('contact-us/', views.contact, name="contact"),
    path('blog/', views.blog, name="blog"),
    path('blog-details/', views.blog_details, name="blog-details"),
    path('videos/', views.videos, name="videos"),
    path('university/', views.university, name="university"),
    path('university-details/<int:id>/', views.university_details, name="university-details"),
    path('application/', views.application, name="application")
]
