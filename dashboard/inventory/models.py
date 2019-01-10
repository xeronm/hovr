from django.db import models
from django.conf import settings
from dashboard.core import abstract_models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.db.models import Q, F
from django.template import Context, Template
from . import CameraState, RecorderMethod
import datetime

ALL_WEEK_DAYS = 0x7F

# Create your models here.
class Schedule(abstract_models.ObjectIdentityNameMixin, abstract_models.ModelAuditDates):
    name = abstract_models.EntityNameField(verbose_name=_('Schedule Name'))
    description = abstract_models.DescrField()

    class Meta:
        app_label = 'inventory'
        ordering = ['name']
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')

class RecorderProfile(abstract_models.ObjectIdentityNameMixin, abstract_models.ModelAuditDates):
    name = abstract_models.EntityNameField(verbose_name=_('Recorder Profile'))
    description = abstract_models.DescrField()

    method = models.PositiveSmallIntegerField(verbose_name=_("Method"), choices=RecorderMethod.CHOICES)

    interval = models.PositiveSmallIntegerField(verbose_name=_('Record interval'), default=0, 
         validators=[MaxValueValidator(3600)],
         help_text=_('Record interval (in seconds). Means interval between snapshots or video record piece length'))
    filename_template = models.CharField(verbose_name=_('Filename template'), max_length=255,
         help_text=_('Record filename template (django)') )
    url_template = models.CharField(verbose_name=_('URL template'), max_length=255,
         help_text=_('URL template (django)') )

    class Meta:
        app_label = 'inventory'
        ordering = ['name']
        verbose_name = _('RecorderProfile')
        verbose_name_plural = _('RecorderProfiles')

    def render_filename(self, **kwargs):
        return Template(self.filename_template).render(Context(kwargs))

    def render_url(self, **kwargs):
        return Template(self.url_template).render(Context(kwargs))

class RecorderArguments(abstract_models.ObjectIdentityWeakMixin, abstract_models.ModelAuditDates):
    recorder_profile = models.ForeignKey(
         'RecorderProfile', related_name='arguments', verbose_name=_("Recorder Profile"), on_delete=models.CASCADE)
    order_no = models.PositiveSmallIntegerField(verbose_name=_('Order Number'))
    argument = models.CharField(verbose_name=_('Argument'), max_length=ALL_WEEK_DAYS)
    is_template = models.BooleanField(_('Is Template'), default=False, 
        help_text=_('True if argument is a template (django)'))

    class Meta:
        app_label = 'inventory'
        ordering = ['recorder_profile', 'order_no']
        unique_together = ('recorder_profile', 'order_no')
        verbose_name = _('RecorderArgument')
        verbose_name_plural = _('RecorderArguments')

    def render(self, **kwargs):
        if self.is_template:
            return Template(self.argument).render(Context(kwargs))
        else:
            return self.argument

class ScheduleIntervals(abstract_models.ObjectIdentityWeakMixin, abstract_models.ModelAuditDates):
    schedule = models.ForeignKey(
         'Schedule', related_name='intervals', verbose_name=_("Schedule"), on_delete=models.CASCADE)
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    week_days = models.PositiveSmallIntegerField(verbose_name=_('Days of week Bitmask'), default=255,
         validators=[MaxValueValidator(ALL_WEEK_DAYS)])
 
    class Meta:
        app_label = 'inventory'
        ordering = ['start_time', 'end_time']
        unique_together = ('schedule', 'start_time', 'end_time')
        verbose_name = _('Schedule Interval')
        verbose_name_plural = _('Schedule Intervals')

    @classmethod
    def qsActiveIntervals(cls, date_time):
        bitwd = 1 << date_time.weekday()
        return ScheduleIntervals.objects.filter(start_time__lte=date_time, end_time__gte=date_time, week_days=F('week_days').bitand((~bitwd) & ALL_WEEK_DAYS) + bitwd )

    def checkInterval(self, date_time):
        bitwd = 1 << date_time.weekday()
        return self.start_time <= date_time.time() and self.end_time >= date_time.time() and (self.week_days & bitwd) == bitwd

    def nextSwitchTime(self, date_time):
        wd = date_time.weekday()
        bitwd = 1 << wd

        dt_flag = (self.start_time <= date_time.time() and self.end_time >= date_time.time())
        time_inv = None
        if (self.start_time.hour, self.start_time.minute) != (0, 0) or (self.end_time.hour, self.end_time.minute) != (23, 59):
            if dt_flag:
                time_inv = self.end_time
            else:
                time_inv = self.start_time

        wd_inv = None
        wd_flag = True
        if (self.week_days & ALL_WEEK_DAYS < ALL_WEEK_DAYS):
            wd_flag = (self.week_days & bitwd) == bitwd
            wd_inv = wd + 1;
            while (wd_inv % 7) != wd:
                bitwd_inv = 1 << (wd_inv % 7)
                if ((self.week_days & bitwd_inv) == bitwd_inv) != (wd_flag and dt_flag):
                    break
                wd_inv += 1;
            assert((wd_inv % 7) != wd)

        if time_inv is None and wd_inv is None:
            return None

        next_switch = None
        if wd_flag and dt_flag:
            next_switch = date_time.replace(hour=self.end_time.hour, minute=self.end_time.minute, second=self.end_time.second)
            if not wd_inv is None and time_inv is None:
                next_switch = next_switch + datetime.timedelta(days=wd_inv-wd-1)
        else:
            next_switch = date_time.replace(hour=self.start_time.hour, minute=self.start_time.minute, second=self.start_time.second)
            if not (wd_flag and date_time.time() <= self.start_time):
                next_switch = next_switch + datetime.timedelta(days=wd_inv-wd)

        return next_switch
        
class Camera(abstract_models.ObjectIdentityNameMixin, abstract_models.ModelAuditDates):
    name = abstract_models.EntityNameField(verbose_name=_('Camera Name'))
    description = abstract_models.DescrField()
    state = models.PositiveSmallIntegerField(verbose_name=_("State"), choices=CameraState.CHOICES, default=CameraState.ENABLED)
    address = models.URLField(verbose_name=_('Address'), help_text=_('IP address or FQDN'))
    user_name = models.CharField(verbose_name=_('User Name'), max_length=30, blank=True, null=True)
    password = models.CharField(verbose_name=_('Password'), max_length=30, blank=True, null=True)
    schedule = models.ForeignKey(
         'Schedule', related_name='cameras', verbose_name=_("Schedule"), on_delete=models.PROTECT)
    recorder_profile = models.ForeignKey(
         'RecorderProfile', related_name='cameras', verbose_name=_("Recorder Profile"), on_delete=models.PROTECT)
    recorder_profile2 = models.ForeignKey(
         'RecorderProfile', related_name='cameras2', verbose_name=_("Recorder Profile (secondary)"), on_delete=models.PROTECT,
         null=True, blank=True)

    class Meta:
        app_label = 'inventory'
        ordering = ['name']
        verbose_name = _('Camera')
        verbose_name_plural = _('Cameras')
