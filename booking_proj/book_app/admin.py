from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(TimeSlot)
admin.site.register(Schedule)
