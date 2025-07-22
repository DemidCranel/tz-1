from django.db import models
from django.utils import timezone


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, related_name="category", on_delete=models.SET_NULL, null=True
    )


class Product(models.Model):
    name = models.CharField(max_length=100)
    supplier = models.ForeignKey(
        Supplier, related_name="supplier", on_delete=models.SET_NULL, null=True
    )
    sku = models.PositiveIntegerField(unique=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)


class StockMovement(models.Model):
    operator_email = models.EmailField()
    product = models.ForeignKey(
        Product, related_name="product", on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField(default=timezone.now, blank=True)
    quantity = models.SmallIntegerField()
    note = models.CharField(max_length=1000, blank=True)
