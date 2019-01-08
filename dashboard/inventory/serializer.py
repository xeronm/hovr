from . import models
from rest_framework import serializers

class ScheduleIntervalsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ScheduleIntervals
        fields = ('url', 'start_time', 'end_time', 'week_days')

class ScheduleSerializer(serializers.HyperlinkedModelSerializer):
    intervals = ScheduleIntervalsSerializer(many=True)
    class Meta:
        model = models.Schedule
        fields = ('url', 'name', 'description', 'intervals')

class RecorderArgumentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RecorderArguments
        fields = ('url', 'order_no', 'argument', 'is_template')

class RecorderProfileSerializer(serializers.HyperlinkedModelSerializer):
    arguments = RecorderArgumentsSerializer(many=True)
    class Meta:
        model = models.RecorderProfile
        fields = ('url', 'name', 'description', 'method', 'interval', 'filename_template', 'url_template', 'arguments')

class CameraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Camera
        fields = ('url', 'name', 'description', 'state', 'address', 'user_name', 'password', 'schedule', 'recorder_profile', 'recorder_profile2')

