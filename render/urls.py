from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<id>/', views.model, name='model'),
    path('copy/<id>', views.copy_images, name='copy'),
    path('create/<id>', views.create_bash_script, name='create'),
    path('process/<id>', views.process_images, name='process')
]

app_name = "render"