from rest_framework import serializers
from dashboard.inventory.models import RecorderProfile, Camera
from dashboard.inventory.serializer import RecorderProfileSerializer, CameraSerializer

class RecorderVLCSerializer(serializers.Serializer):
    is_playing = serializers.BooleanField(read_only=True)
    is_seekable = serializers.BooleanField(read_only=True)
    time = serializers.IntegerField(source='get_time', read_only=True)
    fps = serializers.IntegerField(source='get_fps', read_only=True)
    height = serializers.IntegerField(source='video_get_height', read_only=True)
    width = serializers.IntegerField(source='video_get_width', read_only=True)

class RecorderHTTPGetSerializer(serializers.Serializer):
    last_snapshot_time = serializers.DateTimeField(read_only=True)

class RecorderSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='id', lookup_url_kwarg='pk', read_only=True, view_name='recorder-detail')
    id = serializers.IntegerField(read_only=True)
    start_time = serializers.DateTimeField(read_only=True)
    stop_time = serializers.DateTimeField(read_only=True)
    record_url = serializers.CharField(read_only=True)
    record_path = serializers.CharField(read_only=True)
    record_filename = serializers.CharField(read_only=True)
    recorderVLC = RecorderVLCSerializer(read_only=True)
    recorderHTTPGet = RecorderHTTPGetSerializer(read_only=True)
    camera = serializers.HyperlinkedRelatedField(read_only=True, view_name='camera-detail')
    profile = serializers.HyperlinkedRelatedField(read_only=True, view_name='recorderprofile-detail')
    #profile = RecorderProfileSerializer(read_only=True) 
    #profile = serializers.PrimaryKeyRelatedField(queryset=RecorderProfile.objects.all())

class RecordingCameraSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='id', lookup_url_kwarg='pk', read_only=True, view_name='recording-camera-detail')
    camera = serializers.HyperlinkedRelatedField(read_only=True, view_name='camera-detail')
    recorders = RecorderSerializer(read_only=True, many=True)

#video_get_aspect_ratio
