from django.urls import path

from crm.routes.company_stage.views import (
    CompanyListAPIView, CompanyDetailAPIView,
    StageListAPIView, StgaeDetailAPIView
)
from crm.routes.contact_deal.views import (
    ContactListAPIView, ContactDetailAPIView,
    DealListAPIView, DealDetailAPIView
)
from crm.routes.contact_deal.export_views import ContactExportAPIView, DealExportAPIView


urlpatterns = [
    path("company/", CompanyListAPIView.as_view(), name="company"),
    path("company/<int:pk>/", CompanyDetailAPIView.as_view(), name="company-detail"),

    path("stage/", StageListAPIView.as_view(), name="stage-list"),
    path("stage/<int:pk>/", StgaeDetailAPIView.as_view(), name="stage-detail"),

    path("contact/", ContactListAPIView.as_view(), name="contact-list"),
    path("contact/<int:pk>/", ContactDetailAPIView.as_view(), name="contact-detail"),

    path("deal/", DealListAPIView.as_view(), name="deal-list"),
    path("deal/<int:pk>/", DealDetailAPIView.as_view(), name="deal-detail"),

    path('deals/', DealListAPIView.as_view(), name='deal-list'),
    path('deals/export/', DealExportAPIView.as_view(), name='deal-export'),
]