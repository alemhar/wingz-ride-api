from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Custom permission to only allow users with 'admin' role.
    """
    message = "Only users with admin role can access this API."
    
    def has_permission(self, request, view):
        # Check if user is authenticated and has admin role
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )