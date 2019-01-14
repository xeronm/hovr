from django.shortcuts import render

# Create your views here.
from . import models
from rest_framework import viewsets
from . import serializer

class CameraViewSet(viewsets.ModelViewSet):
    queryset = models.Camera.objects.all()
    serializer_class = serializer.CameraSerializer

class ScheduleIntervalsViewSet(viewsets.ModelViewSet):
    queryset = models.ScheduleIntervals.objects.all()
    serializer_class = serializer.ScheduleIntervalsSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = models.Schedule.objects.all()
    serializer_class = serializer.ScheduleSerializer

class RecorderProfileViewSet(viewsets.ModelViewSet):
    queryset = models.RecorderProfile.objects.all()
    serializer_class = serializer.RecorderProfileSerializer

class RecorderArgumentsViewSet(viewsets.ModelViewSet):
    queryset = models.RecorderArguments.objects.all()
    serializer_class = serializer.RecorderArgumentsSerializer
