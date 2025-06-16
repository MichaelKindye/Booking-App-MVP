from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('provider', 'Service Provider'),
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username
    






class Service(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, unique=True)
    detail = models.TextField()
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.TimeField()
    session_amount = models.PositiveIntegerField()
    session_hour = models.FloatField()
    work_days = models.JSONField(default=list)


    def __str__(self):
        return self.title


    

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    

    def __str__(self):
        return self.service.title





class TimeSlot(models.Model):
    DAY_CHOICES = (
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday')
    )
    day = models.CharField(max_length=50, choices=DAY_CHOICES)
    start = models.TimeField()
    end = models.TimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='time_slots')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'( {self.service.title} ) {self.day}: {self.start} - {self.end}'
    


class Schedule(models.Model):
    date = models.DateField()
    time = models.TimeField()
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)

    def __str__(self):
        return f"appointment on {self.date}: {self.date.day} at {self.time}"