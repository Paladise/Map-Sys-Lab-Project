from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<id>/', views.model, name='model'),
    path('copy/<id>', views.copy_images, name='copy')
]

app_name = "render"