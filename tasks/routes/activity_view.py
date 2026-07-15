from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend
from tasks.filters import ActivityFilter
from drf_spectacular.utils import extend_schema

import logging

from tasks.models import Task
from common.permissions import (
    IsEmployee, IsManager, IsAdmin,
    check_object_permission,get_visible_queryset)
from common.pagination import StandardPagination
from tasks.routes.serializers import ActivitySerializer
from tasks.models import Activity

logger = logging.getLogger('contact')



class ActivaListAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityFilter
    search_fields = ['activity_type']
    ordering_fields = ['activity_type', 'created_at']


    def get_permissions(self):
        return [(IsAdmin | IsManager | IsEmployee)()]


    @extend_schema(summary="Barcha activ lidlar", responses={200: ActivitySerializer(many=True)}, tags=["Activ"])
    def get(self, request):
        queryset = Activity.objects.select_related("contact")
        queryset = get_visible_queryset(request.user, queryset, owner_field="user")

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ActivitySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    


    @extend_schema(summary="Yangi activity yaratish", request=ActivitySerializer, responses={201: ActivitySerializer}, tags=["Activ"])
    def post(self, request):
        data = request.data.copy()

        serializer = ActivitySerializer(data=data)

        if not serializer.is_valid():
            logger.warning(
                f"[CREATE-FAILED] user={request.user} errors={serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        activity = serializer.save(user=request.user)

        logger.info(
            f"[CREATE] user={request.user} activity_id={activity.id}"
        )

        return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)



class ActivityDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Activity.objects.none()
 
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsManager()]
        return [(IsManager | IsEmployee)()]
 

    def get_object(self, request, pk):
        try:
            activity = Activity.objects.select_related("contact", "user").get(pk=pk)
        except Activity.DoesNotExist:
            return None
        check_object_permission(request.user, activity, owner_field="user")
        return activity
 

    @extend_schema(summary="Activity tafsilotlari (Detail)", responses={200: ActivitySerializer}, tags=["Activ"])
    def get(self, request, pk):
        try:
            activity = self.get_object(request, pk)
        except PermissionDenied as exc:
            logger.warning(f"[GET-FORBIDDEN] Activity ID {pk} - user: {request.user} - {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
 
        if activity is None:
            return Response({"detail": "Activity topilmadi."}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = ActivitySerializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)
 

    @extend_schema(summary="Activityni to'liq yangilash (PUT)", request=ActivitySerializer, responses={200: ActivitySerializer}, tags=["Activ"])
    def put(self, request, pk):
        try:
            activity = self.get_object(request, pk)
        except PermissionDenied as exc:
            logger.warning(f"[UPDATE-FORBIDDEN] Activity ID {pk} - user: {request.user} - {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
 
        if activity is None:
            return Response({"detail": "Activity topilmadi."}, status=status.HTTP_404_NOT_FOUND)
 
        data = request.data.copy()
        data.pop("user", None)
        data.pop("user_id", None)
 
        serializer = ActivitySerializer(activity, data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE-PUT] Activity ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
 
        logger.warning(f"[UPDATE-FAILED] Activity ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

    @extend_schema(summary="Activityni qisman yangilash (PATCH)", request=ActivitySerializer, responses={200: ActivitySerializer}, tags=["Activ"])
    def patch(self, request, pk):
        try:
            activity = self.get_object(request, pk)
        except PermissionDenied as exc:
            logger.warning(f"[UPDATE-FORBIDDEN] Activity ID {pk} - user: {request.user} - {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
 
        if activity is None:
            return Response({"detail": "Activity topilmadi."}, status=status.HTTP_404_NOT_FOUND)
 
        data = request.data.copy()
        data.pop("user", None)
        data.pop("user_id", None)
 
        serializer = ActivitySerializer(activity, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE-PATCH] Activity ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
 
        logger.warning(f"[UPDATE-FAILED] Activity ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

    @extend_schema(summary="Activityni o'chirish (DELETE)", responses={204: None}, tags=["Activ"])
    def delete(self, request, pk):
        try:
            activity = self.get_object(request, pk)
        except PermissionDenied as exc:
            logger.warning(f"[DELETE-FORBIDDEN] Activity ID {pk} - user: {request.user} - {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
 
        if activity is None:
            return Response({"detail": "Activity topilmadi."}, status=status.HTTP_404_NOT_FOUND)
 
        logger.info(f"[DELETE] Activity ID {pk} o'chirildi - user: {request.user}")
        activity.delete()
        return Response({"detail": "Activity muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)
 