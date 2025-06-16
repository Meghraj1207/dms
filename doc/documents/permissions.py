
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsInitiator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'initiator'

class IsReviewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'reviewer'

class IsApprover(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'approver'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
