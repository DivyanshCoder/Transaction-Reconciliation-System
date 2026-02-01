from django.urls import path, include
from .views import upload_files
from django.http import HttpResponse

urlpatterns = [
    # path("", upload_files, name="upload_files"),
    path("", lambda r: HttpResponse("PAYMENT OPERATIONS WORKING")),
]