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
    title = models.CharField(max_length=250)
    detail = models.TextField()
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2)

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
    


