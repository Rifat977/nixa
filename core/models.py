from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class Account(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    passport_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(Group, related_name='account_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='account_permissions', blank=True)

    def is_email_verification_token_expired(self):
        if self.email_verification_sent_at:
            expiration_time = timezone.timedelta(hours=24)  # 24 hours validity
            return self.email_verification_sent_at + expiration_time < timezone.now()
        return True

    def generate_password_reset_token(self):
        token = get_random_string(length=32)
        self.password_reset_token = token
        self.save()
        return token

    class Meta:
        verbose_name = "User Accounts"
        verbose_name_plural = "          User Accounts"


class University(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='university_logos', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='university_images', null=True, blank=True)

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "         University"

    def __str__(self):
        return self.name


class Program(models.Model):
    """
    Represents a Program offered by a University.
    """
    # UNIVERSITY_PROGRAM_TYPES = [
    #     ('BACHELOR', 'Bachelor'),
    #     ('MASTER', 'Master'),
    #     ('PHD', 'PhD'),
    #     ('Foundation', 'Foundation'),
    #     ('Pharmacy', 'Pharmacy'),
    # ]

    # university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='programs')
    # program_type = models.CharField(max_length=10, choices=UNIVERSITY_PROGRAM_TYPES)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "        Programs"

    def __str__(self):
        return f"{self.name}"


class Subject(models.Model):
    """
    Represents a Subject offered by a Program.
    """
    COURSE_TYPES = [
        ('Coursework', 'Coursework'),
    ]

    university = models.ForeignKey(University, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    course_period = models.CharField(max_length=255)
    intake = models.CharField(max_length=255)
    fee = models.CharField(max_length=255)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "       Subject"

    def __str__(self):
        return f"{self.program.name} - {self.name}"


class Application(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=255)
    reference_code = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15)  # Example regex for phone number validation
    email = models.EmailField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    passport_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    highest_qualification = models.CharField(max_length=255)
    year_of_passing = models.CharField(max_length=10)
    english_language_certificate = models.BooleanField(default=False)  # Use a BooleanField to represent yes/no
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    certificate_upload = models.FileField(upload_to='certificates/')
    passport_information_page = models.FileField(upload_to='passports/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.name} for {self.program.name} at {self.university.name}"

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = '      Applications'



class GalleryImage(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True) 
    image_primary = models.ImageField(upload_to='gallery_images/')
    image_1 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f'Gallery Image {self.id}'

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = '     Galleries'


class Video(models.Model):
    title = models.CharField(max_length=255) 
    video_url = models.URLField(max_length=200) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = '    Videos'


class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='testimonials/avatars/')
    content = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.designation}"

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = '  Testimonials'



from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tags'
        verbose_name_plural = ' Tags'


class Blog(models.Model):
    title = models.CharField(max_length=200)  
    image = models.ImageField(upload_to='blog/')
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)  
    tags = models.ManyToManyField(Tag, related_name='blogs', blank=True)

    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

