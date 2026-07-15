from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from tasks.filters import TaskFilter
from drf_spectacular.utils import extend_schema

import logging

from tasks.models import Task
from common.permissions import (
    IsEmployee,
    IsManager,
    PermissionDenied,
    check_object_permission,
    get_visible_queryset,
)
from common.pagination import StandardPagination
from tasks.routes.serializers import TaskSerializer

logger = logging.getLogger('contact')


class TaskListAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['description']
    ordering_fields = ['due_date', 'created_at', 'is_done']

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    @extend_schema(summary="Barcha vazifalar", responses={200: TaskSerializer(many=True)}, tags=["Task"])
    def get(self, request):
        queryset = Task.objects.select_related("contact", "deal", "assigned_to")
        queryset = get_visible_queryset(request.user, queryset, owner_field="assigned_to")

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = TaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(summary="Yangi task yaratish", request=TaskSerializer, responses={201: TaskSerializer}, tags=["Task"])
    def post(self, request):
        data = request.data.copy()

        if "assigned_to_id" in data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager taskni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskSerializer(data=data)

        if not serializer.is_valid():
            logger.warning(
                f"[CREATE-FAILED] user={request.user} errors={serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        assigned_to = serializer.validated_data.get("assigned_to", request.user)
        task = serializer.save(assigned_to=assigned_to)

        logger.info(
            f"[CREATE] user={request.user} task_id={task.id} assigned_to={task.assigned_to_id}"
        )

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Task.objects.none()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsManager()]
        return [(IsManager | IsEmployee)()]

    def get_object(self, request, pk):
        try:
            task = Task.objects.select_related("contact", "deal", "assigned_to").get(pk=pk)
        except Task.DoesNotExist:
            return None

        check_object_permission(request.user, task, owner_field="assigned_to")
        return task

    @extend_schema(summary="Task tafsilotlari (Detail)", responses={200: TaskSerializer}, tags=["Task"])
    def get(self, request, pk):
        task = self.get_object(request, pk)

        if task is None:
            return Response({"detail": "Task topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Taskni to'liq yangilash (PUT)", request=TaskSerializer, responses={200: TaskSerializer}, tags=["Task"])
    def put(self, request, pk):
        task = self.get_object(request, pk)

        if task is None:
            return Response({"detail": "Task topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if "assigned_to_id" in request.data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager taskni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE-PUT] Task ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"[UPDATE-FAILED] Task ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Taskni qisman yangilash (PATCH)", request=TaskSerializer, responses={200: TaskSerializer}, tags=["Task"])
    def patch(self, request, pk):
        task = self.get_object(request, pk)

        if task is None:
            return Response({"detail": "Task topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if "assigned_to_id" in request.data and not (request.user.role in ("admin", "manager")):
            return Response(
                {"detail": "Faqat admin va manager taskni boshqa xodimga biriktira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE-PATCH] Task ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"[UPDATE-FAILED] Task ID {pk} - user: {request.user} errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Taskni o'chirish (DELETE)", responses={204: None}, tags=["Task"])
    def delete(self, request, pk):
        task = self.get_object(request, pk)

        if task is None:
            return Response({"detail": "Task topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"[DELETE] Task ID {pk} o'chirildi - user: {request.user}")
        task.delete()
        return Response({"detail": "Task muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)