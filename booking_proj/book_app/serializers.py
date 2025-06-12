from rest_framework import serializers
from .models import *
from django.db import transaction
from django.core.validators import MinValueValidator
from rest_framework.response import Response
from datetime import timedelta, time, datetime



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
                
                TimeSlot.objects.create(day=slot[0], start=slot[1], end=slot[2], service=service) 

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
        fields = ['day', 'start', 'end']


class AppointmentSerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)
    service = ServiceSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    time_slot = serializers.JSONField(default=list)
    class Meta:
        model = Appointment
        fields = ['id', 'service_id', 'service', 'customer', 'is_accepted', 'status', 'time_slot']
        extra_kwargs = {
            'is_accepted':{'read_only':True},
            'status':{'read_only':True}
        }

    def validate_time_slot(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Value must be a list with 3 objects.")
        
        day, start_time, end_time = value
        
        if not isinstance(day, str):
            raise serializers.ValidationError("day must be a string. e.g., 'mon', 'tue'...")
        
        if not isinstance(start_time, str) or not isinstance(end_time, str):
            raise serializers.ValidationError("start_time and end_time elements must be time objects. e.g., '12:00'.")

        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        service_id = validated_data['service_id']
        day = validated_data['time_slot'][0]
        start = validated_data['time_slot'][1]
        end = validated_data['time_slot'][2]
        time_slot =  TimeSlot.objects.get(day=day, start=start, end=end, service=service_id)
       
        if time_slot.appointment is None:
            with transaction.atomic():
                appointment = Appointment.objects.create(service=service_id, customer=user)
                time_slot.appointment = appointment
                time_slot.save()
                return appointment
        raise serializers.ValidationError("Time slot is taken by another appointment.")