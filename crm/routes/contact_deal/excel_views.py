from common.excel_export import export_queryset_to_excel, read_rows_from_excel, ExcelImportError
from crm.models import Company

from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from crm.models import Contact
from common.permissions import IsEmployee, IsManager, get_visible_queryset

contact_logger = logging.getLogger('contact')


class ContactExportAPIView(APIView):
    parser_classes = [JSONParser]

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    @extend_schema(summary="Kontaktlarni Excel'ga eksport qilish", tags=["Contact"])
    def get(self, request):
        queryset = Contact.objects.select_related("company")
        queryset = get_visible_queryset(request.user, queryset, owner_field="created_by")

        for backend in [DjangoFilterBackend, SearchFilter, OrderingFilter]:
            queryset = backend().filter_queryset(request, queryset, self)

        headers = ["ID", "F.I.O", "Telefon", "Email", "Kompaniya", "Manba", "Status", "Yaratilgan sana"]

        def row_builder(c: Contact) -> list:
            return [
                c.id,
                c.full_name,
                c.phone_number,
                c.email or "",
                c.company.name if c.company else "",
                c.get_source_display(),
                c.get_status_display(),
                c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "",
            ]

        return export_queryset_to_excel(
            queryset=queryset,
            headers=headers,
            row_builder=row_builder,
            filename="kontaktlar.xlsx",
            sheet_title="Kontaktlar",
        )


class ContactImportAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsManager]  # faqat admin/manager import qila oladi

    EXPECTED_HEADERS = ["F.I.O", "Telefon", "Email", "Kompaniya", "Manba"]

    @extend_schema(summary="Kontaktlarni Excel'dan import qilish", tags=["Contact"])
    def post(self, request):
        file = request.FILES.get("file")
        if file is None:
            return Response({"detail": "Fayl yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = list(read_rows_from_excel(file, self.EXPECTED_HEADERS))
        except ExcelImportError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        created, skipped, errors = 0, 0, []

        for row in rows:
            full_name = row.get("F.I.O")
            phone = row.get("Telefon")

            if not full_name or not phone:
                errors.append({"qator": row["_row_number"], "xato": "F.I.O yoki Telefon bo'sh."})
                continue

            phone = str(phone).strip()

            if Contact.objects.filter(phone_number=phone).exists():
                skipped += 1
                continue

            company = None
            company_name = row.get("Kompaniya")
            if company_name:
                company, _ = Company.objects.get_or_create(
                    name=str(company_name).strip(), defaults={"created_by": request.user}
                )

            source_raw = str(row.get("Manba") or "other").strip().lower()
            source = source_raw if source_raw in dict(Contact._meta.get_field("source").choices) else "other"

            Contact.objects.create(
                full_name=str(full_name).strip(),
                phone_number=phone,
                email=(row.get("Email") or None),
                company=company,
                source=source,
                created_by=request.user,
            )
            created += 1

        contact_logger.info(
            f"[IMPORT] user={request.user} created={created} skipped={skipped} errors={len(errors)}"
        )

        return Response(
            {"yaratildi": created, "o'tkazib_yuborildi_dublikat": skipped, "xatolar": errors},
            status=status.HTTP_200_OK,
        )