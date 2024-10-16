from django.shortcuts import render, redirect
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from .models import *
from .forms import * 

from django.core.exceptions import PermissionDenied
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
        user_login = request.user
        # ดูประวัติการจองของ user คนนี้
        reservation_table = Reservation.objects.filter(user=user_login).order_by('-created_at')
        print(reservation_table)
        
        context = {
            "form": form,
            "reservation_table":reservation_table
        }
        return render(request, self.template_name, context)
    

    def post(self, request):

        form = ReservationForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user  # กำหนดผู้ใช้ที่ล็อกอิน
            form.save()

            # ถ้ามีการจองบอร์ดเกม ดึงข้อมูลจากฟอร์ม
            board_game = form.cleaned_data['board_game']
            
            if board_game: 
                board_game.status = 'Reserved'  # เปลี่ยนสถานะบอร์ดเกม เป็นถูกจอง
                board_game.save() 


            # แสดงข้อความแจ้งเตือน
            messages.success(request, 'บันทึกการจองของคุณเรียบร้อยแล้ว')

            return redirect('Reservation_form')  # กลับไปหน้าจองโต๊ะ
        
        return render(request, self.template_name, {"form": form})


# cashier     
# staff1 st1@1234

class CashierView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_table"]


    def get(self, request):
        tables = Table.objects.all().order_by('id')
        pack = {'tables': tables}
        return render(request, 'cashier/cashier-table.html', pack)
    
    def post(self, request):
        form = PlaySessionForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('cashier_table')


    
class CashierBillView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_playsession"]

    def get(self, request, table_id):

        #ดึงเอา group ของผู้ใช้คนนี้ อันนี้ผู้ใช้มีแค่คนละ group เดียว
        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "staff":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden
            
        reservation = Reservation.objects.filter(table_id=table_id).order_by('created_at').last()
        playsession = PlaySession.objects.filter(table_id=table_id).order_by('start_time').last()
        pack = {'reservation': reservation, 'playsession': playsession}
        return render(request, 'cashier/bill.html', pack)
    
    def post(self, request, table_id):
        reservation = Reservation.objects.filter(table_id=table_id).order_by('created_at').last()
        playsession = PlaySession.objects.filter(table_id=table_id, end_time__isnull=True).order_by('start_time').last() # โต๊ะนั้นจาก playsession ที่ยังไม่ได้มี end_time 
        if playsession:
            playsession.end_time = datetime.now().time()  # บันทึกเวลาตอนนี้เป็น end_time เฉพาะเวลาเท่านั้น
            start_datetime = datetime.combine(timezone.now().date(), playsession.start_time) # รวมวันนี้กับเวลาเริ่ม
            end_datetime = datetime.combine(timezone.now().date(), playsession.end_time) # รวมวันนี้กับเวลาจบ
            total_hours = int((end_datetime - start_datetime).total_seconds() / 3600 + 1) # แปลงเป็นชั่วโมง + 1 เพราะคิดขั้นต่ำเป็น 1 ชั่วโมง
            total_cost = int(playsession.num_players * 30 * total_hours) # ทำเป็นจำนวนเต็ม
            
            playsession.total_hours = total_hours
            playsession.total_cost = total_cost
            playsession.save()
        return redirect('cashier_bill', table_id=table_id)
    
    

class CashierListView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_reservation"]

    def get(self, request):

        #ดึงเอา group ของผู้ใช้คนนี้ อันนี้ผู้ใช้มีแค่คนละ group เดียว
        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "staff":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden
            
        reserv = Reservation.objects.filter(status='Pending')
        pack = {'reserv': reserv}
        return render(request, 'cashier/cashier-confirm.html', pack)

