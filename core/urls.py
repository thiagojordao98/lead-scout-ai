from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path('admin/', admin.site.urls),
    path("auth/", include("accounts.urls")),
    path("webhooks/", include("plans.urls")),
    path("leads/", include("leads.urls")),
]

if settings.DEBUG and settings.HAS_DEBUG_TOOLBAR:
    urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns

