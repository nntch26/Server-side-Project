from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from .models import *

from .forms import * 

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm  

# Create your views here.

class indexView(View):
    def get(self, request):
        return render(request, 'index.html')


# Reservation
class ReservationFormView(View):
    template_name = "reservation_form.html"

    def get(self, request):

        form = ReservationForm()
        return render(request, self.template_name, {"form": form})
    

    def post(self, request):

        form = ReservationForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user  # กำหนดผู้ใช้ที่ล็อกอิน
            form.save()

            return redirect('Reservation_form')  # กลับไปหน้าจองโต๊ะ
        
        return render(request, self.template_name, {"form": form})


# cashier     
class CashierView(View):
    def get(self, request):
        return render(request, 'cashier.html')



# login & register

class LoginView(View):

    template_name = "login.html"

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template_name, {"form":form})
    
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        
        return render(request, self.template_name, {"form":form})
    

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {"form": form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user1 = form.save()

            UserDetail.objects.create(
                user = user1, #ยัด obj user เข้าไป
                phone_number = form.cleaned_data['phone_number']
            )
            return redirect('login')
        
        return render(request, 'register.html', {"form": form})
    

    


class LogoutView(View):
    
    def get(self, request):
        logout(request)
        return redirect('index')
  
    

