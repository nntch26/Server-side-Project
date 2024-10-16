from typing import Any
from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError

from django import forms
from .models import *

from datetime import date, timedelta, time, datetime
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm


# ฟอร์มจองโต๊ะ
class ReservationForm(forms.ModelForm):
    #  เพิ่มฟิลด์จากตารางอื่น เข้ามาในฟอร์มด้วย
    table = forms.ModelChoiceField(queryset=Table.objects.filter(status='Available'),
                                   label="เลือกโต๊ะ") # แสดงเฉพาะโต๊ะที่ว่าง
    board_game = forms.ModelChoiceField(queryset=BoardGames.objects.filter(status='Available'), label="เลือกบอร์ดเกม",
                                        required=False ) # ไม่บังคับให้จองบอร์ดเกม


    class Meta:
        model = Reservation
        fields = [
            "table", 
            "board_game",
            "reservation_date", 
            "reservation_time", 
            "reservation_cap", 
        ]

        widgets = {
            "reservation_date": forms.DateInput(attrs={'type': 'date'}),
            "reservation_time": forms.DateInput(attrs={'type': 'time'}),
        }

        labels = {
            'table': 'เลือกโต๊ะ', 
            'reservation_date': 'วันที่',
            'reservation_time': 'เวลา',
            'reservation_cap': 'จำนวนคน',
        }

    # เช็ควันที่ ต้องไม่เกิน 1 วัน
    def clean_reservation_date(self):
        res_date = self.cleaned_data["reservation_date"]

        if res_date > date.today() + timedelta(days=1)  or res_date  < date.today():
            raise forms.ValidationError("กำหนดเวลาการจองได้ไม่เกิน 1 วัน!")
        return res_date  

    # เช็คเวลา ต้องอยู่ในช่วง 10 โมงถึง 5 ทุ่ม
    def clean_reservation_time(self):
        res_time = self.cleaned_data["reservation_time"]
    
        if res_time:
            if res_time < time(10, 0) and res_time > time(23, 0):
                raise forms.ValidationError("กำหนดเวลาอยู่ในช่วง 10:00 ถึง 23:00!")
            
            if res_time <= datetime.now().time():
                raise forms.ValidationError(f"ต้องเป็นเวลาการจองล่วงหน้า!")
    
        return res_time


    # เช็คจำนวนคนต้องอยู่ในช่วงจำนวนที่นั่ง
    def clean_reservation_cap(self):
        res_cap = self.cleaned_data["reservation_cap"]
        table = self.cleaned_data["table"]
        
        if res_cap:
            if res_cap <= 0:
                raise forms.ValidationError("จำนวนคนต้องมากกว่า 0!")

            if res_cap > table.table_cap:
                raise forms.ValidationError(f"จำนวนคนต้องไม่เกิน {table.table_cap} คน!")
        
        return res_cap


# ฟอร์ม Register
class CustomUserCreationForm(UserCreationForm):

    #  เพิ่มฟิลด์จากตารางอื่น เข้ามาในฟอร์มด้วย
    phone_number = forms.CharField(max_length=10, label='เบอร์โทรศัพท์')
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name', 
            'username', 
            'phone_number', 
            'email', 
            'password1', 
            'password2'
        ]

        labels = {
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล',
            'username': 'ชื่อผู้ใช้',
            'email': 'อีเมล',
            'password1': 'รหัสผ่าน',
            'password2': 'ยืนยันรหัสผ่าน',
        }
        

    # เช็คว่าเบอร์ซ้ำมั้ย และต้องมี 10 หลัก ห้ามเป็นตัวอักษร
    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]

        data = UserDetail.objects.filter(phone_number= phone_number)

        if data.count():  
            raise ValidationError("Phone number Already Exist")

        if len(phone_number) != 10 or not phone_number.isdigit():  
            raise ValidationError("Phone number must have 10 digits")  

        return phone_number  
    

    # เช็คว่าอีเมลซ้ำมั้ย
    def clean_email(self):
        email = self.cleaned_data["email"]

        data = User.objects.filter(email= email)

        if data.count():  
            raise ValidationError("Email Already Exist")  
        return email  


