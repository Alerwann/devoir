"""Liste des URLS"""

from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.CategoryView.as_view(), name="categories"),
    path("menu-items/", views.MenuItemsView.as_view(), name="menu-items"),
    path("groups/manager/users/<int:userid>", views.manager, name="assign-manager"),
    path(
        "groups/delivery-crew/users/<int:userid>",
        views.delivery_crew,
        name="assign-delivery-crew",
    ),
    path(
        "menu-items/<int:pk>",
        views.MenuItemDetailView.as_view(),
        name="menu-item-detail",
    ),
    path("cart/menu-items", views.CartView.as_view(), name="cart-items"),
    path("orders/", views.OrderView.as_view(), name="orders"),
    path("orders/<int:pk>", views.OrderDetailsView.as_view(), name="order-detail"),
]
