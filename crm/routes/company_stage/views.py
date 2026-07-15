from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from crm.filters import CompanyFilter, StageFilter
from drf_spectacular.utils import extend_schema

from django.core.cache import cache
import logging

from crm.models import Company, Stage
from common.permissions import IsEmployee, IsManager, PermissionDenied, check_object_permission, get_visible_queryset
from common.pagination import StandardPagination
from crm.routes.company_stage.serializers import CompanySerializer, StageSerializer


logger = logging.getLogger('company')
stage_logger = logging.getLogger('stage')


class CompanyListAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ['name', 'industry', 'website']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    @extend_schema(summary="Barcha lidlar", responses={200: CompanySerializer(many=True)}, tags=["Company"])
    def get(self, request):
        user = request.user
        company_version = cache.get("company_cache_version", 1)
        cache_key = f"company_list_{user.id}_{request.query_params.urlencode()}_{company_version}"
        data = cache.get(cache_key)

        if data is None:
            queryset = Company.objects.all().order_by('name')
            queryset = get_visible_queryset(request.user, queryset, owner_field="created_by")

            for backend in self.filter_backends:
                queryset = backend().filter_queryset(request, queryset, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)

            if page is not None:
                serializer = CompanySerializer(page, many=True)
                data = paginator.get_paginated_response(serializer.data).data
            else:
                serializer = CompanySerializer(queryset, many=True)
                data = serializer.data

            cache.set(cache_key, data, timeout=60 * 6)

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(summary="Yangi Lid yaratish", request=CompanySerializer, responses={201: CompanySerializer}, tags=["Company"])
    def post(self, request):
        serializer = CompanySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            cache.delete_pattern("company_list_*")
            logger.info(f"[CREATE] Company '{serializer.data['name']}' - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyDetailAPIView(APIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [IsManager | IsEmployee]

    def get_object(self, pk, request):
        try:
            company = Company.objects.get(pk=pk)
            check_object_permission(request.user, company, owner_field="created_by")
            return company
        except Company.DoesNotExist:
            return None
        except PermissionDenied:
            return None

    @extend_schema(summary="Kompaniya tafsilotlari (Detail)", responses={200: CompanySerializer}, tags=["Company"])
    def get(self, request, pk):
        company_version = cache.get("company_cache_version", 1)
        cache_key = f"company_detail_{pk}_v{company_version}"

        try:
            data = cache.get(cache_key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            data = None

        if data is None:
            company = self.get_object(pk, request)
            if company is None:
                return Response({"detail": "Kompaniya topilmadi yoki sizda ruxsat yo'q."}, status=status.HTTP_404_NOT_FOUND)

            serializer = CompanySerializer(company)
            data = serializer.data

            try:
                cache.set(cache_key, data, timeout=60*10)
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(summary="Kompaniyani to'liq yangilash (PUT)", request=CompanySerializer, responses={200: CompanySerializer}, tags=["Company"])
    def put(self, request, pk):
        company = self.get_object(pk, request)
        if company is None:
            return Response({"detail": "Kompaniya topilmadi yoki sizda ruxsat yo'q."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()

            try:
                cache.incr("company_cache_version")
            except ValueError:
                cache.set("company_cache_version", 1)

            logger.info(f"[UPDATE-PUT] Company ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Kompaniyani qisman yangilash (PATCH)", request=CompanySerializer, responses={200: CompanySerializer}, tags=["Company"])
    def patch(self, request, pk):
        company = self.get_object(pk, request)
        if company is None:
            return Response({"detail": "Kompaniya topilmadi yoki sizda ruxsat yo'q."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            try:
                cache.incr("company_cache_version")
            except ValueError:
                cache.set("company_cache_version", 1)

            logger.info(f"[UPDATE-PATCH] Company ID {pk} qisman yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Kompaniyani o'chirish (DELETE)", responses={204: None}, tags=["Company"])
    def delete(self, request, pk):
        company = self.get_object(pk, request)
        if company is None:
            return Response({"detail": "Kompaniya topilmadi yoki sizda ruxsat yo'q."}, status=status.HTTP_404_NOT_FOUND)

        company.delete()

        try:
            cache.incr("company_cache_version")
        except ValueError:
            cache.set("company_cache_version", 1)

        logger.info(f"[DELETE] Company ID {pk} o'chirildi - user: {request.user}")
        return Response({"detail": "Kompaniya muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)


class StageListAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StageFilter
    search_fields = ['name']
    ordering_fields = ['order', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager()]
        return [IsEmployee()]

    @extend_schema(summary="Barcha bosqichlar", responses={200: StageSerializer(many=True)}, tags=["Stage"])
    def get(self, request):
        queryset = Stage.objects.all().order_by('order')

        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            serializer = StageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = StageSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Yangi bosqich yaratish", request=StageSerializer, responses={201: StageSerializer}, tags=["Stage"])
    def post(self, request):
        serializer = StageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"[CREATE] Stage '{serializer.data['name']}' - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StgaeDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsManager]

    def get_object(self, pk):
        try:
            return Stage.objects.get(pk=pk)
        except Stage.DoesNotExist:
            return None

    @extend_schema(summary="Bosqichlar tafsilotlari (Detail)", responses={200: StageSerializer}, tags=["Stage"])
    def get(self, request, pk):
        stage = self.get_object(pk=pk)

        if stage is None:
            return Response({"detail": "Bosqich topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StageSerializer(stage)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Bosqichni to'liq yangilash (PUT)", request=StageSerializer, responses={200: StageSerializer}, tags=["Stage"])
    def put(self, request, pk):
        stage = self.get_object(pk)
        if stage is None:
            return Response({"detail": "Bosqich topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StageSerializer(stage, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE-PUT] Stage ID {pk} yangilandi - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Bosqichni o'chirish (DELETE)", responses={204: None}, tags=["Stage"])
    def delete(self, request, pk):
        stage = self.get_object(pk)
        if stage is None:
            return Response({"detail": "Bosqichni topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        stage.delete()
        logger.info(f"[DELETE] Stage ID {pk} o'chirildi - user: {request.user}")
        return Response({"detail": "Bosqich muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)