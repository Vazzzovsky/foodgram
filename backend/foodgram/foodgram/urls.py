from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from .settings import ON_PROD


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if not ON_PROD:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
