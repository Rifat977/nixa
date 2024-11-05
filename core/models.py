from django.db import models

class University(models.Model):
    """
    Represents a University with its details.
    """
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='university_logos', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='university_images', null=True, blank=True)

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "  University"

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
        verbose_name_plural = " Program"

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
    start_date = models.DateField()  # month
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subject"

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

class Video(models.Model):
    title = models.CharField(max_length=255) 
    video_url = models.URLField(max_length=200) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='testimonials/avatars/')
    content = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.designation}"