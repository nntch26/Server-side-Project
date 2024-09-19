from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from .models import *

# Create your views here.

class indexView(View):
    def get(self, request):
        # <view logic>
        return render(request, 'index.html')
    