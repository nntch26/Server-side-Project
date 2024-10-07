from django.shortcuts import render, redirect
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from .models import *
from .forms import * 

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth import login, logout, update_session_auth_hash
from .forms import CustomUserCreationForm  
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.contrib import messages
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
class ReservationFormView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.add_reservation"]

    template_name = "reservation_form.html"

    def get(self, request):

        form = ReservationForm()
        return render(request, self.template_name, {"form": form})
    

    def post(self, request):

        form = ReservationForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user  # กำหนดผู้ใช้ที่ล็อกอิน
            form.save()

            # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บันทึกการจองของคุณเรียบร้อยแล้ว')

            return redirect('Reservation_form')  # กลับไปหน้าจองโต๊ะ
        
        return render(request, self.template_name, {"form": form})


# cashier     
# staff1 st1@1234

class CashierView(LoginRequiredMixin, View):
    login_url = 'login'
    # permission_required = ["boardgame.view_table"]


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

class CashierPayView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        tables = Table.objects.all().order_by('id')
        pack = {'tables': tables}
        return render(request, 'cashier/cashier-pay.html', pack)
    
class CashierBillView(View):
    def get(self, request, table_id):
        reservation = Reservation.objects.get(id=table_id)
        pack = {'reservation': reservation}
        return render(request, 'cashier/bill.html', pack)
    

class CashierListView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_reservation"]

    def get(self, request):
        reserv = Reservation.objects.all()
        pack = {'reserv': reserv}
        return render(request, 'cashier/cashier-confirm.html', pack)

# กด confirm
class CashierConfirmView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        table = Table.objects.get(id=reservation.table.id) # getidจองของidโต๊ะนั้นที่จอง
        reservation.status = 'Confirmed' # เปลี่ยนสถานะของตารางจอง
        reservation.save()
        table.status = 'Reserved' # เปลี่ยนสถานะของตารางโต๊ะ
        table.save()
        return redirect('cashier_list')

# กด cancel
class CashierCancelView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        table = Table.objects.get(id=reservation.table.id)
        reservation.status = 'Cancelled' # เปลี่ยนสถานะของตารางจอง
        reservation.save()
        table.status = 'Available' # เปลี่ยนสถานะของตารางโต๊ะ
        table.save()
        return redirect('cashier_list')
    
# พนักงานกดยกเลิกรับโต๊ะ

class CashierServeView(LoginRequiredMixin, View):
    login_url = 'login'

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
    


# ดูรายละเอียดโต๊ะ
class CashierDetailView(View):
    def get(self, request, table_id):
        reservation = Reservation.objects.filter(table_id=table_id) # filter table_id ของ reserve = table_id ที่ส่งมา
        pack = {'reservation': reservation}
        return render(request, 'cashier/table-detail.html', pack)

# โชว์ฟอร์มรับโต๊ะ
class PlaySessionView(View):
    def get(self, request, table_id):
        table = Table.objects.get(id=table_id)
        form = PlaySessionForm()
        pack = {'form': form, 'table': table}
        return render(request, 'cashier/cashier-serve.html', pack)
    
    def post(self, request, table_id):
        table = Table.objects.get(id=table_id)
        form = PlaySessionForm(request.POST)
        if form.is_valid():
            if table.status == 'Available':
                table.status = 'Occupied' # เปลี่ยนสถานะของตารางโต๊ะ
                table.save()
        return redirect('cashier_table')
    






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


            #ดึงเอา group ของผู้ใช้คนนี้ อันนี้ผู้ใช้มีแค่คนละ group เดียว
            user_groups = user.groups.all()
            for group in user_groups:
                print(group.name)  

            # ผู้ใช้ตรงกับ group ไหน เด้งไปหน้านั้น
            if group.name == "customer":
                login(request, user)
                return redirect('index')
            
            elif group.name == "staff":
                login(request, user)
                return redirect('cashier_table')

            elif group.name == "manager":
                login(request, user)
                return redirect('dashboard')
            
        return render(request, self.template_name, {"form":form})
    

