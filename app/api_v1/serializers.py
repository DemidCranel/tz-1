import datetime
from dataclasses import fields

from django.forms import model_to_dict
from rest_framework import serializers

from .models import *


class SupplierSerializer(serializers.ModelSerializer):

    class SupplierProductsSerializer(serializers.ModelSerializer):
        sum_quantity = serializers.SerializerMethodField("get_sum_quantity")

        def get_sum_quantity(self, obj):
            stock_movement = StockMovement.objects.filter(product=obj)
            result = 0
            for i in stock_movement:
                result += i.quantity
            return result

        class Meta:
            model = Product
            fields = "__all__"

    products_supplier = serializers.SerializerMethodField("get_products")
    category_supplier = serializers.SerializerMethodField("get_category")

    def get_products(self, obj):
        product_obj = Product.objects.filter(supplier=obj)
        products_queryset = self.SupplierProductsSerializer(product_obj, many=True).data
        return products_queryset

    def get_category(self, obj):
        category_queryset = obj.category
        if category_queryset:
            result = model_to_dict(category_queryset)
            return result

    class Meta:
        model = Supplier
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    suppliers = serializers.SerializerMethodField("get_suppliers")

    def get_suppliers(self, obj):
        suppliers_queryset = Supplier.objects.filter(category=obj)
        result = suppliers_queryset.values()
        return result

    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    last_stock_movement = serializers.SerializerMethodField("get_last_stock_movement")
    all_stock_movement = serializers.SerializerMethodField("get_all_stock_movement")

    def get_last_stock_movement(self, obj):
        sorted_all_stock_movement = StockMovement.objects.filter(product=obj).order_by(
            "-date"
        )
        last_stock_movement = sorted_all_stock_movement[:5]
        result = last_stock_movement.values()
        return result

    def get_all_stock_movement(self, obj):
        all_stock_movement = StockMovement.objects.filter(product=obj)
        result = len(all_stock_movement)
        return result

    class Meta:
        model = Product
        fields = "__all__"


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = "__all__"

    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Invalid field value quantity")
        return value

    def validate_date(self, value):
        time_delta = value.utcoffset()
        time_zone = datetime.timezone(time_delta)
        actual_datetime = datetime.datetime.now(tz=time_zone)
        if value > actual_datetime:
            raise serializers.ValidationError("Incorrect datetime")
        return value
