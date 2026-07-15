from django.urls import path

from crm.routes.company_stage.views import (
    CompanyListAPIView, CompanyDetailAPIView,
    StageListAPIView, StgaeDetailAPIView
)
from crm.routes.contact_deal.views import (
    ContactListAPIView, ContactDetailAPIView,
    DealListAPIView, DealDetailAPIView, DealCloseAPIView
)
from crm.routes.dashboard.views import DashboardAPIView
from crm.routes.contact_deal.excel_views import ContactExportAPIView, ContactImportAPIView


urlpatterns = [
    path("company/", CompanyListAPIView.as_view(), name="company"),
    path("company/<int:pk>/", CompanyDetailAPIView.as_view(), name="company-detail"),

    path("stage/", StageListAPIView.as_view(), name="stage-list"),
    path("stage/<int:pk>/", StgaeDetailAPIView.as_view(), name="stage-detail"),

    path("contact/", ContactListAPIView.as_view(), name="contact-list"),
    path("contact/<int:pk>/", ContactDetailAPIView.as_view(), name="contact-detail"),

    path("deal/", DealListAPIView.as_view(), name="deal-list"),
    path("deal/<int:pk>/", DealDetailAPIView.as_view(), name="deal-detail"),
    path("deal/<int:pk>/close/", DealCloseAPIView.as_view(), name="deal-close"),

    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),

    path("contact/export/", ContactExportAPIView.as_view(), name="contact-export"),
    path("contact/import/", ContactImportAPIView.as_view(), name="contact-import"),

]