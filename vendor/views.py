from django.db import models
from rest_framework import generics
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer


class VendorListCreate(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class VendorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class PurchaseOrderListCreate(generics.ListCreateAPIView):
    serializer_class = PurchaseOrderSerializer

    def get_queryset(self):
        queryset = PurchaseOrder.objects.all()
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        vendor = instance.vendor

        if instance.status == 'completed':
            completed_pos = PurchaseOrder.objects.filter(
                vendor=vendor, status='completed')
            on_time_delivery_pos = completed_pos.filter(
                delivery_date__lte=instance.delivery_date)
            on_time_delivery_rate = on_time_delivery_pos.count() / completed_pos.count() * 100
            vendor.on_time_delivery_rate = on_time_delivery_rate
            vendor.save()

            if instance.quality_rating:
                quality_rating_avg = completed_pos.exclude(quality_rating__isnull=True).aggregate(
                    avg_rating=models.Avg('quality_rating'))['avg_rating']
                vendor.quality_rating_avg = quality_rating_avg
                vendor.save()

        # Calculate average response time
        if instance.acknowledgment_date:
            response_times = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False, issue_date__isnull=False).annotate(
                response_time=models.ExpressionWrapper(models.F('acknowledgment_date') - models.F('issue_date'), output_field=models.FloatField()))
            avg_response_time = response_times.aggregate(
                avg_response=models.Avg('response_time'))['avg_response']
            vendor.average_response_time = avg_response_time
            vendor.save()

        # Calculate fulfillment rate
        all_pos_count = PurchaseOrder.objects.filter(vendor=vendor).count()
        successful_pos_count = PurchaseOrder.objects.filter(
            vendor=vendor, status='completed').count()
        fulfillment_rate = (successful_pos_count /
                            all_pos_count) * 100 if all_pos_count != 0 else 0
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()

        return instance


class PurchaseOrderRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    lookup_field = 'po_number'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if 'status' in request.data:
            vendor = instance.vendor
            completed_pos = PurchaseOrder.objects.filter(
                vendor=vendor, status='completed')
            completed_pos_count = completed_pos.count()
            if completed_pos_count > 0:
                on_time_delivery_pos_count = completed_pos.filter(
                    delivery_date__lte=instance.delivery_date).count()
                on_time_delivery_rate = (
                    on_time_delivery_pos_count / completed_pos_count) * 100
                vendor.on_time_delivery_rate = on_time_delivery_rate

                quality_rating_avg = completed_pos.exclude(quality_rating__isnull=True).aggregate(
                    avg_rating=models.Avg('quality_rating'))['avg_rating']
                vendor.quality_rating_avg = quality_rating_avg

                response_times = completed_pos.exclude(acknowledgment_date__isnull=True).annotate(response_time=models.ExpressionWrapper(
                    models.F('acknowledgment_date') - models.F('issue_date'), output_field=models.FloatField()))
                avg_response_time = response_times.aggregate(
                    avg_response=models.Avg('response_time'))['avg_response']
                vendor.average_response_time = avg_response_time

                all_pos_count = PurchaseOrder.objects.filter(
                    vendor=vendor).count()
                successful_pos_count = PurchaseOrder.objects.filter(
                    vendor=vendor, status='completed').count()
                fulfillment_rate = (
                    successful_pos_count / all_pos_count) * 100 if all_pos_count != 0 else 0
                vendor.fulfillment_rate = fulfillment_rate

                vendor.save()

        return Response(serializer.data)


class VendorPerformance(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        performance_data = {
            'on_time_delivery_rate': instance.on_time_delivery_rate,
            'quality_rating_avg': instance.quality_rating_avg,
            'average_response_time': instance.average_response_time,
            'fulfillment_rate': instance.fulfillment_rate,
        }
        return Response(performance_data)
