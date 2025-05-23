# accounts/permissions.py

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée qui permet uniquement au propriétaire d'un objet 
    ou à un administrateur d'accéder à l'objet.
    """
    
    def has_object_permission(self, request, view, obj):
        # Les administrateurs ont toujours l'accès complet
        if request.user.is_staff:
            return True
        
        # Détermine si l'objet a un propriétaire
        if hasattr(obj, 'user'):
            # Le propriétaire a l'accès
            return obj.user == request.user
        else:
            # L'objet est l'utilisateur lui-même
            return obj == request.user


class IsProfessor(permissions.BasePermission):
    """
    Permission personnalisée qui permet uniquement aux utilisateurs avec le rôle 
    de professeur d'accéder à la vue.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PROFESSOR'


class IsStudent(permissions.BasePermission):
    """
    Permission personnalisée qui permet uniquement aux utilisateurs avec le rôle 
    d'étudiant d'accéder à la vue.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'