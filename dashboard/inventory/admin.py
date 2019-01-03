from django.contrib import admin

# Register your models here.
from .models import *
 
class ScheduleIntervalsInline(admin.TabularInline):
    model = ScheduleIntervals
    extra = 1

class ScheduleAdmin(admin.ModelAdmin):
    inlines = [
        ScheduleIntervalsInline,
    ]
    model = Schedule

class CameraAdmin(admin.ModelAdmin):
    model = Camera

admin.site.register(Camera, CameraAdmin)
admin.site.register(Schedule, ScheduleAdmin)