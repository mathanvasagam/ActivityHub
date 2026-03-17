from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from searcher.views import landing_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing_view, name="home"),
    path("accounts/", include("accounts.urls")),
    path("oauth/", include("allauth.urls")),
    path("search/", include("searcher.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
