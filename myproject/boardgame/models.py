from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone


# Create your models here.


class UserDetail(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
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




class Categories(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name



class BoardGames(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved')
    ]

    game_name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ManyToManyField(Categories)  
    min_players = models.IntegerField()
    max_players = models.IntegerField(null=True, blank=True)
    play_time = models.IntegerField()
    image = models.ImageField(upload_to='upload')
    video_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available') 


    def __str__(self) -> str:
            return self.game_name
    


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board_game = models.ForeignKey(BoardGames, null=True, blank=True, on_delete=models.SET_NULL)  
    reservation_date = models.DateField()  
    reservation_time = models.TimeField()  
    reservation_cap = models.IntegerField()  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  
    created_at = models.DateTimeField(auto_now_add=True)  

# add
class PlaySession(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    num_players = models.IntegerField(null=False, default=1)
    start_time = models.TimeField(null=False, auto_now_add=True)
    end_time = models.TimeField(null=True)  
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    is_paid = models.BooleanField(default=False) #บันทึกสถานะจ่ายตัง ว่าจ่ายตังไปยัง
    created_at = models.DateTimeField(auto_now_add=True)


class Payments(models.Model):
    session = models.ForeignKey(PlaySession, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    payment_date = models.DateTimeField(null=False, auto_now_add=True)