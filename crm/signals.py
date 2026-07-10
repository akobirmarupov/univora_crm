from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from crm.models import Company

@receiver([post_save, post_delete], sender=Company)
def clear_company_cache(sender, instance, **kwargs):
    try:
        cache.incr("company_cache_version")
    except ValueError:
        cache.set("company_cache_version", 1)