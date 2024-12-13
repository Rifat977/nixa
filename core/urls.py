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
    path('blog-details/<int:pk>/', views.blog_details, name="blog-details"),
    path('videos/', views.videos, name="videos"),
    path('our-gallery/', views.gallery, name="gallery"),

    path('login/', views.user_login, name="login"),
    path('registration/', views.registration, name="registration"),
    path('logout/', views.user_logout, name='logout'),


    path('university/', views.university, name="university"),
    path('university-details/<int:id>/', views.university_details, name="university-details"),
    path('get-subjects/<int:program_id>/<int:u_id>/', views.get_subjects, name='get_subjects'),

    path('application/success/', views.application_success, name='application_success'),
    path('application/', views.application, name="application")
]
