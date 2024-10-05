from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from django.db.models.functions import Length, Upper, Concat
from .models import *

from django.utils import timezone
import datetime

from .forms import * 

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm  

import random


# Create your views here.

class indexView(View):

    template_name = "index.html"

    def get(self, request):
        boardgame_list = list(BoardGames.objects.all())  # แปลง QuerySet เป็น  list เอาไปใส่ใน random

        # ให้ข้อมูลสลับกันมั่วๆ ไม่เรียงกัน สุ่มเลือกจากทั้งก้อน มา 4 ตัว
        boardgame_list = random.sample(boardgame_list, k=4)
        print(boardgame_list)

        category_list = Categories.objects.all()

        context = {
            "boardgame_list": boardgame_list,
            "category_list ":category_list 
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
        tables = Table.objects.all().order_by('id')
        pack = {'tables': tables}
        return render(request, 'cashier/cashier-table.html', pack)
    
    def post(self, request):
        form = PlaySessionForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('cashier_table')

# เด่วมาลบ
class CashierPayView(View):
    def get(self, request):
        tables = Table.objects.all().order_by('id')
        pack = {'tables': tables}
        return render(request, 'cashier/cashier-pay.html', pack)
    
class CashierBillView(View):
    def get(self, request, table_id):
        reservation = Reservation.objects.get(id=table_id)
        pack = {'reservation': reservation}
        return render(request, 'cashier/bill.html', pack)
    
class CashierListView(View):
    def get(self, request):
        reserv = Reservation.objects.all()
        pack = {'reserv': reserv}
        return render(request, 'cashier/cashier-confirm.html', pack)

# กด confirm
class CashierConfirmView(View):
    def get(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        table = Table.objects.get(id=reservation.table.id) # getidจองของidโต๊ะนั้นที่จอง
        reservation.status = 'Confirmed' # เปลี่ยนสถานะของตารางจอง
        reservation.save()
        table.status = 'Reserved' # เปลี่ยนสถานะของตารางโต๊ะ
        table.save()
        return redirect('cashier_list')

# กด cancel
class CashierCancelView(View):
    def get(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        table = Table.objects.get(id=reservation.table.id)
        reservation.status = 'Cancelled' # เปลี่ยนสถานะของตารางจอง
        reservation.save()
        table.status = 'Available' # เปลี่ยนสถานะของตารางโต๊ะ
        table.save()
        return redirect('cashier_list')
    
# พนักงานกดยกเลิกรับโต๊ะ
class CashierServeView(View):
    def get(self, request, table_id):
        table = Table.objects.get(id=table_id)
        if table.status == 'Reserved':
                table.status = 'Available' # เปลี่ยนสถานะของตารางโต๊ะจากจองเป็นว่าง
                table.save()
        # if form.is_valid():
        #     if table.status == 'Reserved':
        #         table.status = 'Available' # เปลี่ยนสถานะของตารางโต๊ะ
        #         table.save()
        #     elif table.status == 'Available':
        #         table.status = 'Occupied' # เปลี่ยนสถานะของตารางโต๊ะ
        #         table.save()
 
        return redirect('cashier_table')
    
# พนักงานกดรับโต๊ะ จากตอนแรกจองพอกดด้านในเปลี่ยนเป็นไม่ว่าง
class CashierReServeView(View):
    def get(self, request, table_id):
        table = Table.objects.get(id=table_id)
        if table.status == 'Reserved':
                table.status = 'Occupied' # เปลี่ยนสถานะของตารางโต๊ะจากจองเป็นไม่ว่าง
                table.save()
        return redirect('cashier_table')
    



class CashierDetailView(View):
    def get(self, request, table_id):
        reservation = Reservation.objects.filter(table_id=table_id) # filter table_id ของ reserve = table_id ที่ส่งมา
        pack = {'reservation': reservation}
        return render(request, 'cashier/table-detail.html', pack)
    






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

        boardgame_list = list(BoardGames.objects.all())
        # ให้แสดงผลแบบสุ่มมั่วๆ สลับๆ ไม่เรียงลำดับ
        random.shuffle(boardgame_list)
        print(boardgame_list)

        form = BoardGamesForm()
        select_cate = None # อันที่กด

        if cate_name:
            boardgame_list = BoardGames.objects.filter(category__name = cate_name)
            select_cate = cate_name # เก็บชื่ออันที่กด

        print(select_cate)
        context = {
            "category_list" : category_list,
            "boardgame_list": boardgame_list,
            "form":form,
            "select_cate":select_cate
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
            category__id=cate , 
            play_time__lte=time,
            min_players__gte = minp , 
            max_players__lte = maxp
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
        boardgame_list = BoardGames.objects.all().count()
        member_list = User.objects.exclude(username='admin').count()
        reservation_list = Reservation.objects.all()
        table_list = Table.objects.all().count()


        print(boardgame_list)

       
        context = {
            "boardgame_list": boardgame_list,
            "member_list":member_list,
            "reservation_list":reservation_list,
            "table_list":table_list
        }
        return render(request, self.template_name, context)


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


# member
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
    

# หมวดหมู่ 
class DashboardCategoriesView(View):
    template_name = "admin/dashboard-categories.html"

    def get(self, request):
        categories_list = Categories.objects.all()
        
        return render(request, self.template_name, {"categories_list": categories_list})

class DashboardCategoriesAddView(View):
    template_name = "admin/categories_add.html"

    def get(self, request):
        form = CategoriesForm()
        return render(request, self.template_name, {"form": form})
    

    def post(self, request):
        form = CategoriesForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('des-categories')
        
        return render(request, self.template_name, {"form": form})


class DashboardCategoriesDelView(View):
    def get(self, request, cate_id):

        data = Categories.objects.get(pk=cate_id)
        data.delete()
        return redirect('des-categories')


class DashboardCategoriesEditView(View):
    template_name = "admin/categories_edit.html"

    def get(self, request, cate_id):

        # ดึง obj มาแสดงในฟอร์มด้วย
        categories = Categories.objects.get(pk=cate_id)
        form = CategoriesForm(instance=categories)

        return render(request, self.template_name, {"form": form})
    

    def post(self, request, cate_id):

        # ดึง obj ที่จะแก้ไข
        categories = Categories.objects.get(pk=cate_id)

        # ส่ง obj นั้น ที่จะแก้ไขเข้าไปในฟอร์ม 
        form = CategoriesForm(request.POST, instance=categories)

        if form.is_valid():
            form.save()
            return redirect('des-categories')
        
        return render(request, self.template_name, {"form": form})



# profile
class ProfileView(View):
    def get(self, request):
        return render(request, 'profile.html')
    
class ProfileEditView(View):
    def get(self, request):
        profile = request.user # ดึงข้อมูลผู้ใช้ / ตัวที่เข้าถึงข้อมูลของ user ที่เข้าสู่ระบบ
        userdetail = UserDetail.objects.get(user=profile) # user = user login
        # initial ตั้งค่าเริ่มต้นคนละตารางกับ user, instance ดึงข้อมูลจาก user มาใส่ฟอร์ม
        form = ProfileEditForm(instance=profile, initial={'phone_number': userdetail.phone_number, 'gender': userdetail.gender, 'birth_date': userdetail.birth_date})
        pack = {'form': form}
        return render(request, 'editprofile-form.html', pack)
    
    def post(self, request):
        profile = request.user
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            userdetail = UserDetail.objects.get(user=profile) # ชี้หา user คนนี้ที่ต้องการเปลี่ยนข้อมูลใหม่
            # clean_date ก่อนไม่งั้นบันทึกไม่ได้
            userdetail.phone_number = form.cleaned_data['phone_number']
            userdetail.gender = form.cleaned_data['gender']
            userdetail.birth_date = form.cleaned_data['birth_date']
            userdetail.save() # บันทึกลงใน user_deatil
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