from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'recorder', views.RecorderViewSet, basename='recorder')
router.register(r'recording-camera', views.RecordingCameraViewSet, basename='recording-camera')

urlpatterns = [
    url(r'^', include(router.urls)),
]