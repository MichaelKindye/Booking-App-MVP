from rest_framework import serializers
from .models import *


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
            return User.objects.create_user(username=username, password=password, role=role)
       

class ServiceSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'provider', 'title', 'detail', 'price_per_session']



    def create(self, validated_data):
        user = self.context['request'].user
        return Service.objects.create(provider=user, **validated_data)
    

class AppointmentSerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)
    service = ServiceSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    class Meta:
        model = Appointment
        fields = ['id', 'service_id', 'service', 'customer', 'is_accepted', 'status']
        extra_kwargs = {
            'is_accepted':{'read_only':True},
            'status':{'read_only':True}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service_id']
        return Appointment.objects.create(service=service, customer=user)