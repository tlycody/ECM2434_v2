from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# Test homepage
def home(request):
    return HttpResponse("Hello, Django is running!")

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('', home),  # Homepage at '/'
    path('api/', include('bingo.urls')),  # Include API routes with 'api/' prefix
]

# Debug Toolbar (Only if settings.DEBUG is True)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)