"""creation des permissions"""

from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    """Permission personnalisée pour le groupe 'Manager'."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Vérifie si l'utilisateur appartient au groupe 'Manager'
        return request.user.groups.filter(name="Manager").exists()


class IsDeliveryCrew(BasePermission):
    """Permission personnalisée pour le groupe 'Delivery crew'."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Vérifie si l'utilisateur appartient au groupe 'Delivery crew'
        return request.user.groups.filter(name="Delivery crew").exists()


class IsCustomer(BasePermission):
    """
    Permission pour les clients (utilisateurs authentifiés sans rôle Manager/Delivery).
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        is_manager = request.user.groups.filter(name="Manager").exists()
        is_delivery = request.user.groups.filter(name="Delivery crew").exists()

        return not (is_manager or is_delivery)
