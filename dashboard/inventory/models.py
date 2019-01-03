from django.db import models
from django.conf import settings
from dashboard.core import abstract_models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

# Create your models here.
class Schedule(abstract_models.ModelAuditDates):
    name = abstract_models.EntityNameField(verbose_name=_('Schedule Name'))
    description = abstract_models.DescrField()

    class Meta:
        app_label = 'inventory'
        ordering = ['name']
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')

class ScheduleIntervals(abstract_models.ObjectIdentityWeakMixin, abstract_models.ModelAuditDates):
    schedule = models.ForeignKey(
         'Schedule', related_name='intervals', verbose_name=_("Schedule"), on_delete=models.CASCADE)
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    days_of_week = models.PositiveSmallIntegerField(verbose_name=_('Days of week Bitmask'), validators=[MaxValueValidator(255)])
 
    class Meta:
        app_label = 'inventory'
        ordering = ['start_time', 'end_time']
        unique_together = ('start_time', 'end_time')
        verbose_name = _('Schedule Interval')
        verbose_name_plural = _('Schedule Intervals')

class Camera(abstract_models.ModelAuditDates):
    name = abstract_models.EntityNameField(verbose_name=_('Camera Name'))
    description = abstract_models.DescrField()
    url = models.URLField(verbose_name=_('RTSP URL'))
    password = models.CharField(verbose_name=_('Password'), max_length=30, blank=True, null=True)
    schedule = models.ForeignKey(
         'Schedule', related_name='cameras', verbose_name=_("Schedule"), on_delete=models.PROTECT)
    record_length = models.PositiveSmallIntegerField(verbose_name=_('Record length'), default=15, 
         validators=[MinValueValidator(5), MaxValueValidator(60)],
         help_text=_('Video record split length (in minutes)'))
    snapshot_interval = models.PositiveSmallIntegerField(verbose_name=_('Snapshot interval'), default=0,
         validators=[MaxValueValidator(3600)],
         help_text=_('Snapshot interval (in seconds)'))

    class Meta:
        app_label = 'inventory'
        ordering = ['name']
        verbose_name = _('Camera')
        verbose_name_plural = _('Cameras')
