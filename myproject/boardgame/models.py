from django.db import models
from django.contrib.auth.models import User  

# Create your models here.


class UserDetail(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('othor', 'Othor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # เชื่อมกับตาราง User 
    phone_number = models.CharField(max_length=10, unique=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    points = models.IntegerField(default=0)
    

    def __str__(self):
        return self.user.username 


class Table(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Occupied', 'Occupied'),
    ]

    table_cap = models.IntegerField()  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available') 

    def __str__(self):
        return f"โต๊ะที่ : {self.id} รองรับ: {self.table_cap}" 


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    reservation_date = models.DateField()  
    reservation_time = models.TimeField()  
    reservation_cap = models.IntegerField()  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  
    created_at = models.DateTimeField(auto_now_add=True)  

