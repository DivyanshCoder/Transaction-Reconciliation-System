from django.urls import path, include
from PaymentOperations.views import upload_files

urlpatterns = [
    path("", upload_files, name="upload_files"),
]