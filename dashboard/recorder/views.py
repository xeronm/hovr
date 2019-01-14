from django.shortcuts import render
from django.http import HttpResponse, Http404

# Create your views here.
from rest_framework import viewsets
from . import serializer
from .recorder import GetRecorder


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class RecorderViewSet(viewsets.ViewSet):    

    def list(self, request):
        mgr = GetRecorder()
        recorders = [rr.recorder for rr in mgr.recorders.values()]
        return Response(serializer.RecorderSerializer(recorders, many=True, context={'request': request}).data)

    def retrieve(self, request, pk=None):
        mgr = GetRecorder()
        recorders = [rr.recorder for rr in mgr.recorders.values() if rr.recorder.id == int(pk)]
        if not recorders:
            raise Http404
        return Response(serializer.RecorderSerializer(recorders[0], context={'request': request}).data)

class RecordingCameraViewSet(viewsets.ViewSet):    

    def list(self, request):
        mgr = GetRecorder()
        return Response(serializer.RecordingCameraSerializer(mgr.recordingCameras().values(), many=True, context={'request': request}).data)

    def retrieve(self, request, pk=None):
        mgr = GetRecorder()
        obj = mgr.recordingCameras().get(int(pk))
        if not obj:
            raise Http404
        return Response(serializer.RecordingCameraSerializer(obj, context={'request': request}).data)