class BoardGamesForm(forms.ModelForm):

    class Meta:
        model = BoardGames
        fields = [
            "game_name", 
            "description", 
            "min_players", 
            "max_players",
            "play_time",
            "image",
            "video_url",
            "category" 
        ]

        widgets = {
            "description": forms.Textarea(),
        }

        labels = {
            'game_name': 'ชื่อบอร์ดเกม', 
            'description': 'รายละเอียด',
            'min_players': 'จำนวนคนขั้นต่ำ',
            'max_players': 'จำนวนคนไม่เกิน',
            'play_time': 'เวลาในการเล่น(นาที)',
            'image': 'รูปภาพ',
            'video_url': 'วิดีโอวิธีเล่น (URL)',
            'category': 'หมวดหมู่',
        }


    # เช็ค ต้องใส่เลขมากกว่า 0
    def clean_min_players(self):
        min_players = self.cleaned_data.get("min_players")


        if min_players <= 0:
            raise forms.ValidationError("กำหนดต้องมากกว่า 0")
        
        return min_players

    def clean_max_players(self):
        max_players = self.cleaned_data["max_players"]


        if max_players <= 0:
            raise forms.ValidationError("กำหนดต้องมากกว่า 0")
        
        return max_players


    def clean_play_time(self):
        play_time = self.cleaned_data["play_time"]

        if play_time <= 0:
            raise forms.ValidationError("กำหนดต้องมากกว่า 0")
        return play_time
    

    # เช็คจำนวนคนเล่นขั้นต่ำ กับ ไม่เกินต้อง สอดคล้องกัน 
    def clean(self):
        cleaned_data = super().clean()  

        min_players = cleaned_data.get("min_players")
        max_players = cleaned_data.get("max_players")

        if min_players >= max_players or max_players <= min_players:
            raise forms.ValidationError("กำหนดจำนวนผู้เล่นขั้นต่ำต้องน้อยกว่าจำนวนผู้เล่นสูงสุด")

        return cleaned_data


# เพิ่มประเภทข้อมูล
class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = [
            "name"
        ]
        labels = {
            'name': 'ชื่อหมวดหมู่',
        }

    # เช็ค ชื่อหมวดหมู่ไม่ซ้ำ
    def clean_name(self):
        cate_name = self.cleaned_data["name"]

        data = Categories.objects.filter(name= cate_name)

        if data.count():  
            raise ValidationError("Category Name Already Exist")
        return cate_name  



# profile
class ProfileEditForm(forms.ModelForm):

    #  เพิ่มฟิลด์จากตารางอื่น เข้ามาในฟอร์มด้วย
    GENDER_CHOICES = [
        ('', 'เลือกเพศ'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('othor', 'Othor'),
    ]

     
    gender = forms.ChoiceField( required=False, choices=GENDER_CHOICES, label='เพศ') #  ChoiceField ทำเปนตัวเลือก

    phone_number = forms.CharField(max_length=10, label='หมายเลขโทรศัพท์')
    birth_date = forms.DateField(required=False, 
                                 label='วันเกิด',
                                 widget=forms.DateInput(attrs={'type': 'date'})) 
    # ต้องใส่ตรงนี้ด้วยไม่งั้นไม่ขึ้นเป็น type:date เพราะเปนตารางอื่น
    
    class Meta:
        model = User
        fields = [
            'username',
            'phone_number',
            'gender',
            'first_name',
            'last_name',
            'email',
            'birth_date',
        ]

        labels = {
            'username': 'ชื่อผู้ใช้',
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล',
            'email': 'อีเมล',
        }
 

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # ยกเว้นตัวมันเอง
        user_id = self.instance.id
        data = UserDetail.objects.filter(phone_number = phone_number).exclude(user_id=user_id)
        if data.count():
            raise ValidationError("Phone number Already Exist")

        if len(phone_number) != 10 or not phone_number.isdigit():  
            raise ValidationError("Phone number must have 10 digits")  

        return phone_number
    
    def clean_email(self):
        email = self.cleaned_data['email']
        user_id = self.instance.id
        data = User.objects.filter(email = email).exclude(pk=user_id) # ยกเว้นตัวมันเอง จากตาราง user
        if data.count():
            raise ValidationError("Email Already Exist")
        return email
    

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date") # เป็นoptional

        if birth_date > date.today():
            raise ValidationError("ห้ามเป็นวันในอนาคต")
        return birth_date
    

class PlaySessionForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=10)
    class Meta:
        model = PlaySession
        fields = [
            'num_players',
            'phone_number',
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        data = UserDetail.objects.filter(phone_number= phone_number)
        if data.count()==0:  # ถ้าไม่มีเบอร์ในฐานข้อมูล
            raise ValidationError("ไม่มีเบอร์โทรศัพท์สมาชิกหมายเลขนี้")  
        return phone_number
    
    def clean_num_players(self):
        num_players = self.cleaned_data.get("num_players")
        if num_players <= 0:
            raise ValidationError("กรุณาเพิ่มจำนวนคนที่มาให้ถูกต้อง")
        return num_players
