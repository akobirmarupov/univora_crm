from rest_framework.views import APIView
from rest_framework import status

from common.permissions import IsManager, IsEmployee
from common.excel_export import export_queryset_to_excel
from crm.filters import ContactFilter, DealFilter
from crm.models import Contact, Deal


class ContactExportAPIView(APIView):

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    def get_queryset(self):
        user = self.request.user
        qs = Contact.objects.select_related('company')
        if user.is_superuser:
            return qs
        if user.role == 'manager':
            team_ids = user.team_members.values_list('id', flat=True)
            return qs.filter(user_id__in=[*team_ids, user.id])
        return qs.filter(user=user)

    def get(self, request):
        qs = ContactFilter(request.GET, queryset=self.get_queryset()).qs

        return export_queryset_to_excel(
            queryset=qs,
            headers=['ID', "To'liq ism", 'Telefon', 'Email', 'Kompaniya', 'Status', 'Yaratilgan sana'],
            row_builder=lambda c: [
                c.id, c.full_name, c.phone_number, c.email,
                c.company.name if c.company else '',
                c.get_status_display(),
                c.created_at.strftime('%Y-%m-%d'),
            ],
            filename='contacts_export.xlsx',
            sheet_title='Contacts',
        )


class DealExportAPIView(APIView):

    def get_permissions(self):
        return [(IsManager | IsEmployee)()]

    def get_queryset(self):
        user = self.request.user
        qs = Deal.objects.select_related('contact', 'user')
        if user.is_superuser:
            return qs
        if user.role == 'manager':
            team_ids = user.team_members.values_list('id', flat=True)
            return qs.filter(user_id__in=[*team_ids, user.id])
        return qs.filter(user=user)

    def get(self, request):
        qs = DealFilter(request.GET, queryset=self.get_queryset()).qs

        return export_queryset_to_excel(
            queryset=qs,
            headers=['ID', 'Nomi', 'Kontakt', 'Summasi', 'Bosqich', 'Menejer', 'Sana'],
            row_builder=lambda d: [
                d.id, d.name, d.contact.full_name if d.contact else '',
                d.amount, d.get_stage_display(),
                d.user.get_full_name() or d.user.username,
                d.created_at.strftime('%Y-%m-%d'),
            ],
            filename='deals_export.xlsx',
            sheet_title='Deals',
        )