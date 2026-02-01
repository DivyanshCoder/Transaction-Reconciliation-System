from django.urls import path, include
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('', views.upload_files, name="upload_files"),
]