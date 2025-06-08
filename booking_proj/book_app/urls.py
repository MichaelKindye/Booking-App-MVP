from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns=[
    path('sign-up/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('home/', views.ListServicesAPIView.as_view(), name='List-Services'),
    path('services/', views.ListCreateServiceAPIView.as_view(), name='List-Create-Services'),
    path('appointments/', views.CreateAppointmentAPIView.as_view(), name='Create-Appointments'),
    path('accept_appt/<int:pk>/', views.AcceptAppointmentAPIView.as_view(), name='Accept-Appointment'),
]