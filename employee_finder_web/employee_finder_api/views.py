from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.generic import View
from employee_finder_api.models import Employees

# Create your views here.

class EmployeeView(View):
    def get(self, request, *args, **kwargs):
        # <http>://<ip>:<port>/employee/?param1=value1&param2=value2&...&paramN=valueN
        
        data = Employees.objects.filter(
            position__contains=request.GET["position"],
            origin__contains=request.GET["origin"]      
        )
        data_json = serializers.serialize("json", data)

        return HttpResponse(data_json, content_type="application/json")

