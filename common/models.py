from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    created_at = models.DateTimeField('Yaratilgan sana', auto_now_add=True)
    updated_at = models.DateTimeField('Yangilangan sana', auto_now=True)

    class Meta:
        abstract = True



class OwnedModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Ma'sul xodim", on_delete=models.PROTECT,
                             related_name="%(class)s_set",)
    
    class Meta:
        abstract = True



class SourceChoices(models.TextChoices):
    TELEGRAM = "telegram", "Telegram"
    PHONE = "phone", "Telefon qo'ng'irog'i"
    WEBSITE = "website", "Sayt"
    REFERRAL = "referral", "Tavsiya"
    EXHIBITION = "exhibition", "Ko'rgazma"
    OTHER = "other", "Boshqa"
 
 
class ActivityTypeChoices(models.TextChoices):
    CALL = "call", "Qo'ng'iroq"
    MEETING = "meeting", "Uchrashuv"
    EMAIL = "email", "Email"
    MESSAGE = "message", "Xabar (Telegram/WhatsApp)"
    OTHER = "other", "Boshqa"
 
