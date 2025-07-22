from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, ProductViewSet, StockMovementViewSet,
                    SupplierViewSet)

router = routers.SimpleRouter()
router.register(r"category", CategoryViewSet)
router.register(r"supplier", SupplierViewSet)
router.register(r"product", ProductViewSet)
router.register(r"stockmovement", StockMovementViewSet)

urlpatterns = [path("", include(router.urls))]
