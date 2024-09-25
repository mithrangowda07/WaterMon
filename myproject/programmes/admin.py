from django.contrib import admin
from .models import UGProgramme, PGProgramme

admin.site.register(UGProgramme)
admin.site.register(PGProgramme)

class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hod_name', 'year_started')
    search_fields = ('name', 'hod_name')