from django.contrib import admin
from django.urls import path, include, re_path
from chat.media import serve_media
from django.views.generic import RedirectView
from django.http import HttpResponseForbidden
from django.conf import settings


def disabled_admin_view(request):
    """The built-in Django admin is disabled. Use /chat/admin-panel/ instead."""
    return HttpResponseForbidden(
        "<h2>Django admin is disabled.</h2>"
        "<p>Use <a href='/chat/admin-panel/'>ChatApp Admin Panel</a> instead.</p>"
    )


urlpatterns = [
    # Django's built-in /admin/ is fully disabled — all management lives at /chat/admin-panel/
    path('admin/', disabled_admin_view),
    path('users/', include('users.urls')),
    path('chat/', include('chat.urls')),
    path('', RedirectView.as_view(url='/chat/', permanent=False)),
    # Uploaded files (avatars, pictures, voice notes). Works with DEBUG=False.
    re_path(r'^media/(?P<path>.*)$', serve_media),
]
