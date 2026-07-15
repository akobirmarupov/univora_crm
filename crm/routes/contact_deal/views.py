from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from crm.filters import ContactFilter, DealFilter
from drf_spectacular.utils import extend_schema

import logging

from crm.models import Contact, Deal
from common.permissions import (
    IsEmployee,
    IsManager,
    PermissionDenied,
    check_object_permission,
    get_visible_queryset,
)
from common.pagination import StandardPagination
from crm.routes.contact_deal.serializers import ContactSerializer, DealSerializer


contact_logger = logging.getLogger('contact')
deal_logger = logging.getLogger('deal')


class ContactListAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ContactFilter
    search_fields = ['full_name', 'phone_number', 'email', 'company__name']
    ordering_fields = ['full_name', 'created_at', 'status']

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    @extend_schema(summary="Barcha lid contactlari", responses={200: ContactSerializer(many=True)}, tags=["Contact"])
    def get(self, request):
        queryset = Contact.objects.select_related("company")
        queryset = get_visible_queryset(request.user, queryset, owner_field="created_by")

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ContactSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(summary="Yangi Contact yaratish", request=ContactSerializer, responses={201: ContactSerializer}, tags=["Contact"])
    def post(self, request):
        serializer = ContactSerializer(data=request.data)

        if not serializer.is_valid():
            contact_logger.warning(
                f"[CREATE-FAILED] user={request.user} errors={serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contact = serializer.save(created_by=request.user)

        contact_logger.info(
            f"[CREATE] user={request.user} contact_id={contact.id} "
            f"full_name={contact.full_name} phone={contact.phone_number}"
        )

        return Response(ContactSerializer(contact).data, status=status.HTTP_201_CREATED)


class ContactDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Contact.objects.none()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsManager()]
        return [(IsManager | IsEmployee)()]

    def get_object(self, request, pk):
        try:
            contact = Contact.objects.select_related("company", "created_by").get(pk=pk)
        except Contact.DoesNotExist:
            return None

        check_object_permission(request.user, contact, owner_field="created_by")
        return contact

    @extend_schema(summary="Contact tafsilotlari (Detail)", responses={200: ContactSerializer}, tags=["Contact"])
    def get(self, request, pk):
        contact = self.get_object(request, pk)

        if contact is None:
            return Response({"detail": "Contact topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactSerializer(contact)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Contactni to'liq yangilash (PUT)", request=ContactSerializer, responses={200: ContactSerializer}, tags=["Contact"])
    def put(self, request, pk):
        contact = self.get_object(request, pk)

        if contact is None:
            return Response({"detail": "Contact topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if "created_by_id" in request.data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager contact'ni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            contact_logger.info(f"[UPDATE-PUT] Contact ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        contact_logger.warning(f"[UPDATE-FAILED] Contact ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Contactni qisman yangilash (PATCH)", request=ContactSerializer, responses={200: ContactSerializer}, tags=["Contact"])
    def patch(self, request, pk):
        contact = self.get_object(request, pk)

        if contact is None:
            return Response({"detail": "Contact topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if "created_by_id" in request.data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager contact'ni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            contact_logger.info(f"[UPDATE-PATCH] Contact ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        contact_logger.warning(f"[UPDATE-FAILED] Contact ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Contactni o'chirish (DELETE)", responses={204: None}, tags=["Contact"])
    def delete(self, request, pk):
        contact = self.get_object(request, pk)

        if contact is None:
            return Response({"detail": "Contact topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        contact_logger.info(f"[DELETE] Contact ID {pk} ({contact.full_name}) o'chirildi - user: {request.user}")
        contact.delete()
        return Response({"detail": "Contact muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)


class DealListAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DealFilter
    search_fields = ['name', 'contact__full_name', 'contact__phone_number', 'contact__email', 'stage__name']
    ordering_fields = ['name', 'amount', 'opened_at', 'closed_at']

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    @extend_schema(summary="Barcha lid contactlari", responses={200: DealSerializer(many=True)}, tags=["Deal"])
    def get(self, request):
        queryset = Deal.objects.select_related("contact", "stage", "manager")
        queryset = get_visible_queryset(request.user, queryset, owner_field="manager")

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = DealSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(summary="Yangi bitim yaratish", request=DealSerializer, responses={201: DealSerializer}, tags=["Deal"])
    def post(self, request):
        data = request.data.copy()
        data.pop("manager_id", None)

        serializer = DealSerializer(data=data)

        if not serializer.is_valid():
            deal_logger.warning(
                f"[CREATE-FAILED] user={request.user} errors={serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        deal = serializer.save(manager=request.user)

        deal_logger.info(
            f"[CREATE] user={request.user} deal_id={deal.id} "
            f"name={deal.name} amount={deal.amount}"
        )

        return Response(DealSerializer(deal).data, status=status.HTTP_201_CREATED)


class DealDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Deal.objects.none()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsManager()]
        return [(IsManager | IsEmployee)()]

    def get_object(self, request, pk):
        try:
            deal = Deal.objects.select_related("contact", "stage", "manager").get(pk=pk)
        except Deal.DoesNotExist:
            return None

        check_object_permission(request.user, deal, owner_field="manager")
        return deal

    @extend_schema(summary="Bitim tafsilotlari (Detail)", responses={200: DealSerializer}, tags=["Deal"])
    def get(self, request, pk):
        deal = self.get_object(request, pk)

        if deal is None:
            return Response({"detail": "Bitim topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DealSerializer(deal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Bitimni to'liq yangilash (PUT)", request=DealSerializer, responses={200: DealSerializer}, tags=["Deal"])
    def put(self, request, pk):
        deal = self.get_object(request, pk)

        if deal is None:
            return Response({"detail": "Bitim topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if "manager_id" in request.data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager bitimni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DealSerializer(deal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            deal_logger.info(f"[UPDATE-PUT] Deal ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        deal_logger.warning(f"[UPDATE-FAILED] Deal ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Bitimni qisman yangilash (PATCH)", request=DealSerializer, responses={200: DealSerializer}, tags=["Deal"])
    def patch(self, request, pk):
        deal = self.get_object(request, pk)

        if deal is None:
            return Response({"detail": "Bitim topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if "manager_id" in request.data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager bitimni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DealSerializer(deal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            deal_logger.info(f"[UPDATE-PATCH] Deal ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        deal_logger.warning(f"[UPDATE-FAILED] Deal ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Bitimni o'chirish (DELETE)", responses={204: None}, tags=["Deal"])
    def delete(self, request, pk):
        deal = self.get_object(request, pk)

        if deal is None:
            return Response({"detail": "Bitim topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        deal_logger.info(f"[DELETE] Deal ID {pk} ({deal.name}) o'chirildi - user: {request.user}")
        deal.delete()
        return Response({"detail": "Bitim muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)