from __future__ import annotations

from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    total_contacts = serializers.IntegerField()
    open_deals = serializers.IntegerField()
    open_deals_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    won_this_month = serializers.IntegerField()
    lost_this_month = serializers.IntegerField()
