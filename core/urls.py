from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path('', views.index, name="index"),
    path('services/', views.services, name="services"),
    path('service-details/', views.service_details, name="service_details"),
    path('faq/', views.faq, name="faq"),
    path('about-us/', views.about, name="about"),
    path('contact-us/', views.contact, name="contact"),
    path('book-consultation/', views.consultation, name="consultation"),
    path('book-consultation/success/', views.consultation_success, name="consultation_success"),
    path('blog/', views.blog, name="blog"),
    path('blog-details/<int:pk>/', views.blog_details, name="blog-details"),
    path('our-gallery/', views.gallery, name="gallery"),

    path('login/', views.user_login, name="login"),
    path('registration/', views.registration, name="registration"),
    path('logout/', views.user_logout, name='logout'),


    path('university/', views.university, name="university"),
    path('university-details/<int:id>/', views.university_details, name="university-details"),
    path('get-subjects/<int:program_id>/<int:u_id>/', views.get_subjects, name='get_subjects'),

    path('application/success/', views.application_success, name='application_success'),
    path('application/', views.application, name="application"),

    path('destinations/', views.destinations, name='destinations'),
    path('destinations/<slug:slug>/', views.destination_detail, name='destination-detail'),
    path('scholarship/', views.scholarship, name='scholarship'),
    path('events/', views.events, name='events'),
    path('events/<slug:slug>/', views.event_detail, name='event-detail'),
    path('events/<slug:slug>/book/', views.event_book, name='event-book'),
    path('search/', views.search, name='search'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
