from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from . import serializer
from .recorder import GetRecorder


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class RecorderViewSet(viewsets.ViewSet):    
    #authentication_classes = (authentication.TokenAuthentication,)
    #permission_classes = (permissions.IsAdminUser,)

    def list(self, request):
        mgr = GetRecorder()
        recorders = [rr.recorder for rr in mgr.recorders.values()]
        return Response(serializer.RecorderSerializer(recorders, many=True, context={'request': request}).data)

#    def retrieve(self, request, pk=None):
#        queryset = User.objects.all()
#        user = get_object_or_404(queryset, pk=pk)
#        serializer = UserSerializer(user)
#        return Response(serializer.data)