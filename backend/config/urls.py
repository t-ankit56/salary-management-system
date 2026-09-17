"""Root URL configuration: mounts the admin site and each app's API routes under /api/."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("employees.urls")),
    path("api/", include("salary.urls")),
    path("api/", include("reporting.urls")),
    path("api/", include("imports.urls")),
]
