from openpyxl import Workbook
from django.http import HttpResponse


def export_queryset_to_excel(queryset, headers: list[str], row_builder, filename: str, sheet_title: str = "Sheet1") -> HttpResponse:
    """
    queryset    - eksport qilinadigan queryset (filtrlangan)
    headers     - ustun sarlavhalari ro'yxati
    row_builder - har bir obyektni qatorga aylantiruvchi funksiya: obj -> list
    filename    - yuklanadigan fayl nomi
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title
    ws.append(headers)

    for obj in queryset:
        ws.append(row_builder(obj))

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response