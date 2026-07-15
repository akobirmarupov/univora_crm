from django.db import models

from common.models import BaseModel
from account.models import User


class Company(BaseModel):
    name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="companies")
    
    
    class Meta:
        verbose_name = "Kompaniya"
        verbose_name_plural = "Kompaniyalar"

    def __str__(self):
        return self.name


class Stage(BaseModel):
    WON_STAGE_NAME = "Yutildi"
    LOST_STAGE_NAME = "Yo'qotildi"

    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Bosqich"
        verbose_name_plural = "Bosqichlar"
        ordering = ["order"]

    def __str__(self):
        return self.name


class SourceChoices(models.TextChoices):
    WEBSITE = "website", "Veb-sayt"
    TELEGRAM = "telegram", "Telegram"
    REFERRAL = "referral", "Tavsiya"
    CALL = "call", "Qo'ng'iroq"
    OTHER = "other", "Boshqa"


class StatusChoices(models.TextChoices):
    NEW = "new", "Yangi"
    ACTIVE = "active", "Faol"
    INACTIVE = "inactive", "Nofaol"


class Contact(BaseModel):
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts"
    )
    source = models.CharField(max_length=20, choices=SourceChoices.choices, default=SourceChoices.OTHER)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NEW)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts"
    )
    
    class Meta:
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontaktlar"

    def __str__(self):
        return self.full_name


class Deal(BaseModel):
    name = models.CharField(max_length=150)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="deals")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stage = models.ForeignKey(Stage, on_delete=models.PROTECT, related_name="deals")
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    opened_at = models.DateField(auto_now_add=True)
    closed_at = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Bitim"
        verbose_name_plural = "Bitimlar"

    def __str__(self):
        return self.name

    @property
    def is_won(self):
        return self.closed_at is not None and self.stage.name == Stage.WON_STAGE_NAME

    @property
    def is_lost(self):
        return self.closed_at is not None and self.stage.name == Stage.LOST_STAGE_NAME