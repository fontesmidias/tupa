"""URL root — ADR-009: kebab-PT-BR paths, snake-EN names."""

from django.contrib import admin
from django.urls import include, path

from apps.accounts.urls import root_urlpatterns as accounts_root_urls
from apps.ai_providers.urls import root_urlpatterns as ai_lab_root_urls
from apps.core.views import hello

urlpatterns = [
    path("", hello, name="home"),
    path("admin/", admin.site.urls),
    path("auth/", include("apps.accounts.urls")),
    path("politicas/", include("apps.policies.urls")),
    *accounts_root_urls,
    *ai_lab_root_urls,
]
