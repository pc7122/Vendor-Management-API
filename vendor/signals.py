from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PurchaseOrder


@receiver([post_save, post_delete], sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, **kwargs):
    vendor = instance.vendor

    if vendor:
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

            all_pos_count = PurchaseOrder.objects.filter(vendor=vendor).count()
            successful_pos_count = PurchaseOrder.objects.filter(
                vendor=vendor, status='completed').count()
            fulfillment_rate = (successful_pos_count /
                                all_pos_count) * 100 if all_pos_count != 0 else 0
            vendor.fulfillment_rate = fulfillment_rate

            vendor.save()
