from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from django.db.models.functions import Length, Upper, Concat
from .models import *

from .forms import * 

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm  

# Create your views here.

class indexView(View):

    template_name = "index.html"

    def get(self, request):
        boardgame_list = BoardGames.objects.all()[0:4]

        context = {
            "boardgame_list": boardgame_list
        }
        return render(request, self.template_name, context)


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
  

# Boardgame 

class BoardgameView(View):
    
    template_name = "boardgame.html"

    def get(self, request, cate_name=None):
        category_list = Categories.objects.all()
        boardgame_list = BoardGames.objects.all()

        form = BoardGamesForm()

        if cate_name:
            boardgame_list = BoardGames.objects.filter(category__name = cate_name)

        context = {
            "category_list" : category_list,
            "boardgame_list": boardgame_list,
            "form":form
        }
        return render(request, self.template_name, context)


# Search

class BoardgameSearchView (View):
    template_name = "boardgame.html"

    def get(self, request):
        data = request.GET.get('search') #ดึงค่าของ search จาก url ที่ส่งมา

        print(data)
        boardgame_list = BoardGames.objects.filter(game_name__icontains= data)

        category_list = Categories.objects.all()
        form = BoardGamesForm()

        context = {
            "category_list" : category_list,
            "boardgame_list": boardgame_list,
            "form":form
        }
        return render(request, self.template_name, context)

# filter

class BoardgameFilterView(View):
    
    template_name = "boardgame.html"
    
    def get(self, request):
        cate = request.GET.get('category')
        time = request.GET.get('play_time')
        minp = request.GET.get('min_players')
        maxp = request.GET.get('max_players')

        boardgame_list = BoardGames.objects.filter(
            category__id=cate , play_time__gte=time,
            min_players__gte = minp , max_players__lte = maxp
            )
        print(boardgame_list)

        category_list = Categories.objects.all()
        form = BoardGamesForm()

        context = {
            "category_list" : category_list,
            "boardgame_list": boardgame_list,
            "form":form
        }
        return render(request, self.template_name, context)


class BoardgameDetailView(View):
    template_name = "boardgame_detail.html"

    def get(self, request, game_id):

        print(game_id)
        
        boardgame_detail = BoardGames.objects.get(pk= game_id)

        boardgame_detail_url = boardgame_detail.video_url.replace('youtu.be/', 'www.youtube.com/embed/')
        
        context = {
            "boardgame_detail": boardgame_detail,
            "boardgame_detail_url":boardgame_detail_url
        }
        return render(request, self.template_name, context)




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

        # ส่ง obj นั้น ที่จะแก้ไขเข้าไปในฟอร์ม 
        form = BoardGamesForm(request.POST , request.FILES, instance=boardgame)

        if form.is_valid():
            form.save()
            return redirect('des-boardgame')
        
        return render(request, self.template_name, {"form": form})


class DashboardMemberView(View):
    template_name = "admin/dashboard-member.html"

    def get(self, request):
        member_list = User.objects.exclude(username='admin') # ไม่เอา admin
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
    
class ProfileEditView(View):
    def get(self, request):
        profile = request.user # ดึงข้อมูลผู้ใช้ / ตัวที่เข้าถึงข้อมูลของ user ที่เข้าสู่ระบบ
        phone = UserDetail.objects.get(user=profile) # user = user login
        # initial ตั้งค่าเริ่มต้นคนละตารางกับ user, instance ดึงข้อมูลจาก user มาใส่ฟอร์ม
        form = ProfileEditForm(instance=profile, initial={'phone_number': phone.phone_number})
        pack = {'form': form}
        return render(request, 'editprofile-form.html', pack)
    
    def post(self, request):
        profile = request.user
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'editprofile-form.html', {'form': form})
    
class PasswordChangeView(View):
    def get(self, request):
        new = request.user
        form = SetPasswordForm(user=new) # ใช้ของdjango ให้รู้ว่า user คนไหนที่ต้องการเปลี่ยนรหัส
        return render(request, 'password.html', {'form': form})
    
    def post(self, request):
        new = request.user
        form = SetPasswordForm(data=request.POST, user=new)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user) # ไม่ให้มัน logout ออกหลังจากเปลี่ยนรหัส เป็นการอัปเดตเซสชันหลังบ้าน import มา
            return redirect('profile')
        return render(request, 'password.html', {'form': form})