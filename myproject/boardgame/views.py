from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from .models import *

from .forms import * 

# Create your views here.

class indexView(View):
    def get(self, request):
        return render(request, 'index.html')


class ReservationFormView(View):
    template_name = "reservation_form.html"

    def get(self, request):

        form = ReservationForm()
        return render(request, self.template_name, {"form": form})
    

    def post(self, request):

        form = ReservationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('Reservation_form')  # กลับไปหน้าจองโต๊ะ



    

        
