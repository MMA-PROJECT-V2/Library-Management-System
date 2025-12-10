from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for monitoring."""
    return JsonResponse({
        "status": "healthy",
        "service": "library-notifications-service"
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("notifications.urls")),
    path("health/", health_check, name="health-check"),
    # redirect root to API
    path("", RedirectView.as_view(url="/api/", permanent=False)),
]

# Customize admin site
admin.site.site_header = "Library Notifications Administration"
admin.site.site_title = "Notifications Admin"
admin.site.index_title = "Welcome to Library Notifications Service"