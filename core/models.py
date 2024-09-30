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
    UNIVERSITY_PROGRAM_TYPES = [
        ('BACHELOR', 'Bachelor'),
        ('MASTER', 'Master'),
        ('PHD', 'PhD'),
        ('Foundation', 'Foundation'),
        ('Pharmacy', 'Pharmacy'),
    ]

    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='programs')
    program_type = models.CharField(max_length=10, choices=UNIVERSITY_PROGRAM_TYPES)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = " Program"

    def __str__(self):
        return f"{self.university.name} - {self.get_program_type_display()}"


class Subject(models.Model):
    """
    Represents a Subject offered by a Program.
    """
    COURSE_TYPES = [
        ('Coursework', 'Coursework'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    course_period = models.CharField(max_length=255)
    start_date = models.CharField(max_length=10)  # month
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subject"

    def __str__(self):
        return f"{self.program.name} - {self.name}"