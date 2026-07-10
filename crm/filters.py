import django_filters
from crm.models import Company, Stage


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