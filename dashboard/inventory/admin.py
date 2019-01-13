from django.contrib import admin

# Register your models here.
from .models import *
 
class ScheduleIntervalsInline(admin.TabularInline):
    model = ScheduleIntervals
    extra = 1

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [
        ScheduleIntervalsInline,
    ]
    model = Schedule

class RecorderArgumentsInline(admin.TabularInline):
    model = RecorderArguments
    extra = 1

class RecorderProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'method', 'interval', 'recycle_timeout')
    inlines = [
        RecorderArgumentsInline,
    ]
    model = RecorderProfile

class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'address', 'state', 'schedule')
    model = Camera

admin.site.register(Camera, CameraAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(RecorderProfile, RecorderProfileAdmin)