"""Littlelemon/views.py (Créez ce fichier si vous ne l'avez pas)"""

from django.template.defaultfilters import date
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import serializers

from .models import Cart, Category, MenuItem, Order, OrderItem
from .permissions import IsCustomer, IsManager, IsDeliveryCrew
from .serializers import (
    CartSerializer,
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
)

User = get_user_model()


class CategoryView(generics.ListCreateAPIView):
    """view des categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]


class MenuItemsView(generics.ListCreateAPIView):
    """Views des items"""

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    pagination_class = PageNumberPagination

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["price"]
    filterset_fields = ["category"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]


@api_view(["POST"])
@permission_classes([IsAdminUser])
def manager(request, userid):
    """définition du role manager"""
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    manager_group = Group.objects.get(name="Manager")

    user.groups.add(manager_group)
    return Response(
        {"message": f"User {userid} added to Manager group"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsManager])
def delivery_crew(request, userid):
    """Permet au Manager d'assigner un utilisateur à l'équipe de livraison"""

    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        delivery_group = Group.objects.get(name="Delivery crew")
    except Group.DoesNotExist:
        return Response(
            {"message": "Delivery crew group not found"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    user.groups.add(delivery_group)
    return Response(
        {"message": f"User {userid} added to Delivery crew group"},
        status=status.HTTP_201_CREATED,
    )


class MenuItemDetailView(RetrieveUpdateDestroyAPIView):
    """Details des menus"""

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):

        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAdminUser() | IsManager()]


class CartView(ListCreateAPIView):
    """view du panier"""

    serializer_class = CartSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):

        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data["menuitem"]
        quantity = serializer.validated_data["quantity"]
        unit_price = menuitem.price
        price = unit_price * quantity

        serializer.save(user=self.request.user, unit_price=unit_price, price=price)


class OrderView(ListCreateAPIView):
    """View de la commande"""

    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Manager").exists() or user.is_staff:
            return Order.objects.all()

        if user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user

        # 1. Récupérer les articles du panier
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            # Il est préférable de gérer cette erreur ici avant la transaction
            raise serializers.ValidationError(
                "Le panier est vide. Impossible de passer commande."
            )

        with transaction.atomic():

            order = serializer.save(
                user=user,
                date=date.today(),
                total=0.00,
            )

            total_price = 0
            order_items_to_create = []

            for cart_item in cart_items:

                order_item = OrderItem(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price,
                )
                order_items_to_create.append(order_item)
                total_price += cart_item.price

            OrderItem.objects.bulk_create(order_items_to_create)

            order.total = total_price
            order.save()

            cart_items.delete()


class OrderDetailsView(RetrieveUpdateDestroyAPIView):
    """Permission pour la commande"""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        """administration des permission"""
        if self.request.method == "GET":
            return [IsCustomer()]
        return [IsManager() | IsDeliveryCrew()]

    def perform_update(self, serializer):
        user = self.request.user
        if user.groups.filter(name="Delivery crew").exists():
            data = self.request.data
            if set(data.keys()) > {"status"}:
                raise serializers.ValidationError(
                    {"message": "Vous ne pouvez modifier que le statut de la commande."}
                )

            if "status" in data:
                if data["status"] is True:
                    serializer.save()
                    return
                raise serializers.ValidationError(
                    {
                        "status": "Le livreur ne peut que marquer la commande comme livrée (True)."
                    }
                )
            else:
                raise serializers.ValidationError(
                    {"status": "Le livreur doit envoyer le champ 'status'."}
                )

        elif user.groups.filter(name="Manager").exists():
            data = self.request.data
            if set(data.keys()) > {"delivery_crew"}:
                raise serializers.ValidationError(
                    {
                        "message": "Le Manager ne peut modifier que l'équipe de livraison."
                    }
                )

            serializer.save()
            return

        else:
            raise serializers.ValidationError(
                {"message": "Vous n'êtes pas autorisé à modifier cette commande."}
            )
