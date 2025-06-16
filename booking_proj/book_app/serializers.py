from rest_framework import serializers
from .models import *
from django.db import transaction
from django.core.validators import MinValueValidator
from rest_framework.response import Response
from datetime import timedelta, time, datetime, date



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    
    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        role = validated_data['role']
        if username and password and role:
            if role == 'admin':
                return User.objects.create_user(username=username, password=password, role=role, is_superuser=True, is_staff=True)
            return User.objects.create_user(username=username, password=password, role=role)
       

class ServiceSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    DAY_CHOICES = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    class Meta:
        model = Service
        fields = ['id', 'provider', 'title', 'detail', 'price_per_session', 'start_time', 'session_hour', 'session_amount', 'work_days']


    def validate_work_days(self, value):
        if len(value) > 7:
            raise serializers.ValidationError(f"work days cannot be greater than 7 you have {len(value)}")
        
        for i in value:
            if not i.lower() in self.DAY_CHOICES:
                raise serializers.ValidationError(f"Invalid value for work days on {i}")
        
            value.append(i.lower())
            
        
        return value


    def create(self, validated_data):
        provider = self.context['request'].user
        start_time = validated_data['start_time']
        session_hour = validated_data['session_hour']
        session_amount = validated_data['session_amount']
        work_days = validated_data['work_days']
        with transaction.atomic():
            slots = self.create_time_slots(start_time, session_hour, session_amount, work_days)
            service = Service.objects.create(provider=provider, **validated_data)
            for slot in slots:
                # each index represents the work_day, start_time and end_time in the slot tuple respectively.
                
                TimeSlot.objects.create(day=slot[0].lower(), start=slot[1], end=slot[2], service=service) 

            return service


    def create_time_slots(self, start_time:time, session_hour:float, session_amount:int, work_days:list):
        abstract_date = datetime.min.date()
        start_t = datetime.combine(abstract_date, start_time)
        slots=[]
        for day in work_days:
            
            current_time = start_t
            for i in range(session_amount):
                end_time = current_time + timedelta(hours=session_hour)
                slot = (day, current_time.time(), end_time.time())
                slots.append(slot)
                current_time+=timedelta(hours=session_hour)    
        return slots


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['day', 'start']


class AppointmentSerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True, source='service')
    service = ServiceSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    time_slot = serializers.ListField(write_only=True)
    class Meta:
        model = Appointment
        fields = ['id', 'service_id', 'service', 'customer', 'is_accepted', 'status', 'time_slot']
        extra_kwargs = {
            'is_accepted':{'read_only':True},
            'status':{'read_only':True}
        }

    def validate_time_slot(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("Value must be a list with 2 objects.")
        
        day, start_time = value
        
        if not isinstance(day, str):
            raise serializers.ValidationError(f"day must be a string. e.g., '{datetime.today().date()}'")
        
        if not isinstance(start_time, str):
            raise serializers.ValidationError("start_time must be time objects. e.g., '12:00'.")
        date_ = datetime.strptime(f"{day} 00:00:00", "%Y-%m-%d %H:%M:%S").date()
        if date_ < date.today():
            raise serializers.ValidationError("Date cannot be in the past.")
        
        if date_ > (date.today() + timedelta(days=7)):
            raise serializers.ValidationError("Appointment cannot be booked more that 7 days in the future.")
        return value


    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        slot = validated_data.pop('time_slot', None)
        self.day = slot[0]
        self.start = slot[1]

        import calendar
        date = datetime.strptime(f"{self.day} {self.start}", "%Y-%m-%d %H:%M").date()
        time = datetime.strptime(f"{self.day} {self.start}", "%Y-%m-%d %H:%M").time()
        weekday = date.weekday()
        
        if calendar.day_abbr[weekday].lower() in [ time_slot.day.lower() for time_slot in TimeSlot.objects.filter(service=service) ]:
            if time in [ time_slot.start for time_slot in TimeSlot.objects.filter(service=service)]:
                with transaction.atomic():
                    if not Schedule.objects.filter(date=date, time=self.start).exists():
                        appointment = Appointment.objects.create(service=service, customer=user)
                        Schedule.objects.create(date=date, time=self.start, appointment=appointment)
                        return appointment
                    raise serializers.ValidationError("This time schedule is booked by another user.")
            raise serializers.ValidationError(f"Unavailable timestamp for appointments on this service.")
        raise serializers.ValidationError(f"The provider is not available on {calendar.day_name[weekday]}")


    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            schedule = Schedule.objects.get(appointment=instance)
            data["appt_timestamp"] = {
                "date":str(schedule.date),
                "time":str(schedule.time)
            }
            
        except schedule.DoesNotExist:
            data["appt_timestamp"] = None
        
        return data