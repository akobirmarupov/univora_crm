from django.urls import path

from crm.routes.company_stage.views import (
    CompanyListAPIView, CompanyDetailAPIView,
    # StageListAPIView, StageDetailAPIView
)


urlpatterns = [
    path("company/", CompanyListAPIView.as_view(), name="company"),
    path("company/<int:pk>/", CompanyDetailAPIView.as_view(), name="company-detail"),

    # path("stage/", StageListAPIView.as_view(), name="stage-list"),
    # path("stage/<int:pk>/", StageDetailAPIView.as_view(), name="stage-detail")
]