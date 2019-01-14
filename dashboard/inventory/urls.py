from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'camera', views.CameraViewSet)
router.register(r'schedule', views.ScheduleViewSet)
router.register(r'schedule-intervals', views.ScheduleIntervalsViewSet)
router.register(r'recorder-profile', views.RecorderProfileViewSet)
router.register(r'recorder-arguments', views.RecorderArgumentsViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]