# admin.py
from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import Group

# admin.site.unregister(Group)
# admin.site.register(User)


class CustomAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'passport_number', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'is_superuser')
    
    
    search_fields = ('email', 'first_name', 'last_name', 'passport_number')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(Account, CustomAdmin)


# class ProgramInline(admin.TabularInline):
#     model = Program
#     extra = 1

# class SubjectInline(admin.TabularInline):
#     model = Subject
#     extra = 1

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'title')
    search_fields = ('name', 'title', 'description')  # search by university name, title, or description
    list_filter = ('name',)  # filter by university name
    # inlines = [ProgramInline]

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name',) # filter by university or program type
    # inlines = [SubjectInline]

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('program', 'name', 'course_period', 'intake', 'fee', 'course_type')
    search_fields = ('name', 'course_period')  # search by subject name, course period, or start date
    list_filter = ('program', 'course_type') 

admin.site.register(University, UniversityAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Application)
admin.site.register(GalleryImage)
admin.site.register(Video)
admin.site.register(Testimonial)

admin.site.site_header = _('Nixaglobal Adminstrator')  # change the site header
admin.site.site_title = _('Nixaglobal Adminstrator')  # change the site title
admin.site.index_title = _('Nixaglobal Adminstrator') 

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'is_published')
    search_fields = ('title', 'content')
    list_filter = ('is_published', 'published_at')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)