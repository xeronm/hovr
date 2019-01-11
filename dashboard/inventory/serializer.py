from . import models
from rest_framework import serializers

class ScheduleIntervalsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ScheduleIntervals
        fields = ('url', 'schedule', 'start_time', 'end_time', 'week_days')

class ScheduleIntervalsSerializerInline(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ScheduleIntervals
        fields = ('url', 'start_time', 'end_time', 'week_days')

class ScheduleSerializer(serializers.HyperlinkedModelSerializer):
    intervals = ScheduleIntervalsSerializerInline(many=True)
    class Meta:
        model = models.Schedule
        fields = ('url', 'name', 'description', 'intervals')

class RecorderArgumentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RecorderArguments
        fields = ('url', 'recorder_profile', 'order_no', 'argument', 'is_template')

class RecorderArgumentsSerializerInline(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RecorderArguments
        fields = ('url', 'order_no', 'argument', 'is_template')

class RecorderProfileSerializer(serializers.HyperlinkedModelSerializer):
    arguments = RecorderArgumentsSerializerInline(many=True)
    class Meta:
        model = models.RecorderProfile
        fields = ('url', 'name', 'description', 'method', 'interval', 'filename_template', 'url_template', 'arguments')

class CameraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Camera
        fields = ('url', 'name', 'description', 'state', 'address', 'user_name', 'password', 'schedule', 'recorder_profile', 'recorder_profile2')

