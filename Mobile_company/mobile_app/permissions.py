# permissions.py
from rest_framework.permissions import BasePermission

class IsActiveSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.is_staff and
            request.user.is_superuser
        )
        
        
class IsCeo(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="ceo"
            except AttributeError:
                    return False
class IsHr(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="hr"
            except AttributeError:
                    return False


class IsSaleManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False 
        try:
            employee=request.user.employee
            return employee.job_id.job_name.lower()=="sales manager"
        except AttributeError:
                    return False


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="manager"
            except AttributeError:
                    return False


class IsWarehouseManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        else:
            try:
                employee=request.user.employee
                return employee.job_id.job_name.lower()=="warehouse manager"
            except AttributeError:
                return False
    