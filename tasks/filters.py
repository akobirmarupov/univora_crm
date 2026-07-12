from __future__ import annotations

import django_filters
from django.utils import timezone

from tasks.models import Task, Activity


class TaskFilter(django_filters.FilterSet):
    contact = django_filters.NumberFilter(field_name='contact')
    deal = django_filters.NumberFilter(field_name='deal')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to')
    is_done = django_filters.BooleanFilter(field_name='is_done')
    due_date_from = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')

    class Meta:
        model = Task
        fields = ['contact', 'deal', 'assigned_to', 'is_done']

    def filter_overdue(self, queryset, name, value):
        now = timezone.now()
        if value:
            return queryset.filter(due_date__lt=now, is_done=False)
        return queryset.exclude(due_date__lt=now, is_done=False)


class ActivityFilter(django_filters.FilterSet):
    contact = django_filters.NumberFilter(field_name='contact')
    user = django_filters.NumberFilter(field_name='user')
    activity_type = django_filters.ChoiceFilter(field_name='activity_type',choices=Activity.TYPE_CHOICES,)
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Activity
        fields = ['contact', 'user', 'activity_type']