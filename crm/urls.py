from django.urls import path

from crm.routes.company_stage.views import CompanyListAPIView, CompanyDetailAPIView


urlpatterns = [
    path("company/", CompanyListAPIView.as_view(), name="company"),
    path("company/<int:pk>/", CompanyDetailAPIView.as_view(), name="company-detail")
]