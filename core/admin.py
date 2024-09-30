# admin.py
from django.contrib import admin
from .models import University, Program, Subject
from django.utils.translation import gettext_lazy as _

class ProgramInline(admin.TabularInline):
    model = Program
    extra = 1

class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 1

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'title')
    search_fields = ('name', 'title', 'description')  # search by university name, title, or description
    list_filter = ('name',)  # filter by university name
    inlines = [ProgramInline]

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('university', 'program_type', 'name')
    search_fields = ('name', 'program_type')  # search by program name or type
    list_filter = ('university', 'program_type')  # filter by university or program type
    inlines = [SubjectInline]

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('program', 'name', 'course_period', 'start_date', 'fee', 'course_type')
    search_fields = ('name', 'course_period', 'start_date')  # search by subject name, course period, or start date
    list_filter = ('program', 'course_type')  # filter by program or course type

admin.site.register(University, UniversityAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Subject, SubjectAdmin)

admin.site.site_header = _('Education Management Admin')  # change the site header
admin.site.site_title = _('Education Management Admin')  # change the site title
admin.site.index_title = _('Education Management Admin') 