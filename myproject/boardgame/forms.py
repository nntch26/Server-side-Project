from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError

from django import forms
from .models import *

from datetime import date
from django.utils import timezone


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

        def clean(self):
            cleaned_data = super().clean()
            res_date = cleaned_data.get("reservation_date")
            res_time = cleaned_data.get("reservation_time")
            res_cap = cleaned_data.get("reservation_cap")
            table = cleaned_data.get("table")

            # เช็ควันที่ ต้องไม่เกิน 1 วัน
            if res_date > date.today()+1 or res_date  < date.today():
                raise forms.ValidationError("กำหนดเวลาการจองได้ไม่เกิน 1 วัน!")
            
            # เช็คเวลา ต้องอยู่ในช่วง 10 โมงถึง 5 ทุ่ม
            elif res_time < timezone.time(10, 0) or res_time > timezone.time(23, 0) :
                raise forms.ValidationError("กำหนดเวลาอยู่ในช่วง 10:00 ถึง 23:00!")
            
            # เช็คจำนวนคนต้องอยู่ในช่วงจำนวนที่นั่ง
            elif res_cap:
                if res_cap <= 0:
                    raise forms.ValidationError("จำนวนคนต้องมากกว่า 0!")

                if res_cap > table.table_cap:
                    raise forms.ValidationError(f"จำนวนคนต้องไม่เกิน {table.table_cap} คน!")
            
            return cleaned_data


        

