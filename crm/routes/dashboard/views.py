from __future__ import annotations

from django.db.models import Sum
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from drf_spectacular.utils import extend_schema

from crm.routes.dashboard.serializer import DashboardSerializer
from crm.models import Contact, Deal, Stage
from common.permissions import IsEmployee, IsManager, get_visible_queryset


class DashboardAPIView(APIView):

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    @extend_schema(
        summary="Asosiy ko'rsatkichlar (dashboard)",
        responses={200: DashboardSerializer},
        tags=["Dashboard"],
    )
    def get(self, request):
        user = request.user

        contacts = get_visible_queryset(user, Contact.objects.all(), owner_field="created_by")
        deals = get_visible_queryset(user, Deal.objects.all(), owner_field="manager")

        month_start = timezone.now().replace(day=1).date()

        open_deals_qs = deals.filter(closed_at__isnull=True)
        won_qs = deals.filter(closed_at__gte=month_start, stage__name=Stage.WON_STAGE_NAME)
        lost_qs = deals.filter(closed_at__gte=month_start, stage__name=Stage.LOST_STAGE_NAME)

        data = {
            "total_contacts": contacts.count(),
            "open_deals": open_deals_qs.count(),
            "open_deals_amount": open_deals_qs.aggregate(total=Sum("amount"))["total"] or 0,
            "won_this_month": won_qs.count(),
            "lost_this_month": lost_qs.count(),
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)