from django.urls import re_path
from django.urls import path
from .views import EmployeeView

urlpatterns = [
    path("employee/", EmployeeView.as_view())
]