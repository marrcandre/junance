from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("families/", include("identity.urls")),
    path("ledger/", include("ledger.urls")),
    path("cards/", include("cards.urls")),
    path("imports/", include("imports.urls")),
    path("planning/", include("planning.urls")),
]
