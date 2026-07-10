from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import Company, Contact, Stage, Deal


class ContactInline(TabularInline):
    model = Contact
    extra = 0
    fields = ("full_name", "phone_number", "email", "status")
    show_change_link = True
    verbose_name = "Kontakt"
    verbose_name_plural = "Kontaktlar"


class DealInline(TabularInline):
    model = Deal
    extra = 0
    fields = ("name", "amount", "stage", "manager", "closed_at")
    show_change_link = True
    verbose_name = "Bitim"
    verbose_name_plural = "Bitimlar"


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ("id", "name", "industry", "website")
    list_filter = ("industry",)
    search_fields = ("name", "industry", "website")
    ordering = ("name",)

    inlines = [ContactInline]

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("name", "industry"),
            },
        ),
        (
            _("Aloqa ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("website", "address"),
            },
        ),
    )


@admin.register(Stage)
class StageAdmin(ModelAdmin):
    list_display = ("id", "name", "order")
    ordering = ("order",)
    search_fields = ("name",)


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "email",
        "company",
        "source",
        "status",
    )
    list_filter = ("status", "source", "company")
    search_fields = ("full_name", "phone_number", "email")
    ordering = ("full_name",)

    inlines = [DealInline]

    fieldsets = (
        (
            _("Shaxsiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("full_name", "phone_number", "email"),
            },
        ),
        (
            _("Kompaniya va manba"),
            {
                "classes": ["tab"],
                "fields": ("company", "source", "status"),
            },
        ),
    )

@admin.register(Deal)
class DealAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "contact",
        "amount",
        "stage",
        "manager",
        "opened_at",
        "closed_at",
    )
    list_filter = ("stage", "manager")
    search_fields = ("name", "contact__full_name")
    ordering = ("-opened_at",)

    readonly_fields = ("opened_at",)   # <- qo'shildi

    fieldsets = (
        (
            _("Bitim ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("name", "contact", "amount"),
            },
        ),
        (
            _("Pipeline"),
            {
                "classes": ["tab"],
                "fields": ("stage", "manager"),
            },
        ),
        (
            _("Sanalar"),
            {
                "classes": ["tab"],
                "fields": ("opened_at", "closed_at"),
            },
        ),
    )