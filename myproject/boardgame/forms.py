from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError

from django import forms
from .models import *

from datetime import date



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