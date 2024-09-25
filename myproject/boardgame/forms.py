from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError

from django import forms
from .models import *

from datetime import date, timedelta, time
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm


# ฟอร์มจองโต๊ะ
class ReservationForm(forms.ModelForm):
    table = forms.ModelChoiceField(queryset=Table.objects.filter(status='Available')) # แสดงเฉพาะโต๊ะที่ว่าง


    class Meta:
        model = Reservation
        fields = [
            "table", 
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

        if res_time < time(10, 0) and res_time > time(23, 0) :
            raise forms.ValidationError("กำหนดเวลาอยู่ในช่วง 10:00 ถึง 23:00!")
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
    
    phone_number = forms.CharField(max_length=15)
    
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
        

    # เช็คว่าเบอร์ซ้ำมั้ย
    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]

        data = UserDetail.objects.filter(phone_number= phone_number)

        if data.count():  
            raise ValidationError("Phone number Already Exist")  
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