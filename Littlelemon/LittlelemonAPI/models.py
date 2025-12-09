"""Models definition"""

from django.db import models
from django.conf import settings


# Create your models here.
class Category(models.Model):
    """Definition des catégorie"""

    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)


class MenuItem(models.Model):
    """Definition des menus"""

    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)


class Cart(models.Model):
    """Definition du panier"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        """Meta de cart"""

        unique_together = ("menuitem", "user")


class Order(models.Model):
    """Model de commande"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)


class OrderItem(models.Model):
    """Model items of order"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        """Meta de cart"""

        unique_together = ("order", "menuitem")
