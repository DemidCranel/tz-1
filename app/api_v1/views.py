import pandas as pd
from drf_excel.renderers import XLSXRenderer
from rest_framework import viewsets
from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.renderers import JSONRenderer

from .models import *
from .paginations import *
from .renderers import *
from .serializers import *


class IsAuthenticatedOrReadAndCreated(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.method in SAFE_METHODS or request.method == "POST")
            or (request.user and request.user.is_authenticated)
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = [JSONRenderer, CSVRenderer, XLSXRenderer]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = [JSONRenderer, CSVRenderer, XLSXRenderer]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = [JSONRenderer, CSVRenderer, XLSXRenderer]


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = (IsAuthenticatedOrReadAndCreated,)
    renderer_classes = [JSONRenderer, CSVRenderer, XLSXRenderer]
