from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'customer' or request.user.role == 'admin'
    
class IsProvider(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'provider' or request.user.role == 'admin'
    
class HasServicePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.provider == request.user or request.user.role == 'admin'