"""URL routes for bulk roster upload."""

from django.urls import path

from imports.views import RosterUploadView

urlpatterns = [
    path("imports/roster/", RosterUploadView.as_view(), name="roster-upload"),
]
