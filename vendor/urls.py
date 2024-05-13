from django.urls import path
from . import views

urlpatterns = [
    path('vendors/', views.VendorListCreate.as_view(),
         name='vendor-list-create'),
    path('vendors/<int:pk>/', views.VendorRetrieveUpdateDestroy.as_view(),
         name='vendor-retrieve-update-destroy'),
    path('purchase_orders/', views.PurchaseOrderListCreate.as_view(),
         name='purchase-order-list-create'),
    path('purchase_orders/<int:po_number>/', views.PurchaseOrderRetrieveUpdateDestroy.as_view(),
         name='purchase-order-retrieve-update-destroy'),
    path('vendors/<int:pk>/performance/',
         views.VendorPerformance.as_view(), name='vendor-performance'),
]
