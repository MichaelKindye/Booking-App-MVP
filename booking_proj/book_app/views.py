from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import *
from .permissions import *


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')
        if username and password and role:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise ValueError('Invalid credentials were given!')
     

class ListCreateServiceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProvider]
    def get(self, request):
        services = Service.objects.filter(provider=request.user)
        try:
            serializer = ServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        try:
            data = request.data
            serializer = ServiceSerializer(data=data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class CreateAppointmentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    def get(self, request):
        appointments = Appointment.objects.filter(customer=request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        try:
            data = request.data
            serializer = AppointmentSerializer(data=data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class ListServicesAPIView(APIView):
    def get(self, request):
        try:
            services = Service.objects.all()
            serializer = ServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class AcceptAppointmentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProvider]
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            if appointment.service.provider == request.user:
                appointment.is_accepted = True
                appointment.save()
                serializer = AppointmentSerializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error":"You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        