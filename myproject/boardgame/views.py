from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse, HttpResponseNotAllowed
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
        tables = Table.objects.all()
        pack = {'tables': tables}
        return render(request, 'cashier-pay.html', pack)



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
  

# Dashboard 

class DashboardView(View):

    template_name = "admin/dashboard.html"

    def get(self, request):
        return render(request, self.template_name)


class DashboardBoardgameView(View):
    template_name = "admin/dashboard-boardgame.html"

    def get(self, request):
        product_list = BoardGames.objects.all()
        return render(request, self.template_name, {"product_list": product_list})



class DashboardBoardgameAddView(View):
    template_name = "admin/boardgame_add.html"

    def get(self, request):
        form = BoardGamesForm()
        return render(request, self.template_name, {"form": form})
    

    def post(self, request):
        form = BoardGamesForm(request.POST , request.FILES)

        if form.is_valid():
            form.save()
            return redirect('des-boardgame')
        
        return render(request, self.template_name, {"form": form})


class DashboardBoardgameDelView(View):
    def get(self, request, game_id):

        project_data = BoardGames.objects.get(pk=game_id)
        project_data.delete()
        return redirect('des-boardgame')


class DashboardBoardgameEditView(View):
    template_name = "admin/boardgame_edit.html"

    def get(self, request, game_id):

        # ดึง obj มาแสดงในฟอร์มด้วย
        boardgame = BoardGames.objects.get(pk=game_id)
        form = BoardGamesForm(instance=boardgame)

        return render(request, self.template_name, {"form": form})
    

    def post(self, request, game_id):

        # ดึง obj ที่จะแก้ไข
        boardgame = BoardGames.objects.get(pk=game_id)

        # ส่ง instance ของ obj ที่จะถูกแก้ไขเข้าไปในฟอร์ม
        form = BoardGamesForm(request.POST , request.FILES, instance=boardgame)

        if form.is_valid():
            form.save()
            return redirect('des-boardgame')
        
        return render(request, self.template_name, {"form": form})


class DashboardMemberView(View):
    template_name = "admin/dashboard-member.html"

    def get(self, request):
        member_list = User.objects.all()
        return render(request, self.template_name, {"member_list": member_list})

class DashboardMemberDelView(View):
    def get(self, request, mem_id):

        member_data = User.objects.get(pk=mem_id)
        member_data.delete()
        return redirect('des-member')
    

# profile
class ProfileView(View):
    def get(self, request):
        return render(request, 'profile.html')