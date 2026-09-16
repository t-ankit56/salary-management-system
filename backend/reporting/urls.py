from django.urls import path

from reporting.views import ReportView

urlpatterns = [
    path("reports/<str:name>/", ReportView.as_view(), name="report"),
]
