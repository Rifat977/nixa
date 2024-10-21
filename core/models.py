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
    LEVEL_OF_STUDY_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]

    name = models.CharField(max_length=255)
    reference_code = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    passport_number = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    ssc_year = models.IntegerField()
    ssc_result = models.CharField(max_length=50)
    hsc_year = models.IntegerField()
    hsc_result = models.CharField(max_length=50)
    bachelor_year = models.IntegerField(blank=True, null=True)
    bachelor_result = models.CharField(max_length=50, blank=True, null=True)
    level_of_study = models.CharField(max_length=10, choices=LEVEL_OF_STUDY_CHOICES)
    english_language_certificate = models.CharField(max_length=255, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    certificate_upload = models.FileField(upload_to='certificates/')
    passport_information_page = models.FileField(upload_to='passports/')

    def __str__(self):
        return f"{self.name} - {self.program.name} - {self.university.name}"