class RegisterView(View):

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {"form": form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user1 = form.save()
            print(user1)

            # เพิ่มผู้ใช้ใหม่ ลงใน group 'customer'
            group = Group.objects.get(name='customer')
            user1.groups.add(group)

            UserDetail.objects.create(
                user = user1, #ยัด obj user เข้าไป
                phone_number = form.cleaned_data['phone_number']
            )

            # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บัญชีของคุณถูกสร้างเรียบร้อยแล้ว')
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

        # แทนที่ข้อความในลิ้ง เป็น www.youtube.com/embed/ ในเล่นวิดีโอ iframe
        boardgame_detail_url = boardgame_detail.video_url.replace('youtu.be/', 'www.youtube.com/embed/')
        
        context = {
            "boardgame_detail": boardgame_detail,
            "boardgame_detail_url":boardgame_detail_url
        }
        return render(request, self.template_name, context)


# //////////////////// Cart list ////////////////////

class CartListView(View):
     
    template_name = "cart_list.html"
     
    def get(self, request):

        return render(request, self.template_name)

class CartAddView(View):


    def get(self, request, game_id):
        pass



class CartDelView(View):
    pass




class PayOrderView(View):
    template_name = "payment_online.html"
     
    def get(self, request, order_id):

        return render(request, self.template_name)

# //////////////////// Dashboard ////////////////////
# manager2 mg2@1234

class DashboardView(LoginRequiredMixin, View):
    login_url = 'login'

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


class DashboardBoardgameView(LoginRequiredMixin, View):
    login_url = 'login'

    template_name = "admin/dashboard-boardgame.html"

    def get(self, request):
        product_list = BoardGames.objects.all()
        return render(request, self.template_name, {"product_list": product_list})


class DashboardBoardgameAddView(LoginRequiredMixin, View):
    login_url = 'login'

    template_name = "admin/boardgame_add.html"

    def get(self, request):
        form = BoardGamesForm()
        return render(request, self.template_name, {"form": form})
    

    def post(self, request):
        form = BoardGamesForm(request.POST , request.FILES)

        if form.is_valid():
            form.save()

             # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว')
            return redirect('des-boardgame')
            

        messages.error(request, 'เกิดข้อผิดพลาด ไม่สามารถบันทึกข้อมูลได้! โปรดลองใหม่')
        return render(request, self.template_name, {"form": form})


class DashboardBoardgameDelView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, game_id):
        project_data = BoardGames.objects.get(pk=game_id)
        project_data.delete()
        return redirect('des-boardgame')


class DashboardBoardgameEditView(LoginRequiredMixin, View):
    login_url = 'login'

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
            # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว')
        
        messages.error(request, 'เกิดข้อผิดพลาด ไม่สามารถบันทึกข้อมูลได้! โปรดลองใหม่')
        return render(request, self.template_name, {"form": form})


# //////////////////// member  ////////////////////
class DashboardMemberView(LoginRequiredMixin, View):
    login_url = 'login'

    template_name = "admin/dashboard-member.html"

    def get(self, request):
        member_list = User.objects.exclude(
            Q(username__startswith='admin') | 
            Q(username__startswith='staff') | 
            Q(username__startswith='manager')
        ) 
        # ไม่เอา admin staff manager

        return render(request, self.template_name, {"member_list": member_list})

class DashboardMemberDelView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, mem_id):

        member_data = User.objects.get(pk=mem_id)
        member_data.delete()
        return redirect('des-member')
    

# //////////////////// หมวดหมู่ ////////////////////
class DashboardCategoriesView(LoginRequiredMixin, View):
    login_url = 'login'

    template_name = "admin/dashboard-categories.html"

    def get(self, request):
        categories_list = Categories.objects.all()
        form = CategoriesForm()

        context = {
            "categories_list": categories_list,
            "form": form
        }
       
        return render(request, self.template_name, context)


    # เพิ่มหมวดหมู่
    def post(self, request):
        form = CategoriesForm(request.POST)

        if form.is_valid():
            form.save()

             # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว')
            return redirect('des-categories')
        
        # ถ้าไม่เข้าเงื่อนไข ให้แสดงข้อมูลเหมือนเดิม
        categories_list = Categories.objects.all()
        form = CategoriesForm()
        context = {
            "categories_list": categories_list,
            "form": form
        }
        
        messages.error(request, 'เกิดข้อผิดพลาด ไม่สามารถบันทึกข้อมูลได้! โปรดลองใหม่')
        return render(request, self.template_name, context)


class DashboardCategoriesDelView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, cate_id):

        data = Categories.objects.get(pk=cate_id)
        data.delete()
        return redirect('des-categories')


class DashboardCategoriesEditView(LoginRequiredMixin, View):
    login_url = 'login'

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
            # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว')


        return render(request, self.template_name, {"form": form})



# /////////////////// profile ////////////////////
class ProfileView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, 'profile.html')
    
class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user # ดึงข้อมูลผู้ใช้ / ตัวที่เข้าถึงข้อมูลของ user ที่เข้าสู่ระบบ
        userdetail = UserDetail.objects.get(user=profile) # user = user login
        # initial ตั้งค่าเริ่มต้นคนละตารางกับ user, instance ดึงข้อมูลจาก user มาใส่ฟอร์ม
        form = ProfileEditForm(instance=profile, 
                               initial={'phone_number': userdetail.phone_number, 'gender': userdetail.gender, 'birth_date': userdetail.birth_date})
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
    
class PasswordChangeView(LoginRequiredMixin, View):
    login_url = 'login'

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