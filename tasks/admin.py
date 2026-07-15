from __future__ import annotations

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display, action

from tasks.models import Task, Activity


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = (
        'description',
        'contact',
        'deal',
        'assigned_to',
        'due_date',
        'status_badge',
        'deadline_badge',
    )
    list_filter = ('is_done', 'assigned_to', 'due_date')
    search_fields = ('note', 'contact__full_name', 'user__phone_number')
    autocomplete_fields = ('contact', 'deal', 'assigned_to')
    list_select_related = ('contact', 'deal', 'assigned_to')
    date_hierarchy = 'due_date'
    ordering = ('due_date',)
    list_per_page = 25
    list_filter_submit = True
    list_fullwidth = True
    compressed_fields = True

    fieldsets = (
        (_('Asosiy ma\'lumot'), {
            'fields': ('description', 'assigned_to', 'is_done'),
        }),
        (_('Bog\'liq obyektlar'), {
            'fields': ('contact', 'deal'),
            'classes': ('tab',),
        }),
        (_('Muddat'), {
            'fields': ('due_date',),
            'classes': ('tab',),
        }),
    )

    actions = ['mark_as_done', 'mark_as_not_done']

    @display(
        description=_('Holati'),
        label={
            'bajarilgan': 'success',
            'kutilmoqda': 'warning',
        },
    )
    def status_badge(self, obj):
        return 'bajarilgan' if obj.is_done else 'kutilmoqda'

    @display(
        description=_('Muddat holati'),
        label={
            'muddati_otgan': 'danger',
            'vaqtida': 'success',
            'bajarilgan': 'info',
        },
    )
    def deadline_badge(self, obj):
        if obj.is_done:
            return 'bajarilgan'
        if obj.due_date and obj.due_date < timezone.now():
            return 'muddati_otgan'
        return 'vaqtida'

    @action(description=_("Bajarildi deb belgilash"))
    def mark_as_done(self, request, queryset):
        updated = queryset.update(is_done=True)
        self.message_user(request, _(f"{updated} ta vazifa bajarildi deb belgilandi."))

    @action(description=_("Bajarilmadi deb belgilash"))
    def mark_as_not_done(self, request, queryset):
        updated = queryset.update(is_done=False)
        self.message_user(request, _(f"{updated} ta vazifa qayta ochildi."))



@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = ('contact', 'user', 'type_badge', 'note_preview', 'created_at')
    list_filter = ('activity_type', 'user', 'created_at')
    search_fields = ('note', 'contact__name', 'user__email')
    autocomplete_fields = ('contact', 'user')
    list_select_related = ('contact', 'user')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    list_filter_submit = True
    list_fullwidth = True
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Muloqot ma\'lumoti'), {
            'fields': ('contact', 'user', 'activity_type', 'note'),
        }),
        (_('Vaqt belgilari'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )

    @display(
        description=_('Turi'),
        label={
            'call': 'info',
            'meeting': 'warning',
            'email': 'success',
            'note': 'primary',
        },
    )
    def type_badge(self, obj):
        return obj.activity_type

    @display(description=_('Izoh'))
    def note_preview(self, obj):
        if len(obj.note) > 60:
            return f"{obj.note[:60]}..."
        return obj.note