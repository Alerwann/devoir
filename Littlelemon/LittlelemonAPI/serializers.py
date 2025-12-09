"""Littlelemon/serializers.py (Créez ce fichier si vous ne l'avez pas)"""

from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour Category"""

    class Meta:
        model = Category

        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    """Ceci affichera le 'title' de la catégorie au lieu de son ID"""

    category = serializers.StringRelatedField()

    class Meta:
        model = MenuItem

        fields = ["id", "title", "price", "featured", "category"]


class CartSerializer(serializers.ModelSerializer):
    """Serializer de cart"""

    class Meta:
        model = Cart
        fields = [
            "id",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
        ]
        read_only_fields = ["user", "unit_price", "price"]

class OrderItemSerializer(serializers.ModelSerializer):
    """serializer de la commande"""

    class Meta:
        model = Order
        fiels = [
            "id",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
        ]
        read_only_fields= ["unit_price", "price"]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer pour la commande (Order)"""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user", 
            "delivery_crew",  
            "status",  
            "total",  
            "date", 
            "items",  
        ]

        read_only_fields = ["user", "delivery_crew", "status", "total", "date"]
