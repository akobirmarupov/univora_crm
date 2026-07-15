from drf_yasg.inspectors import FilterInspector

class SafeDjangoFilterInspector(FilterInspector):
    def get_filter_parameters(self, view, *args, **kwargs):
        # 1. Agar view'da queryset atributi bo'lmasa, uni xavfsiz None qilib qo'yamiz
        if not hasattr(view, 'queryset'):
            view.queryset = None

        # 2. DjangoFilterBackend orqali filtrlarni xavfsiz tahlil qilish
        try:
            from django_filters.rest_framework import DjangoFilterBackend
            for backend in getattr(view, 'filter_backends', []):
                if issubclass(backend, DjangoFilterBackend):
                    return backend().get_schema_fields(view)
        except Exception:
            pass

        # 3. Agar hech qanday filtr bo'lmasa, bo'sh ro'yxat qaytaramiz
        return []