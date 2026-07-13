import django_filters
from crm.models import Company, Stage, Contact, Deal, SourceChoices, StatusChoices
from account.models import User


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    industry = django_filters.CharFilter(lookup_expr='icontains')
    website = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Company
        fields = ['name', 'industry', 'website']


class StageFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    order = django_filters.NumberFilter()  
    order_min = django_filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_max = django_filters.NumberFilter(field_name='order', lookup_expr='lte')

    class Meta:
        model = Stage
        fields = ['name', 'order', 'order_min', 'order_max']



class ContactFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    company = django_filters.ModelChoiceFilter(queryset=Company.objects.all())
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    source = django_filters.ChoiceFilter(choices=SourceChoices.choices)
    status = django_filters.ChoiceFilter(choices=StatusChoices.choices)
    created_at_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Contact
        fields = [
            'full_name', 'phone_number', 'email',
            'company', 'company_name',
            'source', 'status',
        ]


class DealFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all())
    contact_name = django_filters.CharFilter(field_name='contact__full_name', lookup_expr='icontains')
    stage = django_filters.ModelChoiceFilter(queryset=Stage.objects.all())
    manager = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    opened_at_from = django_filters.DateFilter(field_name='opened_at', lookup_expr='gte')
    opened_at_to = django_filters.DateFilter(field_name='opened_at', lookup_expr='lte')
    closed_at_from = django_filters.DateFilter(field_name='closed_at', lookup_expr='gte')
    closed_at_to = django_filters.DateFilter(field_name='closed_at', lookup_expr='lte')
    is_closed = django_filters.BooleanFilter(field_name='closed_at', lookup_expr='isnull', exclude=True)

    class Meta:
        model = Deal
        fields = [
            'name', 'contact', 'contact_name',
            'stage', 'manager',
            'amount_min', 'amount_max',
            'opened_at_from', 'opened_at_to',
            'closed_at_from', 'closed_at_to',
            'is_closed',
        ]