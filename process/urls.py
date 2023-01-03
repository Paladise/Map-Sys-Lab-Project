from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('atlas', views.atlas, name="atlas"),
    path('capture', views.capture, name="capture"),
    path('get_id', views.get_id, name="get_id")
]

app_name = "process"