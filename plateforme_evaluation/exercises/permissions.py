from rest_framework import permissions

class IsProfessor(permissions.BasePermission):
    """
    Permission personnalisée qui permet uniquement aux professeurs d'accéder à la vue.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PROFESSOR'