# กด confirm
class CashierConfirmView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.change_reservation"]

    def get(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        table = Table.objects.get(id=reservation.table.id) # getidจองของidโต๊ะนั้นที่จอง

        reservation.status = 'Confirmed' # เปลี่ยนสถานะของตารางจอง
        reservation.save()
        table.status = 'Reserved' # เปลี่ยนสถานะของตารางโต๊ะ
        table.save()
        return redirect('cashier_list')

# กด cancel การจองที่จองเข้ามา
class CashierCancelView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.delete_reservation"]

    def get(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.status = 'Cancelled' # เปลี่ยนสถานะของตารางจอง
        reservation.save()


        # เปลี่ยนสถานะของบอร์ดเกม
        if reservation.board_game:
            print("555555555555555555")
            gameid = reservation.board_game.id
            game = BoardGames.objects.get(pk=gameid)
            game.status = 'Available'
            game.save()
        return redirect('cashier_list')
    

# พนักงานกดยกเลิกรับโต๊ะหลังจากจองแล้ว

class CashierServeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.change_table"]

    def get(self, request, table_id):
        table = Table.objects.get(id=table_id)
        reservation = Reservation.objects.filter(table_id=table_id).order_by('created_at').last()
        if table.status == 'Reserved':
            table.status = 'Available' # เปลี่ยนสถานะของตารางโต๊ะจากจองเป็นว่าง
            table.save()

        # เปลี่ยนสถานะของบอร์ดเกม
        if reservation.board_game:
            print("555555555555555555")
            gameid = reservation.board_game.id
            game = BoardGames.objects.get(pk=gameid)
            game.status = 'Available'
            game.save()


        return redirect('cashier_table')
    
# พนักงานกดรับโต๊ะ จากตอนแรกจองพอกดด้านในเปลี่ยนเป็นไม่ว่าง
class CashierReServeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.change_table", "boardgame.add_playsession"]

    def get(self, request, table_id):
        table = Table.objects.get(id=table_id)
        reservation = Reservation.objects.filter(table_id=table_id).order_by('created_at').last()
        if table.status == 'Reserved':
            table.status = 'Occupied' # เปลี่ยนสถานะของตารางโต๊ะจากจองเป็นไม่ว่าง
            table.save()

            # เปลี่ยนสถานะของบอร์ดเกม
            if reservation.board_game:
                print("555555555555555555")
                gameid = reservation.board_game.id
                game = BoardGames.objects.get(pk=gameid)
                game.status = 'Available'
                game.save()

            PlaySession.objects.create(
                table=table,
                user=reservation.user,
                num_players=reservation.reservation_cap,
                start_time=timezone.now(),
            )
            # filter ตัวที่เพิ่งสร้างล่าสุด
            playsession = PlaySession.objects.filter(table_id=table_id).order_by('start_time').last()
            return redirect('cashier_detail', table_id=table_id)
        return render(request, 'cashier/cashier-table.html', {'playsession': playsession})
    

# ดูรายละเอียดโต๊ะทั้งจองและรับโต๊ะ
class CashierDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_reservation", "boardgame.view_playsession"]

    def get(self, request, table_id):

        #ดึงเอา group ของผู้ใช้คนนี้ อันนี้ผู้ใช้มีแค่คนละ group เดียว
        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "staff":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden
            
        reservation = Reservation.objects.filter(table_id=table_id) # filter table_id ของ reserve = table_id ที่ส่งมา
        playsession = PlaySession.objects.filter(table_id=table_id).order_by('start_time').last()
        print(playsession)
        pack = {'reservation': reservation, 'playsession': playsession}
        return render(request, 'cashier/table-detail.html', pack)

# โชว์ฟอร์มรับโต๊ะ
class PlaySessionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.add_playsession"]

    def get(self, request, table_id):
        table = Table.objects.get(id=table_id)
        form = PlaySessionForm()
        pack = {'form': form, 'table': table}
        return render(request, 'cashier/cashier-serve.html', pack)
    
    def post(self, request, table_id):
        table = Table.objects.get(id=table_id)
        form = PlaySessionForm(request.POST)
        print(form.instance.start_time)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            data = User.objects.get(userdetail__phone_number = phone_number)


            form.instance.table = table
            form.instance.user = data
            form.save()

            # play = PlaySession.objects.create(
            #     table=table,
            #     user=data,
            #     num_players=request.POST.get('num_players'),
            #     start_time=timezone.now(),
            # )
            

            table.status = 'Occupied' # เปลี่ยนสถานะของตารางโต๊ะ
            table.save()
            return redirect('cashier_detail', table_id=table_id)
        else:
            print(form.errors)
        return render(request, 'cashier/cashier-serve.html', {'form': form, 'table': table})
        
# จ่ายเงิน add point
class PaymentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_playsession", "boardgame.change_playsession", "boardgame.add_payments"]

    def post(self, request, table_id):
        table = Table.objects.get(id=table_id)
        playsession = PlaySession.objects.filter(table_id=table_id).order_by('end_time').last()
        user = playsession.user # playsession ของ user นั้น
        getuser = User.objects.get(id=user.id) # get user.id เพื่อเพิ่ม points
        print(getuser.id)
        pay = request.POST.get('pay') # จำนวนเงินที่กรอกเข้ามาใน input
        
        # ถ้าจ่ายเงินเยอะกว่าเงินที่ต้องจ่าย
        if float(pay) >= float(playsession.total_cost):
            money = float(pay) - float(playsession.total_cost)
            playsession.is_paid = True # เปลี่ยนเป็นจ่ายแล้ว
            playsession.save()

            # .points เพื่อเพิ่ม point ใน userdetail
            point = getuser.userdetail
            point.points += float(playsession.total_cost) / 10
            point.save()
            print(point)

            table.status = 'Available' # เปลี่ยนสถานะของตารางโต๊ะ
            table.save()

            pay = Payments.objects.create(
                session = playsession,
                payment_amount = playsession.total_cost,
                payment_date = timezone.now()
            )

        else:
            money = 0
            messages.error(request, 'กรุณาจ่ายเงินให้ครบ')
        return render(request, 'cashier/bill.html', {'playsession': playsession, 'money': money})

# ใช้คะแนน
class UsePointsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.add_playsession", "boardgame.change_playsession", "boardgame.change_payments"]

    def get(self, request, table_id):
        playsession = PlaySession.objects.filter(table_id=table_id).order_by('end_time').last()
        user = playsession.user
        getuser = User.objects.get(id=user.id)
        print(getuser.id)

        point = getuser.userdetail
        if point.points >= 30:
            point.points -= 30
            point.save()

            total = float(playsession.total_cost) - 30
            playsession.total_cost = total
            playsession.save()

        else:
            # print('1')
            # print(point.points)
            # print(playsession.total_cost)

            total = float(playsession.total_cost) - float(point.points)
            playsession.total_cost = total
            playsession.save()
            print(total)

            point.points -= point.points
            point.save()

            print(point.points)
        return render(request, 'cashier/bill.html', {'playsession': playsession})





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

        form = BoardGamesFilterForm()
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
        form = BoardGamesFilterForm()

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
       
        form = BoardGamesFilterForm(request.GET)
        boardgame_list = None
        print(form.errors)

        if form.is_valid(): # เช็คความถูกต้องของข้อมูลที่กรอกมา
            print(555555555555)
            cate = form.cleaned_data['category']
            time = form.cleaned_data['play_time']
            minp = form.cleaned_data['min_players']
            maxp = form.cleaned_data['max_players']
            print(cate)
            
            boardgame_list = BoardGames.objects.filter(
                category__id__in=cate,  # หาหมวดหมู่หลายอัน  เป็น list
                play_time__lte=time,
                min_players__gte = minp , 
                max_players__lte = maxp
                ).distinct() # ไม่เอาข้อมูลซ้ำ เกมเดียว แต่อยู่ในหลายหมวดหมู่ แสดงครั้งเดียว
            print(boardgame_list)
        else:
            messages.error(request, "โปรดกรอกข้อมูลให้ถูกต้อง!")

        category_list = Categories.objects.all()

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





# //////////////////// Dashboard ////////////////////
# manager2 mg2@1234

class DashboardView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_reservation"]

    template_name = "admin/dashboard.html"


    def get(self, request):

        #ดึงเอา group ของผู้ใช้คนนี้ อันนี้ผู้ใช้มีแค่คนละ group เดียว
        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "manager":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden


        boardgame_list = BoardGames.objects.all().count()
        member_list = User.objects.exclude(
            Q(username__startswith='admin') | 
            Q(username__startswith='staff') | 
            Q(username__startswith='manager')
        ).count()
        # ไม่เอา admin staff manager
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


class DashboardBoardgameView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_boardgames",]

    template_name = "admin/dashboard-boardgame.html"

    def get(self, request):
        product_list = BoardGames.objects.all()
        return render(request, self.template_name, {"product_list": product_list})


class DashboardBoardgameAddView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.add_boardgames",]

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


class DashboardBoardgameDelView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.delete_boardgames",]

    def get(self, request, game_id):
        project_data = BoardGames.objects.get(pk=game_id)
        project_data.delete()
        return redirect('des-boardgame')


class DashboardBoardgameEditView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.change_boardgames",]

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
            messages.success(request, 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว')
            return redirect('des-boardgame')
            # แสดงข้อความแจ้งเตือน
           
        
        messages.error(request, 'เกิดข้อผิดพลาด ไม่สามารถบันทึกข้อมูลได้! โปรดลองใหม่')
        return render(request, self.template_name, {"form": form})


# //////////////////// member  ////////////////////
class DashboardMemberView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["auth.view_user"]


    template_name = "admin/dashboard-member.html"

    def get(self, request):

        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "manager":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden

        member_list = User.objects.exclude(
            Q(username__startswith='admin') | 
            Q(username__startswith='staff') | 
            Q(username__startswith='manager')
        ) 
        # ไม่เอา admin staff manager

        return render(request, self.template_name, {"member_list": member_list})

class DashboardMemberDelView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["auth.delete_user"]

    def get(self, request, mem_id):

        member_data = User.objects.get(pk=mem_id)
        member_data.delete()
        return redirect('des-member')
    

# //////////////////// หมวดหมู่ ////////////////////
class DashboardCategoriesView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_categories"]

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


class DashboardCategoriesDelView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.delete_categories"]

    def get(self, request, cate_id):

        data = Categories.objects.get(pk=cate_id)
        data.delete()
        return redirect('des-categories')


class DashboardCategoriesEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.change_categories"]

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
            
            messages.success(request, 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว')
            return redirect('des-categories')
            # แสดงข้อความแจ้งเตือน
            


        return render(request, self.template_name, {"form": form})



# /////////////////// profile ////////////////////
class ProfileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["auth.view_user", "boardgame.view_userdetail"]

    def get(self, request):
        return render(request, 'profile.html')
    
class ProfileEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.change_userdetail", "boardgame.view_userdetail"]


    def get(self, request):

        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "customer":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden
            
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
    
class PasswordChangeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["auth.change_user"]

    def get(self, request):

        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "customer":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden

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


# /////////////////// Playing ////////////////////

class PlayingView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["boardgame.view_playsession"]

    def get(self, request):

        user = request.user
        user_groups = user.groups.all()
        for group in user_groups:
            print(group.name)  

            # ถ้าผู้ใช้ไม่ใช่ manager
            if group.name != "customer":
                raise PermissionDenied # เข้าหน้าที่ไม่มีสิท  403 Forbidden
            
        form = BoardGamesForm()
        user = request.user
        print(user)
        user_playsessions = PlaySession.objects.filter(user=user, is_paid=False).order_by('-created_at').first() 

        # ดึงข้อมูลใบเสร็จ การเล่นบอร์ดเกมของลุกค้าคนนั้น ล่าสุด
        print(user_playsessions) # ได้ออกมา 1 obj


        context = {
            "form":form,
            "user_playsession":user_playsessions
        }
        return render(request, 'playing.html', context)